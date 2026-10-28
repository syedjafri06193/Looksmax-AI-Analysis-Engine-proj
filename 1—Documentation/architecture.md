# Architecture

```
Expo app (frontend/App.tsx)
   │  POST /analyze/face  (multipart: file)
   ▼
FastAPI (backend/app/main.py)
   │  reads at most 10 MB, runs the analysis in a worker thread
   ▼
app/services/face.py
   decode ─► grayscale ─► Haar-cascade face detection ─► largest face box
                                   │
                    ┌──────────────┴──────────────┐
             face shape (h/w ratio)       symmetry (left half vs mirrored right)
                    └──────────────┬──────────────┘
                     recommendations for the shape + disclaimer
```

## Analysis

| Step | How | Notes |
|---|---|---|
| Decode | `cv2.imdecode` | JPEG, PNG, WebP, …; anything else is a 422 |
| Detect | OpenCV's bundled `haarcascade_frontalface_default.xml` | Largest frontal face wins; minimum size scales with the image |
| Face shape | Height ÷ width of the face box: ≥ 1.35 long, ≤ 0.98 round, ≤ 1.05 square, otherwise oval | A coarse proxy — the detector's box is not a jawline trace |
| Symmetry | Histogram-equalised face; normalised cross-correlation of the left half with the mirrored right half, mapped to 0–1 | Lighting and head tilt lower the score as much as anatomy does |
| Recommendations | Fixed suggestions per face shape, plus a general one | Edit `RECOMMENDATIONS` in `face.py` |

OpenCV is pinned below 5.0 because OpenCV 5 removes the Haar cascade
classifier.

## Privacy

Uploaded images are processed in memory and never written to disk or logged.
