# Hypergammy — Experimental Facial Reference Analysis

Hypergammy is an experimental facial-landmark measurement and reference-comparison project. It combines a React/Vite interface with a FastAPI backend using OpenCV and MediaPipe Face Mesh.

**Important:** measurements and scores are experimental similarity outputs, not scientifically validated attractiveness ratings, medical assessments, identity verification, or decision-making tools.

## Repository structure

- `App.tsx`, `main.tsx`, `styles.css`, `index.html`: React frontend.
- `types.ts`: API response types.
- `package.json`, `vite.config.ts`, `tsconfig*.json`: frontend tooling.
- `main.py`: FastAPI API, including `POST /analyze`.
- `engine.py`: image validation and MediaPipe landmark extraction.
- `categories.json`: category definitions and reference-image paths.
- `weights.json`: experimental category-group weights.
- `scoring.json`: upload and scoring configuration.
- `requirements.txt`: backend dependencies.

## Requirements

- Python 3.10–3.12 recommended for the pinned MediaPipe dependency.
- Node.js 20+ and npm.
- A camera is not required; the app analyzes an uploaded image.

## Backend setup

From the repository root:

Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- Swagger docs: `http://127.0.0.1:8000/docs`

The backend accepts JPG, JPEG, PNG, and WEBP images up to 10 MB. Uploads are processed in memory and are not written to disk by the API. The MediaPipe engine must initialize successfully; if it does not, `/health` reports that it is unavailable and `/analyze` returns HTTP 503.

## Frontend setup

Open a second terminal in the repository root:

```bash
npm install
npm run dev
```

Open the local Vite URL (default `http://127.0.0.1:5173`). The frontend sends uploads to `http://127.0.0.1:8000` by default. To change this, define `VITE_API_URL` in a local `.env` file before starting Vite.

Create a production build with:
```bash
npm run build
npm run preview
```

## Reference images and scoring

Each category in `categories.json` defines its own reference path, for example:

```text
reference_images/
  facial_symmetry/
    reference.jpg
  eye_shape/
    reference.jpg
  ...
```

Add only clear, appropriately licensed reference images that you are authorized to use. The exact folder and filename must match the category's `reference_path`. Restart the API after adding or replacing reference images because processed reference features are cached in memory.

A category receives a score only when:
1. Its required measurements are supported by the current landmark engine.
2. A readable reference image exists at the configured path.
3. The uploaded and reference feature vectors are compatible.

Missing references and unsupported measurements are reported as unscored; they are not assigned fabricated values. The score transformation and group weights are experimental and have not been scientifically calibrated. The current engine does not support every listed profile-view or visual category.

## API

### `GET /`
Returns service metadata.

### `GET /health`
Returns API status and whether the MediaPipe landmark engine initialized.

### `POST /analyze`
Multipart form field: `file`. Returns overall score (or `null` when no category can be scored), category-level results, image-quality diagnostics, coverage, confidence, and limitations.

## Privacy and responsible use

Facial images and derived measurements are sensitive biometric information. Use images only with informed permission. Avoid uploading images of other people without consent, do not retain images unnecessarily, and provide a deletion process for any reference images you manage. Do not use the output for identity verification, medical decisions, hiring, education, access control, or other consequential decisions.

## Verification status

The API and frontend files are added as a non-destructive feature branch. The repository's build and image-analysis flow still need to be run in a local environment with the declared Python and Node dependencies. No performance or scoring accuracy is claimed until that validation is completed.
