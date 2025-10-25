from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging

from app.services.recommendation_service import (
    get_recommendations,
    generate_sdxl_image,
    stream_recommendations,
)

# ====== Setup ======
router = APIRouter(prefix="/ai", tags=["AI Fashion"])
logger = logging.getLogger(__name__)

# ====== Schemas ======
class RecommendationRequest(BaseModel):
    clothing_item: str
    color: Optional[str] = ""
    style: Optional[List[str]] = []
    gender: Optional[str] = "men"


class ImageRequest(BaseModel):
    prompt: str


# ====== Endpoints ======

@router.post("/recommendations")
async def create_recommendations(payload: RecommendationRequest):
    """
    Generate complete fashion recommendations (non-streaming).
    """
    try:
        logger.info(
            f"Generating recommendations for {payload.gender}'s "
            f"{payload.color} {payload.clothing_item} | styles: {payload.style}"
        )
        result = await get_recommendations(
            clothing_item=payload.clothing_item,
            color=payload.color,
            style=payload.style,
            gender=payload.gender,
        )
        return JSONResponse(content=result)
    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        raise e
    except Exception as e:
        logger.exception("Unexpected error while generating recommendations")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/stream")
async def stream_recommendations_endpoint(payload: RecommendationRequest):
    """
    Stream OpenAI response token-by-token.
    Used for live typing effect or real-time display on frontend.
    """
    logger.info(f"Streaming recommendations for {payload.clothing_item}")

    async def event_generator():
        try:
            async for chunk in stream_recommendations(
                clothing_item=payload.clothing_item,
                color=payload.color,
                style=payload.style,
                gender=payload.gender,
            ):
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.02)
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/generate-image")
async def generate_image(payload: ImageRequest):
    """
    Generate a high-quality fashion image using Replicate (SDXL or Flux).
    """
    try:
        logger.info(f"Generating image for prompt: {payload.prompt[:80]}...")
        image_url = await generate_sdxl_image(payload.prompt)
        return {"image_url": image_url}

    except HTTPException as e:
        logger.error(f"Image generation HTTP error: {e.detail}")
        raise e

    except asyncio.TimeoutError:
        logger.warning("Replicate request timed out.")
        raise HTTPException(status_code=504, detail="Image generation timed out")

    except Exception as e:
        logger.exception("Unexpected image generation error")
        raise HTTPException(status_code=500, detail=str(e))
