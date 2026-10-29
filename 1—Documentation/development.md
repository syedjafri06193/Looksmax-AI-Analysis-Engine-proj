# Development

## Configuration

| Variable | Where | Default | Purpose |
|---|---|---|---|
| `CORS_ORIGINS` | backend | `*` | Comma-separated allowed origins (the API sends no cookies) |
| `EXPO_PUBLIC_API_URL` | app | `http://localhost:8000` | Backend URL as reachable from the phone |

## Tests

```bash
cd backend && pytest
cd frontend && npx tsc --noEmit
```

The backend tests cover face-shape thresholds, the symmetry score, decoding
errors, the 422 paths (garbage upload, no face, oversized upload) and the
success response shape. CI (`.github/workflows/ci.yml`) runs them on Python
3.10–3.12 and type-checks the app.

## Known limitations

- Face shape comes from the detector's bounding box, which is a rough proxy.
  A landmark model (MediaPipe Face Mesh, dlib) would give a jawline and
  cheekbone width to classify on.
- The Haar cascade misses faces that are turned, tilted or poorly lit.
- Expo SDK 50 is several releases old; `npm audit` reports advisories in its
  dependency tree that need an SDK upgrade to clear.
