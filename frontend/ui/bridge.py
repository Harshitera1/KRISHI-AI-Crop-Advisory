"""Browser microphone, device location, spoken confirmation, and saved login."""
from pathlib import Path

import streamlit.components.v1 as components

_bridge = components.declare_component(
    "krishi_bridge",
    path=str(Path(__file__).resolve().parent / "krishi_bridge"),
)


def browser_bridge(
    *,
    role,
    language="en",
    show_tools=False,
    persist=None,
    clear=False,
    announce="",
    announce_id="",
    speak_label="Speak a place name",
    geo_label="Use this device's location",
    key=None,
):
    value = _bridge(
        role=role,
        language=language,
        show_tools=show_tools,
        persist=persist or {},
        clear=bool(clear),
        announce=announce or "",
        announce_id=announce_id or "",
        speak_label=speak_label,
        geo_label=geo_label,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
