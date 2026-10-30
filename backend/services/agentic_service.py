import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from controllers.crop_controller import get_crop
from services.rag_service import retrieve_knowledge

load_dotenv()

logger = logging.getLogger(__name__)


class AdvisoryState(TypedDict, total=False):
    farmer_input: dict
    recommendation: dict
    risk_flagged: bool
    risk_level: str
    risk_flags: list[str]
    knowledge: list[str]
    advisory_text: str


def predict_crop(state: AdvisoryState) -> dict:
    """Call the existing recommendation flow without duplicating ML logic."""
    return {"recommendation": get_crop(state["farmer_input"])}


def check_risk(state: AdvisoryState) -> dict:
    recommendation = state["recommendation"]
    farmer_input = state["farmer_input"]
    flags = []

    top_3 = recommendation.get("top_3", [])
    confidence = top_3[0].get("confidence", 0) if top_3 else 0
    if confidence < 0.60:
        flags.append(f"final crop confidence is low ({confidence:.3f})")

    weather = recommendation.get("weather", {})
    temperature = weather.get("temperature", farmer_input.get("temperature"))
    humidity = weather.get("humidity", farmer_input.get("humidity"))
    ml_input = recommendation.get("ml_input") or {}
    rainfall = ml_input.get("rainfall")
    if rainfall is None:
        rainfall = weather.get("seasonal_rainfall_mm", farmer_input.get("rainfall"))

    proximity = recommendation.get("proximity") or {}
    if proximity.get("proximity_level") == "distant":
        flags.append(proximity.get("note") or "the selected place is far from the nearest known profile")
    soil_info = recommendation.get("soil_info") or {}
    if soil_info.get("soil_source") not in (None, "farmer"):
        flags.append("soil N, P, K, and pH are estimates from the nearest district profile, not a soil test for this field")

    if temperature is not None and (temperature < 5 or temperature > 40):
        flags.append(f"temperature is extreme ({temperature} C)")
    if humidity is not None and (humidity < 20 or humidity > 90):
        flags.append(f"humidity is extreme ({humidity}%)")
    if rainfall is not None and (rainfall < 20 or rainfall > 300):
        flags.append(f"rainfall is outside the working range ({rainfall} mm)")

    ph = farmer_input.get("ph")
    if ph is not None and (ph < 5.5 or ph > 8.5):
        flags.append(f"soil pH needs attention ({ph})")

    nutrient_limits = {"N": 20, "P": 10, "K": 20}
    for nutrient, limit in nutrient_limits.items():
        value = farmer_input.get(nutrient)
        if value is not None and value < limit:
            flags.append(f"{nutrient} level is low ({value})")

    if not recommendation.get("success"):
        flags.append("the existing crop recommendation did not succeed")

    return {
        "risk_flagged": bool(flags),
        "risk_level": "high" if len(flags) >= 2 else "moderate" if flags else "low",
        "risk_flags": flags,
    }


def retrieve_for_recommendation(state: AdvisoryState) -> dict:
    recommendation = state["recommendation"]
    if not recommendation.get("success") or not recommendation.get("recommended_crop"):
        return {"knowledge": []}

    farmer_input = state["farmer_input"]
    npk = {key: farmer_input.get(key, "unknown") for key in ("N", "P", "K")}
    query_context = json.dumps(
        {
            "risk_flags": state.get("risk_flags", []),
            "soil": farmer_input.get("soil"),
            "ph": farmer_input.get("ph"),
            "weather": recommendation.get("weather", {}),
        },
        default=str,
    )
    return {
        "knowledge": retrieve_knowledge(
            recommendation["recommended_crop"], npk, query_context
        )
    }


def _language_name(farmer_input: dict) -> str:
    code = str((farmer_input or {}).get("language") or "en").lower()
    if code.startswith("hi"):
        return "Hindi, using Devanagari script"
    return "English"


def _card_brief(recommendation: dict) -> str:
    lines = []
    for card in recommendation.get("crop_cards") or []:
        price = card.get("msp_inr_per_quintal")
        price_text = (
            f"indicative MSP reference Rs {price}/quintal ({card.get('msp_note')})"
            if price
            else card.get("msp_note")
        )
        lines.append(
            f"{card.get('crop')}: yield {card.get('yield_low')}-{card.get('yield_high')} {card.get('yield_unit')}; "
            f"season {card.get('season')}; states {', '.join(card.get('states') or [])}; "
            f"challenges {'; '.join(card.get('challenges') or [])}; price: {price_text}. "
            f"{card.get('price_disclaimer')}"
        )
    return "\n".join(lines) or "No crop reference card was attached."


def _fallback_advisory(recommendation: dict, language: str) -> str:
    crop = recommendation.get("recommended_crop", "a crop")
    proximity = (recommendation.get("proximity") or {}).get("note", "")
    if language.startswith("Hindi"):
        return (
            f"सुझावित फसल {crop} है. {proximity} "
            "यह अपने आप बना सारांश है क्योंकि भाषा मॉडल अभी उपलब्ध नहीं है. "
            "बुवाई से पहले मिट्टी जाँच और स्थानीय विशेषज्ञ से पुष्टि करें."
        )
    return (
        f"The suggested crop is {crop}. {proximity} "
        "This is an automatic summary because the language model is unavailable. "
        "Confirm the soil test and the local market before sowing."
    )


def _invoke_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    from langchain_groq import ChatGroq

    response = ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=api_key,
        temperature=0.4,
        max_tokens=900,
        reasoning_effort="low",
    ).invoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = " ".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        )
    return str(content).strip()


def _generate_llm_advisory(state: AdvisoryState, include_warning: bool) -> dict:
    recommendation = state["recommendation"]
    farmer_input = state["farmer_input"]
    language = _language_name(farmer_input)
    if not recommendation.get("success") or not recommendation.get("recommended_crop"):
        return {
            "advisory_text": (
                recommendation.get("message")
                or "A crop recommendation could not be completed. Please check the location, weather, and soil inputs."
            )
        }

    risk_section = "No risk warning was raised."
    if include_warning:
        risk_section = "Risk warning ({level}):\n{flags}".format(
            level=state.get("risk_level", "moderate"),
            flags="\n".join(f"- {flag}" for flag in state.get("risk_flags", [])),
        )

    prompt = f"""You are an agricultural advisor. Write the entire answer in {language}.
Write a practical advisory of no more than 220 words. Vary the wording to match this farmer's place, soil source, and weather. Do not reuse a fixed template.
Cover: the recommended crop and what the confidence means; whether this is a field-specific result or the nearest known trend; what to sow and the yield range from the crop card; challenges; fertilizer and irrigation notes grounded only in the retrieved documents; and the price note exactly as a reference, never as today's mandi rate.
Do not invent fertilizer rates, diagnoses, or prices. If soil values are estimates, say so. Remind the farmer to confirm rates with a soil test or a local expert.

Farmer input:
{json.dumps(farmer_input, indent=2, default=str)}

Recommendation summary:
recommended_crop={recommendation.get("recommended_crop")}
advisory_basis={recommendation.get("advisory_basis")}
proximity={json.dumps(recommendation.get("proximity"), default=str)}
soil={json.dumps(recommendation.get("soil_info"), default=str)}
weather={json.dumps({k: recommendation.get("weather", {}).get(k) for k in ("city", "temperature", "humidity", "condition", "forecast_rain_5d_mm", "seasonal_rainfall_mm", "rainfall_note")}, default=str)}
top_3={json.dumps(recommendation.get("top_3"), default=str)}
nearby_crops={json.dumps(recommendation.get("nearby_crops"), default=str)}
fertilizer={json.dumps(recommendation.get("fertilizer"), default=str)}

Crop reference cards:
{_card_brief(recommendation)}

{risk_section}

Retrieved agronomy documents:
{chr(10).join(state.get("knowledge", [])) or "No documents were retrieved."}
"""
    try:
        return {"advisory_text": _invoke_groq(prompt)}
    except Exception as error:
        logger.error("Advisory generation failed", extra={"event": "llm_error", "error": str(error)})
        return {"advisory_text": _fallback_advisory(recommendation, language)}


def synthesize_advisory(state: AdvisoryState) -> dict:
    return _generate_llm_advisory(state, include_warning=True)


def synthesize_without_warning(state: AdvisoryState) -> dict:
    return _generate_llm_advisory(state, include_warning=False)


def _risk_route(state: AdvisoryState) -> str:
    return "with_warning" if state.get("risk_flagged") else "without_warning"


def _build_graph():
    graph = StateGraph(AdvisoryState)
    graph.add_node("predict_crop", predict_crop)
    graph.add_node("check_risk", check_risk)
    graph.add_node("retrieve_knowledge", retrieve_for_recommendation)
    graph.add_node("synthesize_advisory", synthesize_advisory)
    graph.add_node("synthesize_without_warning", synthesize_without_warning)
    graph.add_edge(START, "predict_crop")
    graph.add_edge("predict_crop", "check_risk")
    graph.add_edge("check_risk", "retrieve_knowledge")
    graph.add_conditional_edges(
        "retrieve_knowledge",
        _risk_route,
        {
            "with_warning": "synthesize_advisory",
            "without_warning": "synthesize_without_warning",
        },
    )
    graph.add_edge("synthesize_advisory", END)
    graph.add_edge("synthesize_without_warning", END)
    return graph.compile()


_advisory_graph = _build_graph()


def answer_farmer_question(question: str, language: str = "en", context: dict | None = None) -> dict:
    """Answer a follow-up from retrieved notes and the current recommendation. Does not rerun the crop model."""
    question = (question or "").strip()
    if not question:
        return {"success": False, "message": "A question is required"}

    context = context or {}
    crop = context.get("recommended_crop") or "crop"
    npk = context.get("npk") or {}
    try:
        knowledge = retrieve_knowledge(crop, npk, question)
    except Exception as error:
        logger.error("Question retrieval failed", extra={"event": "rag_error", "error": str(error)})
        knowledge = []

    language_name = _language_name({"language": language})
    prompt = f"""You are an agricultural advisor. Answer in {language_name}.
The farmer asked a follow-up. Answer in at most 160 words. Use the retrieved documents and the recommendation context. If the documents do not support a claim, say what is unknown. Do not invent fertilizer rates, disease names, or market prices. This is decision support alongside local knowledge, not a replacement for it.

Question:
{question}

Recommendation context:
{json.dumps(context, indent=2, default=str)}

Retrieved agronomy documents:
{chr(10).join(knowledge) or "No documents were retrieved."}
"""
    try:
        answer = _invoke_groq(prompt)
    except Exception as error:
        logger.error("Question answering failed", extra={"event": "llm_error", "error": str(error)})
        answer = (
            "The language model could not answer just now. Use the retrieved notes below and confirm with a local expert."
            if not language_name.startswith("Hindi")
            else "भाषा मॉडल अभी उत्तर नहीं दे सका. नीचे दिए नोट देखें और स्थानीय विशेषज्ञ से पुष्टि करें."
        )
    return {"success": True, "answer": answer, "knowledge": knowledge}


def run_advisory_pipeline(farmer_input: dict) -> dict:
    """Run prediction, risk checks, RAG retrieval, and LLM synthesis."""
    result = _advisory_graph.invoke({"farmer_input": farmer_input})
    return {
        **result["recommendation"],
        "risk_flagged": result.get("risk_flagged", False),
        "risk_level": result.get("risk_level", "low"),
        "risk_flags": result.get("risk_flags", []),
        "knowledge": result.get("knowledge", []),
        "advisory_text": result.get("advisory_text", ""),
    }


def _pdf_text(value) -> str:
    text = "" if value is None else str(value)
    text = text.replace("**", "")
    replacements = {
        "\u20b9": "Rs ",
        "\u2014": "-",
        "\u2013": "-",
        "\u2011": "-",
        "\u2010": "-",
        "\u202f": " ",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def export_advisory_pdf(advisory_text: str, payload: dict) -> str:
    """Write a farmer advisory PDF and return its absolute path."""
    from fpdf import FPDF

    output_dir = Path(__file__).resolve().parents[1] / "generated_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now().timestamp() - 2 * 24 * 3600
    for old in output_dir.glob("advisory_*.pdf"):
        try:
            if old.stat().st_mtime < cutoff:
                old.unlink()
        except OSError:
            pass

    file_name = f"advisory_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.pdf"
    output_path = output_dir / file_name
    font_dir = Path(__file__).resolve().parents[1] / "assets" / "fonts"
    hindi = any("\u0900" <= char <= "\u097f" for char in advisory_text or "")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # DejaVu covers the English page chrome. Noto is used only for Devanagari
    # advisory text, because that font does not include Latin letters.
    pdf.add_font("Body", "", str(font_dir / "DejaVuSans.ttf"))
    pdf.add_font("Body", "B", str(font_dir / "DejaVuSans-Bold.ttf"))
    if hindi:
        pdf.add_font("Hindi", "", str(font_dir / "NotoSansDevanagari-Regular.ttf"))

    def heading(text, size=14):
        pdf.set_font("Body", "B", size)
        pdf.multi_cell(0, 8, _pdf_text(text))
        pdf.ln(1)

    def body(text):
        pdf.set_font("Body", "", 11)
        pdf.multi_cell(0, 6, _pdf_text(text))
        pdf.ln(2)

    place = payload.get("resolved_place") or {}
    soil = payload.get("soil_info") or {}
    weather = payload.get("weather") or {}
    proximity = payload.get("proximity") or {}
    crop = payload.get("recommended_crop") or "Not provided"
    cards = payload.get("crop_cards") or []
    top_card = next((card for card in cards if card.get("crop") == str(crop).lower()), cards[0] if cards else {})

    heading("KRISHI AI Advisory Report", 16)
    body("Decision-support note. Confirm soil rates and the local market before sowing or buying inputs.")
    heading("Recommendation", 13)
    body(
        f"Crop: {crop}\n"
        f"Place: {place.get('name') or payload.get('user_selected_location') or payload.get('location')}"
        f", {place.get('state') or ''}\n"
        f"Nearest profile: {proximity.get('district')}, {proximity.get('state')} "
        f"({proximity.get('distance_km')} km, {proximity.get('proximity_level')})\n"
        f"Basis: {payload.get('advisory_basis')}\n"
        f"{proximity.get('note') or ''}"
    )
    heading("Soil and weather used", 13)
    body(
        f"Soil source: {soil.get('soil_source')}. Type: {soil.get('soil_type')}. "
        f"N {soil.get('N')}, P {soil.get('P')}, K {soil.get('K')}, pH {soil.get('ph')}.\n"
        f"Temperature {weather.get('temperature')} C, humidity {weather.get('humidity')}%, "
        f"{weather.get('condition')}.\n"
        f"Forecast rain, next 5 days: {weather.get('forecast_rain_5d_mm')} mm. "
        f"Seasonal proxy used by the model: {weather.get('seasonal_rainfall_mm')} mm. "
        f"{weather.get('rainfall_note') or ''}"
    )
    if top_card:
        heading("Yield, challenges, and price reference", 13)
        price = top_card.get("msp_inr_per_quintal")
        price_line = (
            f"Indicative MSP reference: Rs {price} per quintal. {top_card.get('msp_note')}"
            if price
            else str(top_card.get("msp_note"))
        )
        body(
            f"Yield range: {top_card.get('yield_low')} to {top_card.get('yield_high')} {top_card.get('yield_unit')}. "
            f"Season: {top_card.get('season')}.\n"
            f"States where this crop is commonly grown: {', '.join(top_card.get('states') or [])}.\n"
            f"Challenges: {'; '.join(top_card.get('challenges') or [])}.\n"
            f"{price_line}\n{top_card.get('price_disclaimer')}"
        )
    heading("Advisory", 13)
    if hindi:
        pdf.set_font("Hindi", "", 12)
        pdf.set_fallback_fonts(["Body"])
        pdf.multi_cell(0, 7, _pdf_text(advisory_text or "No advisory text was produced."))
    else:
        body(advisory_text or "No advisory text was produced.")
    pdf.output(str(output_path))
    return str(output_path)