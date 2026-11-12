# INFINITY Backend

## Requirements
Use Python 3.10 or 3.11. MediaPipe wheels may not be available for every Python version/platform.

## Windows setup
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

## References
Each category needs its own reference image. The UI/backend do not invent references. Add a JPG using:
`PUT /references/{category_id}` with multipart field `file`, or place `reference.jpg` and `metadata.json` in `reference_images/{category_id}/`.

Only use images you own or have permission to use. The current comparison is experimental and not scientifically calibrated.

## Tests
```powershell
$env:PYTHONPATH="."
pytest -q
```

The API returns no score when a reference is missing or the required feature is not supported.
