# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai
import os

app = FastAPI(
    title="Stylo API",
    description="AI Fashion Assistant Backend (async)",
    version="2.0.0",
)

# ===== CORS =====
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://stylo-frontend.onrender.com")


allowed_origins = [
    FRONTEND_URL,
    FRONTEND_URL.rstrip("/"),
    FRONTEND_URL + "/",
    "https://stylo-frontend.onrender.com",
    "https://stylo-frontend.onrender.com/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Routers =====
app.include_router(ai.router)

# ===== Health Checks =====
@app.get("/")
async def root():
    return {"message": "Stylo API is live!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
