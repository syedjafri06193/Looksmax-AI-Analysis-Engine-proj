import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from app.services.face import MAX_UPLOAD_BYTES, FaceAnalysisError, analyze_image

app = FastAPI(title="LooksMax AI")

# Comma-separated list; defaults to any origin for local development. The API
# uses no cookies, so credentials are never allowed (a wildcard origin with
# credentials is rejected by browsers anyway).
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "LooksMax AI backend running"}


@app.post("/analyze/face")
async def analyze(file: UploadFile = File(...)):
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    try:
        # OpenCV work is CPU-bound; keep it off the event loop.
        return await run_in_threadpool(analyze_image, data)
    except FaceAnalysisError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
