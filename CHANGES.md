# What changed in this upgrade

## Landing-page fixes

Speech and device location now run in the browser, on the Place tab, next to Find this place. The server no longer needs PyAudio, which cannot hear the microphone in the farmer's browser. A spoken village that is not in the old list is geocoded and then matched to the nearest of 400 profiles. Weather is requested for the pin's latitude and longitude, and the card shows those coordinates. After a place is set, the browser speaks a short confirmation. Login is kept in the browser for a reload; the token itself lasts 12 hours. Sign out clears the saved login.

The map has Dark, Streets, and Satellite layers, a green pin for the selected place, a gold pin for the nearest profile, and a dashed line for the distance.



This file is the handoff for the next person or coding agent. Read it before changing the environment, the crop model, or the location logic.

## What the farmer can do now

1. Sign in with the existing account API (`/api/auth/signup` and `/api/auth/login`).
2. Choose a place in four ways: click any point on the map, type a village or city, use the browser location button, or speak a place name. Typing still works if the microphone does not.
3. The API geocodes that place (OpenWeather, then OpenStreetMap if needed), reads current weather and a five-day forecast for those coordinates, and finds the nearest district in the local gazetteer.
4. Nitrogen, phosphorus, potassium, and pH are filled from that district and labeled as an estimate. If the farmer edits them, or ticks the soil-test box, those entered values are what the model uses.
5. The same Random Forest as before recommends crops. Rainfall sent to the model is the next five days of forecast rain, scaled to 90 days, because the model was trained on seasonal rainfall rather than one day's rain. The screen states that this is a proxy.
6. If the point is far from the nearest profile, confidence is low, or the soil values are still the estimate, the screen says the result is the nearest known trend, not a laboratory result for that exact field.
7. The result shows the crop, confidence, risk, yield range, challenges, states where the crop is commonly grown, an indicative price note, fertilizer, nearby crops, the notes that were retrieved, a written advisory in English or Hindi, audio of that text, and a PDF of the same advisory.
8. A follow-up box answers a new question, including a leaf or pest symptom, from the same notes. It does not classify a photograph. There is no image model in this project.
9. My Farm saves a place against the signed-in user. History lists earlier advisories.

## What was wrong before

- Map clicks and voice snapped to about 14 hard-coded names, then weather was fetched for that name.
- Rainfall for the model was `humidity * 3`.
- Yield, profit, and the regional table on the old screen were hard-coded in the browser.
- Spoken output was one fixed sentence, and playback called macOS `afplay`, which does nothing on Linux.
- Soil, farm, and standalone fertilizer routes existed and were not opened from the screen.
- The OpenWeather key was written into `weather_service.py`, so the environment variable was ignored.
- The login token used a hard-coded secret instead of `SECRET_KEY`.
- Two copies of the agronomy notes could drift apart. The API now reads only `rag_standalone/knowledge/`.

## What was deliberately not changed

- The crop model file `backend/models/crop_model.pkl` was not retrained and not replaced. The training table has N, P, K, temperature, humidity, pH, and rainfall. It has no district column, so a new model cannot learn an unknown village until someone has yield labels for those places.
- No new crop dataset was collected. `district_gazetteer.json` is a reference list of about 108 district headquarters used only to name the nearest land profile.
- No Google Maps, Geocoding, or paid weather product was added.
- Prices are not live mandi rates. Where a crop has a CACP minimum support price, the card cites the 2024-25 reference and tells the farmer to confirm the current notification. Fruit and plantation crops say that no MSP applies.
- Pest detection is a written scouting answer from the pest note. A camera model is future work. Do not add a fake accuracy number.
- The duplicate `/api/user/signup` and `/api/user/login` routes are still in the code and are not used by the screen. Sign-in stays on `/api/auth`.

## New or updated commands

From the project folder (`KRISHI-AI-Crop-`):

```bash
chmod +x run.sh
./run.sh
```

That is the supported start. It creates `.venv` with Python 3.12 if present, otherwise 3.11 or 3.13, installs `requirements.txt`, and starts both processes.

Manual start, only if you need separate terminals:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
cd backend && python main.py
```

In a second terminal, from the project folder:

```bash
source .venv/bin/activate
cd frontend && streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```

Regenerate the gazetteer and crop cards after editing `backend/data/build_reference_data.py`:

```bash
python backend/data/build_reference_data.py
```

The running app reads the JSON files, not the builder.

## Environment rules that will break the app if ignored

Create `backend/.env` from `.env.example`. The running folder may already have a filled `.env`. Do not commit it and do not put it in a zip you share.

| Name | Required for | If it is missing |
|---|---|---|
| `MONGO_URI` | Sign-in, history, saved farms, stored soil rows | The API still starts, but those calls fail. District estimates still load from the JSON gazetteer. |
| `SECRET_KEY` | Login tokens | Login cannot issue a token. Old tokens signed with the previous hard-coded secret are invalid. Sign in again. |
| `WEATHER_API_KEY` | Geocoding and weather | Place search falls back to OpenStreetMap for the name, but the advisory stops because the model needs weather. |
| `GROQ_API_KEY` | Written advisory and follow-up answers | The crop list still returns. The advisory text becomes a short automatic summary that says the language model is unavailable. |

Also:

- Use Python 3.11, 3.12, or 3.13. Do not point this project at Python 3.14 or 3.15. `run.sh` refuses to pick those versions.
- `requirements.txt` installs CPU PyTorch (`torch==2.6.0+cpu`) from the PyTorch CPU index. Do not replace it with a CUDA wheel unless this machine has a GPU and you accept a multi-gigabyte install.
- `scikit-learn` must stay at `1.6.1`. That is the version that saved `crop_model.pkl`.
- The first advisory needs network access so `sentence-transformers` can cache `all-MiniLM-L6-v2`.
- Microphone input needs a browser or desktop mic. `SpeechRecognition` is installed. `PyAudio` is optional and is not required. If the mic fails, type the place.
- Speech playback uses `gTTS` and Streamlit's audio player. It needs network access to Google's text-to-speech endpoint. The words it speaks are the advisory just generated, not a fixed clip.
- N, P, and K on the form and in the API must be between 0 and 150. The training table's apple and grape rows often have potassium above 150, so those classes are harder to reach from this form. That limit is intentional and matches the API check.
- Rotate the OpenWeather key if this project was ever shared while the key sat inside `weather_service.py`. The source file no longer contains a key.

## API the screen uses

- `POST /api/auth/signup`, `POST /api/auth/login`
- `GET /api/location/resolve?q=` or `?lat=&lon=` (signed in)
- `GET /api/location/districts`
- `GET /api/weather/search?q=`, `GET /api/weather/at?lat=&lon=`, `GET /api/weather/<city>`
- `GET /api/soil/cities`, `GET /api/soil/data?city=&soil_type=`
- `POST /api/crop/advisory`
- `POST /api/crop/advisory/pdf` (send the advisory already on screen so the PDF matches it)
- `POST /api/crop/ask`
- `GET /api/fertilizer/<crop>`
- `POST /api/farm/add`, `GET /api/farm/list`
- `GET /api/history/`

`POST /api/crop/recommend` still runs the same pipeline. The screen calls `/api/crop/advisory`.

## How a later agent should work in this folder

- Keep one knowledge folder: `rag_standalone/knowledge/`.
- Keep place search on coordinates. Do not restore a fixed city list as the only input.
- Do not retrain the Random Forest unless a new labeled table exists and the pickle version is updated in `requirements.txt` in the same change.
- Do not describe a pest-photo accuracy, a live mandi feed, or IoT soil sensors in the report or the UI. They are not in this build.
- The final report is `docs/KRISHI_AI_Final_Project_Report.md`. If the code changes, change the report in the same pass so a demo and the document still match.
