import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import face
from app.services.face import FaceAnalysisError, FaceBox

client = TestClient(app)


def _png(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return buf.tobytes()


def test_root():
    assert client.get("/").json()["status"].startswith("LooksMax")


@pytest.mark.parametrize("w,h,shape", [(100, 150, "long"), (100, 120, "oval"),
                                       (100, 100, "square"), (100, 90, "round")])
def test_face_shape(w, h, shape):
    assert face.face_shape(FaceBox(0, 0, w, h)) == shape


def test_symmetry_is_one_for_a_mirrored_image():
    rng = np.random.default_rng(0)
    half = rng.integers(0, 255, (64, 32), dtype=np.uint8)
    sym = np.hstack([half, np.fliplr(half)])
    assert face.symmetry_score(sym) == 1.0


def test_symmetry_is_lower_for_an_asymmetric_image():
    rng = np.random.default_rng(1)
    img = rng.integers(0, 255, (64, 64), dtype=np.uint8)
    assert face.symmetry_score(img) < 0.8


def test_decode_rejects_garbage_and_empty():
    with pytest.raises(FaceAnalysisError):
        face.decode_image(b"")
    with pytest.raises(FaceAnalysisError):
        face.decode_image(b"definitely not an image")


def test_api_rejects_non_image_with_422():
    # The original code crashed with AttributeError (HTTP 500) here.
    r = client.post("/analyze/face", files={"file": ("x.jpg", b"nope", "image/jpeg")})
    assert r.status_code == 422
    assert "decodable" in r.json()["detail"]


def test_api_reports_no_face_with_422():
    blank = np.full((200, 200, 3), 127, np.uint8)
    r = client.post("/analyze/face", files={"file": ("x.png", _png(blank), "image/png")})
    assert r.status_code == 422
    assert "no face" in r.json()["detail"]


def test_api_success_shape(monkeypatch):
    monkeypatch.setattr(face, "detect_face", lambda gray: FaceBox(50, 40, 100, 125))
    rng = np.random.default_rng(2)
    img = rng.integers(0, 255, (240, 200, 3), dtype=np.uint8)
    r = client.post("/analyze/face", files={"file": ("x.png", _png(img), "image/png")})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["face_shape"] == "oval"
    assert 0.0 <= body["symmetry"] <= 1.0
    assert body["recommendations"] and body["disclaimer"]
    assert body["face_box"] == {"x": 50, "y": 40, "width": 100, "height": 125}


def test_api_rejects_oversized_upload():
    big = b"\xff" * (face.MAX_UPLOAD_BYTES + 10)
    r = client.post("/analyze/face", files={"file": ("x.jpg", big, "image/jpeg")})
    assert r.status_code == 422
