# backend/app/services/recommendation_service.py
import os
import json
import logging
import asyncio
from typing import List, Optional, AsyncGenerator
from fastapi import HTTPException
from openai import AsyncOpenAI
import replicate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ========== STREAMING RECOMMENDATIONS ==========
async def stream_recommendations(
    clothing_item: str,
    color: str = "",
    style: Optional[List[str]] = None,
    gender: str = "men",
) -> AsyncGenerator[str, None]:
    """
    Stream OpenAI response token-by-token in real time.
    """
    style = style or []
    primary_item_description = f"{color} {clothing_item}".strip()

    if not style:
        style_instruction = f"Generate 3 distinct style inspirations for {gender}'s {primary_item_description}."
        style_list_for_prompt = ""
    else:
        style_instruction = f"Generate 3 distinct style inspirations strictly following: {', '.join(style)}."
        style_list_for_prompt = f" and styles: {', '.join(style)}"

    prompt = f"""
You are a skilled AI fashion stylist for {gender}'s fashion.
Given a primary clothing item (including color if specified){style_list_for_prompt},
generate color palette, style inspirations, and outfit recommendations.
Respond in structured JSON format.
Primary clothing item: {primary_item_description}
"""

    try:
        logger.info(f"🔹 Streaming response for: {primary_item_description}")

        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert AI fashion stylist that responds only in JSON."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield json.dumps({"error": str(e)})


# ========== OTHER EXISTING FUNCTIONS (unchanged) ==========
# get_recommendations(), generate_sdxl_image() stay the same as before
