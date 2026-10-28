"""Face analysis.

Detects the most prominent frontal face with OpenCV's bundled Haar cascade,
then derives two simple, explainable measurements from it:

* **face shape** — a heuristic from the face box's height/width ratio;
* **symmetry** — normalised correlation between the left half of the face
  and the mirrored right half (1.0 = perfectly symmetric).

These are coarse heuristics, not a medical or aesthetic assessment, and the
API says so in every response.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

RECOMMENDATIONS = {
    "oval": [
        "Most haircuts suit an oval face; a textured crop or side part works well",
        "Keep facial hair even and short to preserve balanced proportions",
    ],
    "round": [
        "Add height on top (quiff, pompadour) to lengthen the face",
        "A short boxed beard adds angles along the jaw",
    ],
    "long": [
        "Keep volume at the sides rather than on top",
        "Fuller sideburns or a beard on the cheeks shortens the face visually",
    ],
    "square": [
        "Softer, textured styles balance a strong jaw",
        "A short, rounded beard softens the jawline",
    ],
}
GENERAL = ["Good posture and neck alignment change how the jawline photographs"]
DISCLAIMER = ("Heuristic estimate from a single photo; not a medical or "
              "professional aesthetic assessment.")


class FaceAnalysisError(ValueError):
    """The upload could not be analysed (bad image or no face)."""


@dataclass(frozen=True)
class FaceBox:
    x: int
    y: int
    w: int
    h: int


def decode_image(data: bytes) -> np.ndarray:
    if not data:
        raise FaceAnalysisError("empty upload")
    if len(data) > MAX_UPLOAD_BYTES:
        raise FaceAnalysisError("image larger than 10 MB")
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise FaceAnalysisError("not a decodable image (JPEG, PNG, WebP, ...)")
    return img


def detect_face(gray: np.ndarray) -> FaceBox:
    min_side = max(48, min(gray.shape[:2]) // 8)
    faces = _CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                      minSize=(min_side, min_side))
    if len(faces) == 0:
        raise FaceAnalysisError("no face found; use a well-lit, front-facing photo")
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return FaceBox(int(x), int(y), int(w), int(h))


def face_shape(box: FaceBox) -> str:
    """Classify by height/width ratio of the detected face box."""
    ratio = box.h / box.w
    if ratio >= 1.35:
        return "long"
    if ratio <= 1.05:
        return "round" if ratio < 0.98 else "square"
    return "oval"


def symmetry_score(face_gray: np.ndarray) -> float:
    """Normalised cross-correlation of the left half with the mirrored right
    half, mapped to [0, 1]."""
    face = cv2.equalizeHist(face_gray)
    w = face.shape[1] - (face.shape[1] % 2)
    left = face[:, : w // 2].astype(np.float64)
    right = np.fliplr(face[:, w // 2 : w]).astype(np.float64)
    left -= left.mean()
    right -= right.mean()
    denom = np.sqrt((left ** 2).sum() * (right ** 2).sum())
    if denom == 0:
        return 1.0
    corr = float((left * right).sum() / denom)
    return round(max(0.0, min(1.0, (corr + 1) / 2)), 2)


def analyze_image(data: bytes) -> dict:
    img = decode_image(data)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    box = detect_face(gray)
    shape = face_shape(box)
    face = gray[box.y : box.y + box.h, box.x : box.x + box.w]
    return {
        "face_shape": shape,
        "symmetry": symmetry_score(face),
        "face_box": {"x": box.x, "y": box.y, "width": box.w, "height": box.h},
        "recommendations": RECOMMENDATIONS[shape] + GENERAL,
        "disclaimer": DISCLAIMER,
    }
