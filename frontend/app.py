import sys
import time
from pathlib import Path

import folium
import plotly.graph_objects as go
import streamlit as st
from folium.plugins import Fullscreen, MiniMap, MousePosition
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.api import ApiError, get, post, post_bytes
from ui.bridge import browser_bridge
from ui.i18n import translate
from ui.theme import CSS

st.set_page_config(page_title="KRISHI AI", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

SOIL_TYPES = ["Loamy", "Sandy", "Clay", "Silty", "Peaty"]
MODEL_CROPS = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans", "mungbean",
    "blackgram", "lentil", "pomegranate", "banana", "mango", "grapes", "watermelon",
    "muskmelon", "apple", "orange", "papaya", "coconut", "cotton", "jute", "coffee",
]


def init_state():
    defaults = {
        "token": None,
        "username": "",
        "language": "en",
        "place": None,
        "use_own_soil": False,
        "N": 40,
        "P": 18,
        "K": 80,
        "ph": 6.8,
        "soil": "Loamy",
        "last_result": None,
        "last_payload": None,
        "audio": None,
        "answer": None,
        "geo_key": None,
        "map_click": None,
        "bridge_sig": "",
        "place_error": "",
        "announce": "",
        "announce_id": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    pending = st.session_state.pop("pending_soil", None)
    if pending and not st.session_state.use_own_soil:
        for field in ("N", "P", "K", "ph", "soil"):
            st.session_state[field] = pending[field]


def t(key):
    return translate(st.session_state.language, key)


def apply_place(payload):
    nearest = payload.get("nearest") or {}
    soil_name = nearest.get("soil") or "Loamy"
    if soil_name not in SOIL_TYPES:
        soil_name = "Loamy"
    st.session_state.place = payload
    st.session_state.pending_soil = {
        "N": int(nearest.get("N") or 40),
        "P": int(nearest.get("P") or 18),
        "K": min(150, int(nearest.get("K") or 40)),
        "ph": float(nearest.get("ph") or 6.5),
        "soil": soil_name,
    }
    st.session_state.last_result = None
    st.session_state.answer = None
    st.session_state.place_error = ""
    st.session_state.announce = place_sentence(payload)
    st.session_state.announce_id = str(time.time())
    st.rerun()


def clean_place_phrase(text):
    cleaned = " ".join((text or "").split())
    lowered = cleaned.lower()
    prefixes = (
        "i am in ", "i'm in ", "i live in ", "my village is ", "my place is ",
        "the place is ", "place is ", "we are in ", "this is ", "near ", "around ",
        "mera gaon ", "mera gram ", "gaon ",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            lowered = cleaned.lower()
    return cleaned.strip(" .,")


def place_sentence(payload):
    point = payload.get("place") or {}
    nearest = payload.get("nearest") or {}
    weather = payload.get("weather") or {}
    name = point.get("name") or "the selected place"
    district = nearest.get("district") or "the nearest profile"
    distance = nearest.get("distance_km")
    temp = weather.get("temperature")
    if st.session_state.language == "hi":
        return (
            f"{name} चुन लिया गया है. सबसे नजदीकी प्रोफाइल {district} है, "
            f"लगभग {distance} किलोमीटर. इस पिन पर तापमान {temp} डिग्री है."
        )
    return (
        f"Place set to {name}. The nearest profile is {district}, about {distance} kilometers away. "
        f"Weather at this pin is {temp} degrees."
    )


def handle_bridge(event):
    if not isinstance(event, dict):
        return
    signature = f"{event.get('kind')}:{event.get('at')}"
    if not event.get("kind") or signature == st.session_state.get("bridge_sig"):
        return
    st.session_state.bridge_sig = signature
    kind = event.get("kind")
    try:
        if kind == "restore" and not st.session_state.token and event.get("token"):
            st.session_state.token = event["token"]
            st.session_state.username = event.get("username") or ""
            st.rerun()
        elif kind == "speech" and event.get("text"):
            phrase = clean_place_phrase(event["text"])
            if phrase:
                st.session_state.heard_place = phrase
                apply_place(resolve_query(phrase))
            else:
                st.session_state.place_error = "No place name was heard. Try again or type it."
                st.rerun()
        elif kind == "geo" and event.get("lat") is not None:
            apply_place(resolve_point(event["lat"], event["lon"]))
        elif kind in ("speech_error", "geo_error"):
            st.session_state.place_error = event.get("message") or "That action did not complete."
            st.rerun()
    except (ApiError, Exception) as error:
        st.session_state.place_error = str(error)
        st.rerun()


def resolve_query(query):
    return get("/api/location/resolve", token=st.session_state.token, params={"q": query}, timeout=30)


def resolve_point(lat, lon):
    return get(
        "/api/location/resolve",
        token=st.session_state.token,
        params={"lat": lat, "lon": lon},
        timeout=30,
    )


def listen_for_phrase():
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=6, phrase_time_limit=6)
    language = "hi-IN" if st.session_state.language == "hi" else "en-IN"
    return recognizer.recognize_google(audio, language=language)


def farmer_payload():
    place = st.session_state.place or {}
    point = place.get("place") or {}
    nearest = place.get("nearest") or {}
    name = point.get("name") or nearest.get("district") or "Selected place"
    edited = st.session_state.use_own_soil
    for field, places in (("N", 0), ("P", 0), ("K", 0), ("ph", 1)):
        try:
            current = round(float(st.session_state[field]), places)
            profile = round(float(nearest.get(field)), places)
            if current != profile:
                edited = True
        except (TypeError, ValueError):
            edited = True
    return {
        "location": name,
        "latitude": point.get("lat"),
        "longitude": point.get("lon"),
        "soil": st.session_state.soil,
        "soil_source": "farmer" if edited else "estimate",
        "N": int(st.session_state.N),
        "P": int(st.session_state.P),
        "K": int(st.session_state.K),
        "ph": float(st.session_state.ph),
        "language": st.session_state.language,
    }


def dark_chart(figure):
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e7f3ea",
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
    )
    return figure


def render_auth():
    st.markdown(
        f"<div class='hero'><h1>{t('title')}</h1><p>{t('subtitle')}</p></div>",
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown(
            "<div class='glass'>"
            "<p class='metric-label'>What this desk does</p>"
            "<p>Pick any place, read live weather, compare it with the nearest district profile, "
            "and receive a written advisory with a PDF. Soil numbers from a test replace the estimate.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with right:
        st.subheader(t("login_title"))
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")
        sign_col, login_col = st.columns(2)
        with sign_col:
            if st.button(t("signup"), use_container_width=True):
                try:
                    result = post("/api/auth/signup", {"username": username, "password": password})
                    if result.get("success"):
                        st.success(result.get("message", "Account created"))
                    else:
                        st.error(result.get("message", "Could not create the account"))
                except (ApiError, Exception) as error:
                    st.error(str(error))
        with login_col:
            if st.button(t("login"), use_container_width=True):
                try:
                    result = post("/api/auth/login", {"username": username, "password": password})
                    if result.get("success") and result.get("token"):
                        st.session_state.token = result["token"]
                        st.session_state.username = username
                        st.session_state.clear_session = False
                        st.rerun()
                    st.error(result.get("message", "Login failed"))
                except (ApiError, Exception) as error:
                    st.error(str(error))


def render_sidebar():
    st.sidebar.markdown(f"### {t('settings')}")
    language = st.sidebar.selectbox(
        t("language"),
        options=["en", "hi"],
        format_func=lambda code: "English" if code == "en" else "हिन्दी",
        index=0 if st.session_state.language == "en" else 1,
    )
    st.session_state.language = language
    st.sidebar.caption(f"{t('connected')}: 127.0.0.1:5001")
    st.sidebar.caption(st.session_state.username)
    if st.sidebar.button(t("logout")):
        for key in ("token", "username", "place", "last_result", "last_payload", "audio", "answer", "announce"):
            st.session_state[key] = None if key != "username" else ""
        st.session_state.username = ""
        st.session_state.clear_session = True
        st.rerun()


def consume_device_location():
    params = st.query_params
    if "lat" not in params or "lon" not in params:
        return
    key = (str(params["lat"]), str(params["lon"]))
    if st.session_state.geo_key == key:
        return
    st.session_state.geo_key = key
    try:
        apply_place(resolve_point(params["lat"], params["lon"]))
    except (ApiError, Exception) as error:
        st.error(str(error))


def build_map(payload):
    point = (payload or {}).get("place") or {}
    nearest = (payload or {}).get("nearest") or {}
    weather = (payload or {}).get("weather") or {}
    has_point = point.get("lat") is not None and point.get("lon") is not None
    center = [point.get("lat") or 22.5, point.get("lon") or 79.0]
    fmap = folium.Map(location=center, zoom_start=8 if has_point else 5, tiles=None, control_scale=True)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="CARTO",
        name="Dark",
    ).add_to(fmap)
    folium.TileLayer("OpenStreetMap", name="Streets").add_to(fmap)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
    ).add_to(fmap)
    if has_point:
        popup = (
            f"<b>{point.get('name') or 'Selected pin'}</b><br>"
            f"{point.get('state') or ''}<br>"
            f"{point.get('lat'):.4f}, {point.get('lon'):.4f}<br>"
            f"{weather.get('temperature', '')} C, {weather.get('condition', '')}"
        )
        folium.CircleMarker(
            [point["lat"], point["lon"]],
            radius=10,
            color="#e4c56a",
            weight=3,
            fill=True,
            fill_color="#1f8f55",
            fill_opacity=0.95,
            tooltip=point.get("name") or "Selected pin",
            popup=folium.Popup(popup, max_width=260),
        ).add_to(fmap)
        if nearest.get("latitude") is not None:
            folium.CircleMarker(
                [nearest["latitude"], nearest["longitude"]],
                radius=8,
                color="#e4c56a",
                weight=2,
                fill=True,
                fill_color="#8a6a22",
                fill_opacity=0.9,
                tooltip=f"Nearest profile: {nearest.get('district')}",
                popup=f"{nearest.get('district')}, {nearest.get('state')}<br>{nearest.get('distance_km')} km",
            ).add_to(fmap)
            folium.PolyLine(
                [[point["lat"], point["lon"]], [nearest["latitude"], nearest["longitude"]]],
                color="#e4c56a",
                weight=2,
                opacity=0.8,
                dash_array="6 8",
            ).add_to(fmap)
            if nearest.get("distance_km") and float(nearest["distance_km"]) <= 250:
                folium.Circle(
                    [point["lat"], point["lon"]],
                    radius=float(nearest["distance_km"]) * 1000,
                    color="#8ee0a8",
                    weight=1,
                    fill=False,
                    opacity=0.35,
                ).add_to(fmap)
    Fullscreen().add_to(fmap)
    MiniMap(toggle_display=True, position="bottomleft").add_to(fmap)
    MousePosition(position="bottomright", separator=" | ", prefix="Lat/Lon:").add_to(fmap)
    folium.LayerControl(collapsed=False).add_to(fmap)
    return fmap


def render_place_tab():
    st.caption(t("map_help"))
    heard = st.session_state.pop("heard_place", None)
    if heard:
        st.session_state.place_query = heard
    with st.form("find_place", clear_on_submit=False):
        search_col, button_col = st.columns([4, 1], vertical_alignment="bottom")
        with search_col:
            query = st.text_input(t("search_label"), key="place_query")
        with button_col:
            submitted = st.form_submit_button(t("search_button"), use_container_width=True)
    if submitted:
        phrase = clean_place_phrase(query)
        if phrase:
            try:
                apply_place(resolve_query(phrase))
            except (ApiError, Exception) as error:
                st.error(str(error))
        else:
            st.warning("Type a village, town, or district first.")

    place_event = browser_bridge(
        role="place",
        language=st.session_state.language,
        show_tools=True,
        announce=st.session_state.get("announce") or "",
        announce_id=st.session_state.get("announce_id") or "",
        speak_label=t("voice_button"),
        geo_label=t("geo_button"),
        key="krishi_place_bridge",
    )
    handle_bridge(place_event)
    if st.session_state.place_error:
        st.warning(st.session_state.place_error)

    if not st.session_state.place:
        st.info(t("place_waiting"))
    else:
        render_place_summary()
        alternatives = st.session_state.place.get("alternatives") or []
        if len(alternatives) > 1:
            labels = [
                f"{item.get('name')} ({item.get('state') or item.get('country') or 'match'})"
                for item in alternatives
            ]
            picked = st.selectbox("Other matches for that name", labels, key="place_alt")
            if st.button("Use this match"):
                chosen = alternatives[labels.index(picked)]
                try:
                    apply_place(resolve_point(chosen["lat"], chosen["lon"]))
                except (ApiError, Exception) as error:
                    st.error(str(error))

    point = (st.session_state.place or {}).get("place") or {}
    map_key = "krishi-map"
    if point.get("lat") is not None:
        map_key = f"krishi-map-{round(float(point['lat']), 3)}-{round(float(point['lon']), 3)}"
    clicked = st_folium(
        build_map(st.session_state.place),
        height=520,
        use_container_width=True,
        returned_objects=["last_clicked"],
        key=map_key,
    )
    st.caption("Green pin: your place and its weather. Gold pin: nearest soil profile. Dashed line: the distance between them.")
    last = (clicked or {}).get("last_clicked") or {}
    if last.get("lat") is None:
        return
    if point.get("lat") is not None:
        if abs(float(last["lat"]) - float(point["lat"])) < 0.02 and abs(float(last["lng"]) - float(point["lon"])) < 0.02:
            return
    signature = (round(float(last["lat"]), 4), round(float(last["lng"]), 4))
    if signature == st.session_state.map_click:
        return
    st.session_state.map_click = signature
    try:
        apply_place(resolve_point(last["lat"], last["lng"]))
    except (ApiError, Exception) as error:
        st.error(str(error))


def render_place_summary():
    payload = st.session_state.place
    if not payload:
        return
    point = payload.get("place") or {}
    nearest = payload.get("nearest") or {}
    weather = payload.get("weather") or {}
    name = point.get("name") or "Selected place"
    state = point.get("state") or ""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='glass'><p class='metric-label'>{t('selected')}</p>"
            f"<p class='metric-value'>{name}</p><p>{state}</p></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='glass'><p class='metric-label'>{t('nearest')}</p>"
            f"<p class='metric-value'>{nearest.get('district', '')}</p>"
            f"<p>{nearest.get('state', '')} · {nearest.get('distance_km', '')} km · {nearest.get('proximity_level', '')}</p></div>",
            unsafe_allow_html=True,
        )
    with c3:
        if weather.get("success"):
            pin = ""
            if weather.get("latitude") is not None:
                pin = f"{weather.get('latitude')}, {weather.get('longitude')}"
            st.markdown(
                f"<div class='glass'><p class='metric-label'>{t('weather_now')}</p>"
                f"<p class='metric-value'>{weather.get('temperature')} °C</p>"
                f"<p>{weather.get('condition')} · {weather.get('humidity')}% humidity</p>"
                f"<p>{t('weather_pin')}: {weather.get('city') or name}"
                + (f" ({pin})" if pin else "")
                + "</p></div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning(weather.get("msg") or "Weather is not available for this point yet.")
    if nearest.get("note"):
        st.caption(nearest["note"])


def render_soil_tab():
    if not st.session_state.place:
        st.info(t("no_place"))
        return
    st.caption(t("first_run"))
    if st.session_state.use_own_soil:
        st.caption("Soil-test values will be sent to the model.")
    else:
        st.caption(t("soil_estimate"))
    st.checkbox(t("own_soil"), key="use_own_soil")
    st.selectbox(t("soil_type"), SOIL_TYPES, key="soil")
    n_col, p_col, k_col, ph_col = st.columns(4)
    with n_col:
        st.number_input(t("nitrogen"), min_value=0, max_value=150, step=1, key="N")
    with p_col:
        st.number_input(t("phosphorus"), min_value=0, max_value=150, step=1, key="P")
    with k_col:
        st.number_input(t("potassium"), min_value=0, max_value=150, step=1, key="K")
    with ph_col:
        st.number_input(t("ph"), min_value=0.0, max_value=14.0, step=0.1, key="ph")

    with st.expander(t("soil_bank")):
        try:
            cities = get("/api/soil/cities", token=st.session_state.token)
            st.caption(", ".join((cities.get("cities") or [])[:24]))
            nearest_name = ((st.session_state.place or {}).get("nearest") or {}).get("district")
            if nearest_name and st.button("Load saved soil row for the nearest district"):
                row = get(
                    "/api/soil/data",
                    token=st.session_state.token,
                    params={"city": nearest_name, "soil_type": st.session_state.soil},
                )
                data = (row or {}).get("data") or {}
                if data:
                    st.session_state.pending_soil = {
                        "N": min(150, int(data.get("N") or st.session_state.N)),
                        "P": min(150, int(data.get("P") or st.session_state.P)),
                        "K": min(150, int(data.get("K") or st.session_state.K)),
                        "ph": float(data.get("ph") or st.session_state.ph),
                        "soil": st.session_state.soil,
                    }
                    st.rerun()
                else:
                    st.info(row.get("message") or "No stored row. The district estimate above is still available.")
        except (ApiError, Exception) as error:
            st.caption(str(error))

    if st.button(t("recommend"), type="primary"):
        payload = farmer_payload()
        if payload["latitude"] is None:
            st.error(t("no_place"))
            return
        with st.spinner(t("working")):
            try:
                result = post("/api/crop/advisory", payload, token=st.session_state.token, timeout=180)
            except (ApiError, Exception) as error:
                st.error(str(error))
                return
        if not result.get("success"):
            st.error(result.get("message") or result.get("errors") or "The advisory could not be built.")
            return
        st.session_state.last_payload = payload
        st.session_state.last_result = result
        st.session_state.audio = None
        st.session_state.answer = None
        st.rerun()


def render_results():
    result = st.session_state.last_result
    if not result:
        return
    st.markdown("---")
    basis = result.get("advisory_basis")
    st.subheader(result.get("recommended_crop", "").title())
    if basis == "field":
        st.success(t("basis_field"))
    else:
        st.warning(t("basis_trend"))
    top = (result.get("top_3") or [{}])[0]
    c1, c2, c3 = st.columns(3)
    c1.metric(t("confidence"), f"{round(float(top.get('confidence') or 0) * 100)}%")
    c2.metric(t("risk"), str(result.get("risk_level") or ""))
    c3.metric("Basis", basis or "")
    if result.get("risk_flags"):
        st.warning("\n".join(f"- {flag}" for flag in result["risk_flags"]))

    level = result.get("risk_level")
    gauge_value = {"low": 25, "moderate": 60, "high": 90}.get(level, 40)
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gauge_value,
        title={"text": t("risk")},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#e4c56a"},
            "steps": [
                {"range": [0, 40], "color": "#1f8f55"},
                {"range": [40, 70], "color": "#8a6a22"},
                {"range": [70, 100], "color": "#8a3030"},
            ],
        },
    ))
    st.plotly_chart(dark_chart(gauge), use_container_width=True)

    st.markdown(f"### {t('advisory')}")
    st.markdown(result.get("advisory_text") or "")
    speak_col, pdf_col = st.columns(2)
    with speak_col:
        if st.button(t("speak")):
            try:
                from gtts import gTTS

                lang = "hi" if st.session_state.language == "hi" else "en"
                clip = ROOT / "advisory_audio.mp3"
                gTTS(result.get("advisory_text") or "", lang=lang).save(str(clip))
                st.session_state.audio = clip.read_bytes()
            except Exception as error:
                st.warning(f"Speech could not be prepared ({error}). The written advisory is still above.")
        if st.session_state.audio:
            st.audio(st.session_state.audio, format="audio/mp3")
    with pdf_col:
        if st.button(t("download")):
            try:
                pdf = post_bytes(
                    "/api/crop/advisory/pdf",
                    st.session_state.last_result,
                    token=st.session_state.token,
                    timeout=60,
                )
                st.download_button("Save krishi_advisory.pdf", data=pdf, file_name="krishi_advisory.pdf", mime="application/pdf")
            except (ApiError, Exception) as error:
                st.error(str(error))

    cards = result.get("crop_cards") or []
    if cards:
        st.markdown(f"### {t('yield_chart')}")
        names = [card["crop"].title() for card in cards]
        fig = go.Figure()
        fig.add_bar(name="Low", x=names, y=[card["yield_low"] for card in cards], marker_color="#1f8f55")
        fig.add_bar(name="High", x=names, y=[card["yield_high"] for card in cards], marker_color="#e4c56a")
        fig.update_layout(barmode="group")
        st.plotly_chart(dark_chart(fig), use_container_width=True)
        for card in cards:
            price = card.get("msp_inr_per_quintal")
            price_line = f"Rs {price}/quintal. {card.get('msp_note')}" if price else card.get("msp_note")
            st.markdown(
                f"**{card['crop'].title()}** · {card.get('yield_low')}-{card.get('yield_high')} {card.get('yield_unit')} · {card.get('season')}"
            )
            st.caption(f"{t('price')}: {price_line} {card.get('price_disclaimer')}")
            st.caption(f"{t('challenges')}: {'; '.join(card.get('challenges') or [])}")
            st.caption("States: " + ", ".join(card.get("states") or []))
            profile = card.get("training_profile") or {}
            if profile:
                st.caption(
                    "Training-table trend for this crop: "
                    f"N {profile.get('N')}, P {profile.get('P')}, K {profile.get('K')}, "
                    f"rainfall {profile.get('rainfall')} mm."
                )

    left, right = st.columns(2)
    with left:
        confidence_fig = go.Figure(go.Bar(
            x=[item["crop"].title() for item in result.get("top_3") or []],
            y=[item["confidence"] for item in result.get("top_3") or []],
            marker_color="#8ee0a8",
        ))
        confidence_fig.update_layout(title=t("confidence_chart"))
        st.plotly_chart(dark_chart(confidence_fig), use_container_width=True)
        st.markdown(f"**{t('nearby')}**")
        st.write(", ".join(result.get("nearby_crops") or []))
    with right:
        daily = (result.get("weather") or {}).get("daily") or []
        if daily:
            rain_fig = go.Figure(go.Scatter(
                x=[day["date"] for day in daily],
                y=[day["rain_mm"] for day in daily],
                mode="lines+markers",
                line={"color": "#e4c56a"},
            ))
            rain_fig.update_layout(title=t("rain_chart"))
            st.plotly_chart(dark_chart(rain_fig), use_container_width=True)
        weather = result.get("weather") or {}
        st.caption(weather.get("rainfall_note") or "")
        fertilizer = result.get("fertilizer") or {}
        st.markdown(f"**{t('fertilizer')}**")
        st.write(fertilizer.get("fertilizer_type") or fertilizer.get("type") or "")
        st.caption(fertilizer.get("description") or "")
        st.caption(fertilizer.get("dosage") or "")

    notes = result.get("knowledge") or []
    if notes:
        st.markdown(f"### {t('knowledge')}")
        for note in notes:
            title, _, body = note.partition(":")
            with st.expander(title.strip() or "Note"):
                st.write(body.strip() or note)

    st.markdown(f"### {t('lookup')}")
    other = st.selectbox("Crop", MODEL_CROPS, key="fertilizer_lookup")
    if st.button("Fetch fertilizer note"):
        try:
            looked = get(f"/api/fertilizer/{other}")
            st.json(looked)
        except (ApiError, Exception) as error:
            st.error(str(error))

    st.markdown(f"### {t('ask')}")
    st.caption(t("ask_help"))
    question = st.text_area(t("ask"), key="question_text")
    symptom = st.text_input(t("symptom"), key="symptom_text")
    if st.button(t("ask_button")):
        asked = " ".join(part for part in (question, symptom) if part and part.strip())
        if not asked:
            st.warning("Type a question or a symptom first.")
        else:
            context = {
                "recommended_crop": result.get("recommended_crop"),
                "advisory_basis": result.get("advisory_basis"),
                "proximity": result.get("proximity"),
                "soil_info": result.get("soil_info"),
                "npk": {
                    "N": (result.get("soil_info") or {}).get("N"),
                    "P": (result.get("soil_info") or {}).get("P"),
                    "K": (result.get("soil_info") or {}).get("K"),
                },
                "nearby_crops": result.get("nearby_crops"),
            }
            try:
                answer = post(
                    "/api/crop/ask",
                    {"question": asked, "language": st.session_state.language, "context": context},
                    token=st.session_state.token,
                    timeout=90,
                )
                st.session_state.answer = answer
            except (ApiError, Exception) as error:
                st.error(str(error))
    if st.session_state.answer:
        st.markdown(st.session_state.answer.get("answer") or "")
        if st.button("Play this answer"):
            try:
                from gtts import gTTS

                lang = "hi" if st.session_state.language == "hi" else "en"
                clip = ROOT / "answer_audio.mp3"
                gTTS(st.session_state.answer.get("answer") or "", lang=lang).save(str(clip))
                st.audio(clip.read_bytes(), format="audio/mp3")
            except Exception as error:
                st.warning(str(error))


def render_farm_tab():
    place = (st.session_state.place or {}).get("place") or {}
    name = st.text_input(t("farm_name"), value=place.get("name") or "")
    area = st.number_input(t("area"), min_value=0.0, value=1.0, step=0.5)
    notes = st.text_area(t("notes"))
    if st.button(t("save_farm")):
        payload = {
            "username": st.session_state.username,
            "farm_name": name,
            "area_acres": area,
            "notes": notes,
            "latitude": place.get("lat"),
            "longitude": place.get("lon"),
            "place": place.get("name"),
            "state": place.get("state"),
        }
        try:
            saved = post("/api/farm/add", payload, token=st.session_state.token)
            if saved.get("success"):
                st.success(saved.get("msg"))
            else:
                st.error(saved.get("msg"))
        except (ApiError, Exception) as error:
            st.error(str(error))
    try:
        listing = get("/api/farm/list", token=st.session_state.token, params={"username": st.session_state.username})
        farms = listing.get("farms") or []
        if farms:
            st.dataframe(farms, use_container_width=True)
        else:
            st.caption("No farms saved for this account yet.")
    except (ApiError, Exception) as error:
        st.caption(str(error))


def render_history_tab():
    try:
        payload = get("/api/history/", token=st.session_state.token)
    except (ApiError, Exception) as error:
        st.error(str(error))
        return
    rows = []
    for item in payload.get("history") or []:
        result = item.get("result") or []
        top = result[0] if result else {}
        entered = item.get("input") or {}
        rows.append({
            "Place": entered.get("location") or item.get("user_selected_location"),
            "Crop": top.get("crop") if isinstance(top, dict) else top,
            "Confidence": top.get("confidence") if isinstance(top, dict) else "",
            "Nearest": item.get("nearest_district"),
            "Distance km": item.get("distance_km"),
        })
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info(t("no_history"))


def main():
    init_state()
    clear_saved_login = bool(st.session_state.pop("clear_session", False))
    persist = {}
    if st.session_state.token:
        persist = {"token": st.session_state.token, "username": st.session_state.username}
    session_event = browser_bridge(
        role="session",
        language=st.session_state.language,
        show_tools=False,
        persist=persist,
        clear=clear_saved_login,
        key="krishi_session_bridge",
    )
    handle_bridge(session_event)
    consume_device_location()
    if not st.session_state.token:
        render_auth()
        return
    render_sidebar()
    st.markdown(
        f"<div class='hero'><h1>{t('title')}</h1><p>{t('subtitle')}</p></div>",
        unsafe_allow_html=True,
    )
    place_tab, soil_tab, farm_tab, history_tab = st.tabs([t("locate"), t("soil"), t("farm"), t("history")])
    with place_tab:
        render_place_tab()
    with soil_tab:
        render_soil_tab()
    with farm_tab:
        render_farm_tab()
    with history_tab:
        render_history_tab()
    render_results()
    st.caption(t("footer"))


if __name__ == "__main__":
    main()
else:
    main()
