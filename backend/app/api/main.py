from fastapi import FastAPI
from app.api import recommend
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS configuration to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(recommend.router)

# Define the request body model
class RecommendationRequest(BaseModel):
    clothing_item: str
    color: str = "" # Optional color field
    style: str = "" # Optional style field

@app.get("/")
def read_root():
    return {"message": "Fashion Stylist Backend is running!"}

@app.get("/api/")
def api_root():
    return {"message": "API root is working!"}