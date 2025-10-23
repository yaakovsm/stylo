from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.recommendation_service import get_recommendations, generate_sdxl_image

router = APIRouter(prefix="/api/recommend")

class RecommendationRequest(BaseModel):
    clothing_item: str
    color: str = ""
    style: list[str] = []
    gender: str = "men"

class ImageRequest(BaseModel):
    prompt: str

@router.post("/")
async def recommend(request: RecommendationRequest):
    try:
        recommendations = get_recommendations(
            request.clothing_item, 
            request.color, 
            request.style,
            request.gender
        )
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def generate_image(request: ImageRequest):
    try:
        image_url = generate_sdxl_image(request.prompt)
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
