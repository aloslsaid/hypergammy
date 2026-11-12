from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_and_health_are_available():
    assert client.get("/").status_code == 200
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rejects_unsupported_file_extension():
    response = client.post(
        "/analyze",
        files={"file": ("payload.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_rejects_empty_image_upload():
    response = client.post(
        "/analyze",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400


def test_rejects_upload_over_ten_megabytes():
    response = client.post(
        "/analyze",
        files={"file": ("large.jpg", b"x" * (10 * 1024 * 1024 + 1), "image/jpeg")},
    )
    assert response.status_code == 413
