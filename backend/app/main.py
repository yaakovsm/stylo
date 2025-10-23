# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai

app = FastAPI(
    title="Stylo API",
    description="AI Fashion Assistant Backend (async)",
    version="2.0.0",
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain in production
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
