# Hypergammy — Experimental Facial Landmark Analysis

Hypergammy is an experimental React + TypeScript interface backed by a Python FastAPI service. It extracts facial landmarks with OpenCV and MediaPipe, reports basic image-quality diagnostics, and describes which configured measurement categories are supported.

> **Important:** This repository does not currently include calibrated reference images or a validated reference-comparison algorithm. The API therefore withholds category and overall scores instead of inventing them. This is a research prototype, not an attractiveness rating, identity system, medical tool, or decision-making system.

## Current capabilities

- JPG, PNG and WEBP upload with a 10 MB server-side limit.
- Single-face detection and basic image-quality warnings.
- Landmark normalization and experimental 2D feature extraction.
- 34 category definitions, grouped by facial region.
- Explicit reporting for missing measurements and missing reference images.
- React interface for upload, diagnostics and category status.

## Repository structure

- `App.tsx`, `main.tsx`, `styles.css`, `types.ts`: frontend.
- `main.py`: FastAPI API (`/health`, `/analyze`).
- `engine.py`: OpenCV and MediaPipe landmark extraction.
- `categories.json`, `weights.json`, `scoring.json`: category and experimental configuration.
- `tests/test_config.py`: category configuration integrity check.

## Requirements

- Node.js 20+ and npm.
- Python 3.11 (recommended for the pinned MediaPipe dependency).

## Start the backend

From the repository root:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Check `http://127.0.0.1:8000/health`. If MediaPipe cannot initialize in your Python environment, the health response reports that the landmark engine is unavailable and `/analyze` returns a service error rather than a fabricated result.

## Start the frontend

In a second terminal:

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The frontend sends images to `http://127.0.0.1:8000/analyze` by default. Set `VITE_API_URL` if the API is hosted elsewhere.

## API

- `GET /`: service identity and API docs location.
- `GET /health`: API and landmark-engine readiness.
- `POST /analyze`: multipart upload field `file`; accepts JPG, PNG or WEBP and returns image diagnostics plus category availability.

The service does not persist uploaded images. Deployments should still use HTTPS, access controls, rate limiting, request-size limits and a documented retention policy.

## Tests and checks

```bash
python -m pytest
npm run build
```

These checks must be run in the target environment before claiming a successful release.

## Roadmap to validated reference comparison

1. Add properly licensed reference images and record their provenance and consent.
2. Define a reproducible landmark/feature representation for each category.
3. Calibrate normalization and distance functions on a representative, consented evaluation set.
4. Validate reliability across pose, lighting, image quality and demographic groups.
5. Publish uncertainty, failure cases and evaluation methodology before enabling numeric scores.

Do not add arbitrary reference images or tune weights to produce attractive-looking scores. A missing or unvalidated measurement should remain unavailable.

## Privacy and responsible use

Facial images and derived measurements are sensitive biometric information. Process only images you have permission to use, minimize retention, and provide deletion controls if storage is introduced. Landmark estimates are affected by camera quality, pose, lighting and model bias. Do not use outputs for hiring, access control, identity verification, medical decisions, or judgments about a person's worth.

## License

No license is declared. All rights reserved unless the repository owner adds an explicit license.
