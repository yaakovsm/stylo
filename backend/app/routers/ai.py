# backend/app/routers/ai.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from app.services.recommendation_service import (
    get_recommendations,
    generate_sdxl_image,
    stream_recommendations,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Fashion"],
)


class RecommendationRequest(BaseModel):
    clothing_item: str
    color: Optional[str] = ""
    style: Optional[List[str]] = []
    gender: Optional[str] = "men"


class ImageRequest(BaseModel):
    prompt: str


# ======== NORMAL (non-stream) ==========
@router.post("/recommendations")
async def create_recommendations(payload: RecommendationRequest):
    try:
        result = await get_recommendations(
            clothing_item=payload.clothing_item,
            color=payload.color,
            style=payload.style,
            gender=payload.gender,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======== STREAMING ENDPOINT ==========
@router.post("/recommendations/stream")
async def stream_recommendations_endpoint(payload: RecommendationRequest):
    """
    Stream OpenAI response in real-time.
    """

    async def event_generator():
        async for chunk in stream_recommendations(
            clothing_item=payload.clothing_item,
            color=payload.color,
            style=payload.style,
            gender=payload.gender,
        ):
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ======== IMAGE GENERATION ==========
@router.post("/generate-image")
async def generate_image(payload: ImageRequest):
    try:
        image_url = await generate_sdxl_image(payload.prompt)
        return {"image_url": image_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
