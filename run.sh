#!/usr/bin/env bash
# One-command start for the KRISHI AI advisory desk.
# Uses Python 3.11, 3.12, or 3.13. Python 3.14 and newer are not used:
# several scientific wheels are unreliable there.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PY=""
for candidate in python3.12 python3.11 python3.13; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PY="$candidate"
    break
  fi
done

if [[ -z "$PY" ]]; then
  echo "Install Python 3.11, 3.12, or 3.13, then run this script again."
  exit 1
fi

if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt

if [[ ! -f backend/.env ]]; then
  cp .env.example backend/.env
  echo "Created backend/.env from .env.example."
  echo "Fill in MONGO_URI, SECRET_KEY, WEATHER_API_KEY, and GROQ_API_KEY, then run ./run.sh again."
  exit 1
fi

cleanup() {
  if [[ -n "${BACK_PID:-}" ]]; then
    kill "$BACK_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

cd "$ROOT/backend"
python main.py &
BACK_PID=$!
cd "$ROOT/frontend"
echo "Backend: http://127.0.0.1:5001"
echo "Advisory desk: http://127.0.0.1:8501"
streamlit run app.py --server.headless true --server.port 8501 --server.address 127.0.0.1
