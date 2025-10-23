# backend/app/services/recommendation_service.py
import os
import json
import time
import logging
import asyncio
from typing import List, Optional, AsyncGenerator
from fastapi import HTTPException
from openai import AsyncOpenAI, OpenAI
import replicate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment (only for local dev, not for production)
if os.getenv("ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

# Initialize OpenAI clients
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sync_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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


# ========== FASHION RECOMMENDATION (OpenAI) ==========
async def get_recommendations(
    clothing_item: str,
    color: str = "",
    style: Optional[List[str]] = None,
    gender: str = "men",
) -> dict:
    """
    Generate style recommendations, color palette, and outfit prompts using OpenAI.
    Returns structured JSON containing:
    - color_palette
    - style_inspirations  
    - outfits
    """
    style = style or []
    primary_item_description = f"{color} {clothing_item}".strip()

    if not style:
        style_instruction = (
            f"Generate 3 distinct style inspirations and their corresponding image prompts. "
            f"These styles should be common complementary styles for {gender}'s {primary_item_description}."
        )
        style_list_for_prompt = ""
    else:
        style_instruction = (
            f"Generate 3 distinct style inspirations and their corresponding image prompts, "
            f"strictly adhering to: {', '.join(style)}. "
            f"If you cannot generate 3, include additional common complementary styles."
        )
        style_list_for_prompt = f" and the following styles: {', '.join(style)}"

    prompt = f"""
You are a highly skilled fashion stylist AI specializing in {gender}'s fashion.
Given a primary clothing item (already described with color if provided){style_list_for_prompt}, generate:

1. A color palette (5 colors, name + hex).
   - First color MUST match the provided primary item color if available.

2. {style_instruction}

3. Three outfit recommendations that *complement* the primary clothing item.
   Each outfit includes:
   - top
   - pants  
   - shoes
   - a descriptive image_prompt (full-body fashion photo).

RULES:
- Color palette MUST prioritize the input color if given.
- Outfit parts must match color palette and adhere to provided styles.
- Full-body photo, realistic, editorial fashion photography.
- Respond ONLY in JSON with this structure:
{{
  "color_palette": [{{"name": "Beige", "hex": "#F5F5DC"}}, ...],
  "style_inspirations": [
    {{"description": "...", "main_image_prompt": "..."}},
    ...
  ],
  "outfits": [
    {{"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."}},
    ...
  ]
}}

Primary clothing item: {primary_item_description}
"""

    try:
        logger.info(f"Generating recommendations for: {primary_item_description}")
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a skilled fashion stylist AI for {gender}'s fashion. "
                        "Always return structured JSON, no extra text."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        start, end = content.find("{"), content.rfind("}") + 1
        json_str = content[start:end]
        data = json.loads(json_str)

        # Enhance prompts for image generation consistency
        for i, outfit in enumerate(data.get("outfits", [])):
            style_desc = data["style_inspirations"][i % len(data["style_inspirations"])]["description"]
            outfit_parts = [part for part in [outfit.get("top"), outfit.get("pants"), outfit.get("shoes")] 
                          if part and part != "N/A (complete dress look)"]
            outfit_text = ", ".join(outfit_parts)
            data["outfits"][i]["image_prompt"] = (
                f"Full body fashion photo of a {gender} wearing: {outfit_text}. "
                f"Primary item: {primary_item_description}. "
                f"Exact color and garment match required. Style: {style_desc.lower()}. "
                f"Clean background, editorial lighting, shoes visible."
            )

        for i, style_insp in enumerate(data.get("style_inspirations", [])):
            desc = style_insp["description"]
            data["style_inspirations"][i]["main_image_prompt"] = (
                f"Full body fashion photo of a {gender} in {desc}. "
                f"Include the {primary_item_description}. "
                f"Studio or street lighting, sharp focus, clean background."
            )

        return data

    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        color_name = color.capitalize() or "Red"
        fallback_styles = style or ["Casual", "Elegant", "Sporty"]
        fallback_style_inspirations = [
            {
                "description": f"{s} style for {gender}'s {primary_item_description}",
                "main_image_prompt": (
                    f"Full body fashion photo of {gender} wearing a {primary_item_description} "
                    f"in a {s} style, clean background, editorial lighting"
                ),
            }
            for s in fallback_styles[:3]
        ]
        return {
            "color_palette": [
                {"name": color_name, "hex": "#FF0000"},
                {"name": "White", "hex": "#FFFFFF"},
                {"name": "Black", "hex": "#000000"},
                {"name": "Gray", "hex": "#808080"},
                {"name": "Navy", "hex": "#000080"},
            ],
            "style_inspirations": fallback_style_inspirations,
            "outfits": [
                {"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."}
                for _ in range(3)
            ],
        }


# ========== IMAGE GENERATION (Replicate / SDXL) ==========
async def generate_sdxl_image(prompt: str) -> str:
    """
    Generate a fashion image using Stable Diffusion XL via Replicate.
    Returns the URL of the generated image.
    """
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not set")

    model_candidates = [
        os.getenv("REPLICATE_MODEL") or "stability-ai/sdxl",
        "stability-ai/stable-diffusion-xl-base-1.0",
    ]
    max_retries, delay = 3, 3
    prompt = prompt.strip()[:4000]
    enhanced_prompt = (
        f"{prompt}. Full body, head to toe visible, standing pose, centered subject. "
        f"Professional studio lighting, neutral background, editorial fashion photo. "
        f"Do not alter specified garments or colors."
    )
    negative_prompt = (
        "cropped, out of frame, missing feet, cut off legs, lowres, blurry, "
        "wrong color, mismatched outfit, text, watermark, logo"
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        for model_slug in model_candidates:
            try:
                output = await asyncio.to_thread(
                    replicate.run,
                    model_slug,
                    input={
                        "prompt": enhanced_prompt,
                        "width": 768,
                        "height": 1344,
                        "num_inference_steps": 40,
                        "guidance_scale": 9.0,
                        "negative_prompt": negative_prompt,
                    },
                    timeout=120,
                )
                urls = list(output) if output else []
                if not urls:
                    raise ValueError("No image URL returned")
                logger.info(f"✅ Image generated via {model_slug}")
                return urls[0]
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed for {model_slug}: {e}")
                last_error = e
                continue
        if attempt < max_retries:
            await asyncio.sleep(delay * attempt)

    raise HTTPException(
        status_code=500,
        detail=f"Image generation failed after {max_retries} retries. Last error: {last_error}",
    )
