"""Small client for the KRISHI Flask API."""
import os
import requests

try:
    import streamlit as st
except ImportError:
    st = None

LOCAL_BACKEND_URL = "http://127.0.0.1:5001"


def _configured_backend_url():
    configured = (
        os.getenv("KRISHI_BACKEND_URL")
        or os.getenv("API_BASE_URL")
    )

    if not configured and st is not None:
        try:
            configured = (
                st.secrets.get("KRISHI_BACKEND_URL")
                or st.secrets.get("API_BASE_URL")
            )
        except (FileNotFoundError, KeyError, AttributeError):
            configured = None

    return (configured or LOCAL_BACKEND_URL).rstrip("/")


BASE_URL = _configured_backend_url()


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
        message = (
            body.get("message")
            or body.get("msg")
            or body.get("errors")
            or response.reason
        )
        raise ApiError(str(message))

    return body


def _connection_error(error):
    return ApiError(
        f"Could not connect to the KRISHI backend at {BASE_URL}. "
        "Check the backend URL and confirm that the backend is available."
    )


def get(path, token=None, params=None, timeout=25):
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            headers=_headers(token),
            params=params,
            timeout=timeout,
        )
    except requests.RequestException as error:
        raise _connection_error(error) from error

    return _payload(response)


def post(path, payload, token=None, timeout=90):
    try:
        response = requests.post(
            f"{BASE_URL}{path}",
            json=payload,
            headers=_headers(token),
            timeout=timeout,
        )
    except requests.RequestException as error:
        raise _connection_error(error) from error

    return _payload(response)


def post_bytes(path, payload, token=None, timeout=120):
    try:
        response = requests.post(
            f"{BASE_URL}{path}",
            json=payload,
            headers=_headers(token),
            timeout=timeout,
        )
    except requests.RequestException as error:
        raise _connection_error(error) from error

    content_type = response.headers.get("content-type", "")
    if "application/pdf" not in content_type:
        _payload(response)
        raise ApiError("The server did not return a PDF.")

    return response.content
