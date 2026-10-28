# LooksMax AI

[![CI](https://github.com/syedjafri06193/looksmax-ai-/actions/workflows/ci.yml/badge.svg)](https://github.com/syedjafri06193/looksmax-ai-/actions/workflows/ci.yml)

A mobile app that analyses a face photo and suggests grooming and styling
changes. An Expo (React Native) client uploads a photo to a FastAPI backend,
which detects the face with OpenCV and returns a face-shape estimate, a
symmetry score and recommendations for that face shape.

> Results are heuristics from a single photo — a face-box ratio and a
> left/right correlation — not a medical or professional assessment. Every
> response carries that disclaimer.

## Quick start

**Backend** (Python 3.10+):

```bash
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest                                   # 12 tests
```

**App** (Node 18+, Expo Go on a phone or an emulator):

```bash
cd frontend
npm ci
EXPO_PUBLIC_API_URL=http://<your-computer's-LAN-IP>:8000 npx expo start
```

`localhost` inside the app means the phone itself, so point
`EXPO_PUBLIC_API_URL` at the machine running the backend.

## Repository layout

```
.
├── 1—Documentation/   architecture, API reference, development notes
├── backend/
│   ├── app/main.py            FastAPI app (CORS, upload endpoint)
│   ├── app/services/face.py   decoding, face detection, shape + symmetry
│   └── tests/                 pytest suite
└── frontend/
    ├── App.tsx                pick a photo, upload, show results
    └── app.json               Expo config (photo-library permission text)
```

## Documentation

All documentation lives in [`1—Documentation/`](1—Documentation/README.md).
