"""Crop yield, challenge, and indicative price cards."""
import json
from functools import lru_cache
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "crop_cards.json"


@lru_cache(maxsize=1)
def _cards():
    with _DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)["crops"]


def crop_card(name):
    if not name:
        return None
    card = _cards().get(str(name).lower().replace(" ", ""))
    if not card:
        return None
    return {"crop": str(name).lower().replace(" ", ""), **card}


def cards_for(crops):
    found = []
    for crop in crops:
        name = crop.get("crop") if isinstance(crop, dict) else crop
        card = crop_card(name)
        if card:
            confidence = crop.get("confidence") if isinstance(crop, dict) else None
            found.append({**card, "confidence": confidence})
    return found
