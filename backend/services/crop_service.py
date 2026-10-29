import joblib
import pandas as pd
import os
import logging

from flask import g  # for request_id

logger = logging.getLogger(__name__)

# Absolute safe path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/crop_model.pkl")

# Load model once
try:
    model = joblib.load(MODEL_PATH)
    logger.info(
        "Model loaded successfully",
        extra={"event": "model_load"}
    )
except Exception as e:
    logger.error(
        "Model loading failed",
        extra={"event": "model_error", "error": str(e)}
    )
    model = None


def predict_crop(data):
    if model is None:
        return "Model not loaded"

    try:
        input_df = pd.DataFrame([{
            "N": data.get("N", 0),
            "P": data.get("P", 0),
            "K": data.get("K", 0),
            "temperature": data.get("temperature", 0),
            "humidity": data.get("humidity", 0),
            "ph": data.get("ph", 7),
            "rainfall": data.get("rainfall", 0)
        }])

        logger.info(
            "Running ML prediction",
            extra={
                "event": "ml_prediction_start",
                "request_id": g.get("request_id"),
                "input": data
            }
        )

        # 🔥 Get probabilities
        probs = model.predict_proba(input_df)[0]
        crops = model.classes_

        # 🔥 Top 3 crops
        top_indices = probs.argsort()[-3:][::-1]

        top_3 = []
        for i in top_indices:
            top_3.append({
                "crop": crops[i],
                "confidence": round(float(probs[i]), 3)
            })

        logger.info(
            "ML prediction completed",
            extra={
                "event": "ml_prediction_end",
                "request_id": g.get("request_id"),
                "result": top_3
            }
        )

        return top_3

    except Exception as e:
        logger.error(
            "Prediction error",
            extra={
                "event": "ml_error",
                "request_id": g.get("request_id"),
                "error": str(e)
            }
        )
        return "Prediction error"