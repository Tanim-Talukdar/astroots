
from fastapi import FastAPI

from app.api.plants import router as plants_router

app = FastAPI(
    title="AgriSphere AI",
    description=(
        "Autonomous Plant Intelligence and "
        "Smart Greenhouse Simulation System"
    ),
    version="2.0.0"
)


@app.get("/")
def home():
    return {
        "project": "AgriSphere AI",
        "system": "Autonomous Plant Intelligence",
        "status": "online",
        "version": "2.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "backend": "running"
    }


app.include_router(plants_router)
