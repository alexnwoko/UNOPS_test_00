"""
Disaster-tweet classifier API + UI (FastAPI, single Cloud Run service).

Endpoints:
  GET  /         -> the web UI (static HTML)
  GET  /health   -> {"status": "ok"}
  POST /predict  -> {"label": 0|1, "score": float in [0,1]}

The model (TF-IDF + calibrated Logistic Regression) runs in-process; there are
no external/paid API calls at inference time, per the assessment constraints.
"""
import os
import joblib
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from textclean import clean  # noqa: F401  needed so the pickled model can resolve it

MODEL_PATH = os.environ.get("MODEL_PATH", "model.joblib")
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Disaster Tweet Classifier", version="1.0.0")


class PredictIn(BaseModel):
    text: str = Field(..., description="Tweet / short text to classify")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: PredictIn):
    text = (payload.text or "").strip()
    if not text:
        return JSONResponse(status_code=422, content={"error": "text must not be empty"})
    score = float(model.predict_proba([text])[0][1])
    label = int(score >= 0.5)
    return {"label": label, "score": round(score, 4)}


@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))
