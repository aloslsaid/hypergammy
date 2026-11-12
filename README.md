# Hypergammy

Hypergammy is a face-landmark analysis experiment. Its current repository combines a React/TypeScript interface with a Python analysis engine. The Python engine extracts normalized facial measurements using OpenCV and, when available, MediaPipe. These measurements are experimental and are not a medical, identity, or attractiveness assessment.

## Repository contents

The root currently includes `App.tsx`, `main.tsx`, `styles.css`, `engine.py`, JSON scoring/category/weight data, and `requirements.txt`. It does not currently include the conventional Vite `package.json`/TypeScript configuration or the documented `app/main.py` API entry point. As a result, the previous `uvicorn app.main:app` instructions do not match the visible root layout and should not be relied on as a working launch command.

## Setup and current limitations

- Python: use a virtual environment and install the listed backend dependencies with `python -m pip install -r requirements.txt`.
- Frontend/API startup: no verified command is provided because the expected frontend package manifest and documented API entry point are absent from the root file list.
- Tests: no test files or verified test command are currently present in the root.

Before contributing, inspect the existing files and determine the intended API/UI integration. Do not create reference images or scores by guessing; the engine's output depends on actual supported inputs and reference data.

## Privacy and responsible use

Facial images and derived measurements are sensitive personal data. Use images only with informed permission, minimize retention, and explain how data is handled. The measurements and comparisons are experimental, can be affected by image quality and bias, and must not be used to make consequential decisions about people.
