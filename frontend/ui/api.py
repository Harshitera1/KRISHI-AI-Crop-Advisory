
"""Small client for the KRISHI Flask API."""
import os
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5001")

try:
    import streamlit as st
except ImportError:
    st = None

if st is not None:
    try:
        configured_url = st.secrets.get("API_BASE_URL")
    except (FileNotFoundError, KeyError, AttributeError):
        configured_url = None
    if configured_url:
        BASE_URL = configured_url

BASE_URL = BASE_URL.rstrip("/")


class ApiError(Exception):
    pass


def _headers(token):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _payload(response):
    try:
        body = response.json()
    except ValueError:
        body = {"message": response.text[:300] or "Empty response"}
    if response.status_code >= 400:
        message = body.get("message") or body.get("msg") or body.get("errors") or response.reason
        raise ApiError(str(message))
    return body


def get(path, token=None, params=None, timeout=25):
    response = requests.get(
        f"{BASE_URL}{path}",
        headers=_headers(token),
        params=params,
        timeout=timeout,
    )
    return _payload(response)


def post(path, payload, token=None, timeout=90):
    response = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers=_headers(token),
        timeout=timeout,
    )
    return _payload(response)


def post_bytes(path, payload, token=None, timeout=120):
    response = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers=_headers(token),
        timeout=timeout,
    )
    content_type = response.headers.get("content-type", "")
    if "application/pdf" not in content_type:
        _payload(response)
        raise ApiError("The server did not return a PDF.")
    return response.content
