# API reference

Base URL: `http://<host>:8000`. Interactive docs are served at `/docs`.

## `GET /`

Health check. `{"status": "LooksMax AI backend running"}`

## `POST /analyze/face`

Multipart form with one field, `file` (an image, at most 10 MB).

**200**

```json
{
  "face_shape": "oval",
  "symmetry": 0.87,
  "face_box": {"x": 212, "y": 140, "width": 260, "height": 312},
  "recommendations": ["...", "..."],
  "disclaimer": "Heuristic estimate from a single photo; ..."
}
```

| Field | Meaning |
|---|---|
| `face_shape` | `oval`, `round`, `square` or `long` |
| `symmetry` | 0–1; 1 is perfectly mirror-symmetric |
| `face_box` | Detected face in image pixels |
| `recommendations` | Suggestions for the face shape |
| `disclaimer` | Always present |

**422** — `{"detail": "..."}` when the upload is empty, larger than 10 MB, not
a decodable image, or contains no detectable face.

`jawline_strength`, returned as a constant by the first version, was removed
because nothing measured it.
