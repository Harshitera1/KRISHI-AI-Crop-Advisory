"""
Voice Controller - Handles voice-based inputs and outputs
Processes voice commands, location extraction, and voice synthesis
"""
import logging
from flask import g
from services.location_service import match_voice_location
from services.crop_service import predict_crop

logger = logging.getLogger(__name__)


def extract_soil_from_speech(text):
    """
    Extract soil type from spoken text
    Returns soil type or None
    """
    if not text:
        return None

    text_lower = text.lower()
    soil_types = {
        "loamy": ["loamy", "loam", "loamy soil"],
        "sandy": ["sandy", "sandy soil", "sand"],
        "clay": ["clay", "clay soil", "clayey"],
        "silty": ["silty", "silty soil", "silt"],
        "peaty": ["peaty", "peaty soil", "peat"]
    }

    for soil_type, keywords in soil_types.items():
        for keyword in keywords:
            if keyword in text_lower:
                logger.info(
                    "Soil type extracted from voice",
                    extra={
                        "event": "soil_extracted",
                        "soil_type": soil_type,
                        "detected_keyword": keyword
                    }
                )
                return soil_type.capitalize()

    return None


def process_voice_command(voice_text, ml_input):
    """
    Process complete voice command for crop recommendation
    Extracts location, soil, and triggers ML prediction
    Returns structured result with crop recommendation
    """
    if not voice_text:
        return {
            "success": False,
            "message": "No voice input detected"
        }

    logger.info(
        "Processing voice command",
        extra={
            "event": "voice_command_received",
            "request_id": g.get("request_id"),
            "text": voice_text[:100]  # Log first 100 chars
        }
    )

    # Extract location from voice
    matched_location = match_voice_location(voice_text)

    if not matched_location:
        logger.warning(
            "Location not extracted from voice",
            extra={
                "event": "voice_location_failed",
                "request_id": g.get("request_id"),
                "input": voice_text
            }
        )
        return {
            "success": False,
            "message": "Could not extract location from speech. Please say a major city name like 'Delhi' or 'Meerut'."
        }

    # Extract soil type from voice
    soil_type = extract_soil_from_speech(voice_text)

    # Get ML prediction
    ml_result = predict_crop(ml_input)

    if not isinstance(ml_result, list):
        logger.error(
            "ML prediction failed in voice controller",
            extra={
                "event": "voice_ml_error",
                "request_id": g.get("request_id"),
                "error": ml_result
            }
        )
        return {
            "success": False,
            "message": "Failed to generate crop recommendation"
        }

    logger.info(
        "Voice command processed successfully",
        extra={
            "event": "voice_processed",
            "request_id": g.get("request_id"),
            "location": matched_location["location"],
            "soil": soil_type,
            "top_crop": ml_result[0]["crop"] if ml_result else None
        }
    )

    return {
        "success": True,
        "location": matched_location,
        "soil_type": soil_type,
        "ml_result": ml_result
    }
