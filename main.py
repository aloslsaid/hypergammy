from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from engine import FaceEngine

BASE_DIR = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
CATEGORIES = json.loads((BASE_DIR / "categories.json").read_text(encoding="utf-8"))

app = FastAPI(
    title="Hypergammy Face Landmark Analysis",
    version="0.1.0",
    description="Experimental landmark extraction and reference-coverage reporting.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

engine = FaceEngine()


@app.get("/")
def root():
    return {"name": "Hypergammy", "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "landmark_engine_ready": engine.ready}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "A filename is required.")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Upload a JPG, PNG, or WEBP image.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if not content:
        raise HTTPException(400, "The uploaded image is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Image must be 10 MB or smaller.")

    try:
        result = engine.analyze(content)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    features = result["features"]
    categories = []
    for item in CATEGORIES:
        missing_features = [
            name for name in item.get("required_features", [])
            if name not in features
        ]
        reference = BASE_DIR / item["reference_path"]
        if missing_features:
            status = "unavailable"
            explanation = "Required measurement is not implemented by the current landmark engine: " + ", ".join(missing_features)
        elif not reference.is_file():
            status = "reference_missing"
            explanation = "The category measurement is available, but its reference image is not included. No score is calculated."
        else:
            # A reference image alone is not sufficient: a calibrated comparison
            # implementation is required before a score can be responsibly shown.
            status = "unavailable"
            explanation = "A reference file exists, but calibrated comparison is not implemented."
        categories.append({
            "category_id": item["category_id"],
            "name": item["display_name"],
            "weight_group": item["group_id"],
            "status": status,
            "score": None,
            "explanation": explanation,
            "confidence": float(result["confidence"]),
        })

    limitations = [
        "No calibrated reference images are currently included in this repository; category scores are therefore withheld.",
        "The landmark measurements are experimental and are not a validated attractiveness, identity, medical, or psychological assessment.",
        "A single frontal image cannot reliably measure 3D projection, skin texture, or features hidden by hair and pose.",
        "Image quality, pose, lighting, camera optics, and landmark errors can change the measurements.",
    ]
    return {
        "overall_score": None,
        "analyzed_categories": 0,
        "coverage_percent": 0,
        "overall_confidence": float(result["confidence"]),
        "categories": categories,
        "image_quality": result["quality"],
        "limitations": limitations,
    }
