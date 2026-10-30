# KRISHI AI

KRISHI AI is a crop advisory desk for a B.Tech capstone. A farmer, or a person helping a farmer, picks any place, and the system reads live weather for that point, compares it with the nearest district profile, and runs the existing crop model. A short written advisory, grounded in local agronomy notes, can be played aloud or saved as a PDF.

The screen is Streamlit. The API is Flask. Accounts and history use MongoDB Atlas. The crop model is the saved Random Forest in `backend/models/crop_model.pkl`. It was not retrained for this upgrade.

## Run

Python 3.11, 3.12, or 3.13 is required. From this folder:

```bash
chmod +x run.sh
./run.sh
```

The script creates `.venv`, installs `requirements.txt` (including the CPU build of PyTorch), and starts:

- API: http://127.0.0.1:5001
- Advisory desk: http://127.0.0.1:8501

On the first advisory, the app downloads the small `all-MiniLM-L6-v2` embedding model. That step needs a network connection once.

## Environment

Copy `.env.example` to `backend/.env` if that file is not already present. Four backend values are required:

- `MONGO_URI`
- `SECRET_KEY`
- `WEATHER_API_KEY` (OpenWeather)
- `GROQ_API_KEY`

Login and saved history need MongoDB. A crop advisory also needs OpenWeather and Groq. If Atlas is down, sign-in fails, but district soil estimates still come from the local gazetteer once a signed-in session exists.

The Streamlit deployment should set `API_BASE_URL` in Streamlit Secrets (or the environment). It overrides the local default `http://127.0.0.1:5001`. For a deployed API, set `CORS_ORIGINS` on the backend to the exact Streamlit origin (comma-separated for more than one); production starts with no cross-origin allowlist if neither `CORS_ORIGINS` nor `FRONTEND_URL` is configured. Set `FLASK_ENV=production` on Render to force debug off.

`CHANGES.md` lists what this upgrade changed, how a farmer moves through the desk, and what a later coding session must not reinstall or replace.

## Layout

- `frontend/app.py` is the dashboard.
- `backend/main.py` is the API.
- `backend/data/district_gazetteer.json` is the nearest-land reference, not a new training set.
- `backend/data/crop_cards.json` holds yield ranges, challenges, and indicative MSP notes.
- `rag_standalone/knowledge/` is the only agronomy note set used by retrieval.
- `docs/KRISHI_AI_Final_Project_Report.md` is the final project report.
