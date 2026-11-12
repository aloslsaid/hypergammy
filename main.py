from __future__ import annotations

import json
import math
import threading
from functools import lru_cache
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from engine import FaceEngine

ROOT = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

with (ROOT / "categories.json").open("r", encoding="utf-8") as handle:
    CATEGORIES = json.load(handle)
with (ROOT / "weights.json").open("r", encoding="utf-8") as handle:
    GROUP_WEIGHTS = json.load(handle).get("groups", {})
with (ROOT / "scoring.json").open("r", encoding="utf-8") as handle:
    SCORING = json.load(handle)

engine = FaceEngine()
engine_lock = threading.Lock()

app = FastAPI(
    title="Hypergammy Facial Reference Analysis",
    version="1.0.0",
    description="Experimental, reference-based facial landmark comparison. Not an attractiveness or identity assessment.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _numeric_vector(value):
    try:
        vector = np.asarray(value, dtype=np.float64).reshape(-1)
    except (TypeError, ValueError):
        return None
    if vector.size == 0 or not np.isfinite(vector).all():
        return None
    return vector


def _reference_features(relative_path: str):
    candidate = (ROOT / relative_path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    try:
        with engine_lock:
            result = engine.analyze(candidate.read_bytes())
        return result["features"]
    except Exception:
        return None


@lru_cache(maxsize=64)
def _cached_reference_features(relative_path: str):
    return _reference_features(relative_path)


def _compare_category(category, uploaded_features, image_confidence):
    name = category["display_name"]
    base = {
        "category_id": category["category_id"],
        "name": name,
        "weight_group": category["group_id"],
        "score": None,
        "confidence": 0.0,
        "distance": None,
    }

    if category.get("initial_status") == "unavailable":
        return {
            **base,
            "status": "not_assessable",
            "explanation": category.get("description", "This measurement is not supported."),
        }

    required = category.get("required_features", [])
    if not required or any(key not in uploaded_features for key in required):
        return {
            **base,
            "status": "not_assessable",
            "explanation": "The current landmark engine does not provide every measurement required for this category.",
        }

    reference_path = category.get("reference_path", "")
    reference_features = _cached_reference_features(reference_path)
    if reference_features is None:
        return {
            **base,
            "status": "reference_missing",
            "explanation": "No readable reference image is configured for this category.",
        }

    distances = []
    for key in required:
        left = _numeric_vector(uploaded_features.get(key))
        right = _numeric_vector(reference_features.get(key))
        if left is None or right is None or left.shape != right.shape:
            return {
                **base,
                "status": "not_assessable",
                "explanation": f"The uploaded and reference measurements for '{key}' are incompatible.",
            }
        distances.append(float(np.linalg.norm(left - right) / math.sqrt(left.size)))

    distance = float(np.mean(distances))
    scale = float(category.get("score_scale") or SCORING.get("default_score_scale", 0.12))
    if not math.isfinite(distance) or scale <= 0:
        return {
            **base,
            "status": "not_assessable",
            "explanation": "The comparison produced an invalid numeric result.",
        }

    # Experimental similarity transform; this is not a validated human-rating scale.
    score = max(0.0, min(10.0, 10.0 * math.exp(-distance / scale)))
    confidence = max(0.0, min(1.0, image_confidence))
    return {
        **base,
        "score": round(score, 2),
        "confidence": round(confidence, 3),
        "distance": round(distance, 5),
        "status": "experimental",
        "explanation": category.get("description", "Experimental comparison with the configured reference."),
    }


@app.get("/")
def root():
    return {"name": "Hypergammy", "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "landmark_engine_ready": engine.ready}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, "Upload a JPG, JPEG, PNG, or WEBP image.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if not content:
        raise HTTPException(400, "The uploaded image is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Image must be 10 MB or smaller.")
    if not engine.ready:
        raise HTTPException(503, "The facial landmark engine is unavailable. Check the MediaPipe installation and restart the API.")

    try:
        with engine_lock:
            measured = engine.analyze(content)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(422, f"Could not analyze this image: {exc}") from exc

    category_results = [
        _compare_category(category, measured["features"], measured["confidence"])
        for category in CATEGORIES
    ]
    scored = [item for item in category_results if item["score"] is not None]

    total_weight = sum(float(value) for value in GROUP_WEIGHTS.values()) or 1.0
    scored_groups = {item["weight_group"] for item in scored}
    coverage = sum(float(GROUP_WEIGHTS.get(group, 0.0)) for group in scored_groups)
    overall_score = None
    overall_confidence = 0.0

    if scored:
        group_scores = []
        for group in scored_groups:
            members = [item for item in scored if item["weight_group"] == group]
            group_score = sum(item["score"] for item in members) / len(members)
            group_scores.append((group_score, float(GROUP_WEIGHTS.get(group, 0.0))))
        weighted_total = sum(score * weight for score, weight in group_scores)
        weight_total = sum(weight for _, weight in group_scores)
        if weight_total > 0:
            overall_score = round(weighted_total / weight_total, 2)
        overall_confidence = round(sum(item["confidence"] for item in scored) / len(scored), 3)

    limitations = [
        "All scores are experimental similarity measurements, not scientifically validated attractiveness ratings.",
        "Results depend on image quality, facial pose, landmark accuracy, and the selected reference image.",
        "Only categories with compatible measurements and a configured reference image can receive a score.",
        "The current landmark engine does not support every listed visual or profile-view category.",
        "Do not use these results for identity verification, medical decisions, hiring, or other consequential decisions.",
    ]
    if not scored:
        limitations.append("No categories could be scored because suitable reference images are not currently configured or compatible.")

    quality = measured["quality"]
    return {
        "overall_score": overall_score,
        "analyzed_categories": len(scored),
        "coverage_percent": round(100.0 * coverage / total_weight, 1),
        "overall_confidence": overall_confidence,
        "categories": category_results,
        "image_quality": {
            "width": quality["width"],
            "height": quality["height"],
            "brightness": quality["brightness"],
            "blur_variance": quality["blur_variance"],
            "warnings": quality["warnings"],
        },
        "limitations": limitations,
    }
