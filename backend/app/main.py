import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.plants import router as plants_router
from app.services.diagnosis_registry import UPLOAD_DIR

app = FastAPI(
    title="AgriSphere AI",
    description=(
        "Autonomous Plant Intelligence and "
        "Smart Greenhouse Simulation System"
    ),
    version="3.0.0",
)

# Set FRONTEND_ORIGINS on Render/Vercel deployment, comma-separated.
frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "AgriSphere AI",
        "system": "Autonomous Plant Intelligence",
        "status": "online",
        "version": "3.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "backend": "running"}


app.include_router(plants_router)

# Uploaded plant images are served from this directory.
app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads",
)
