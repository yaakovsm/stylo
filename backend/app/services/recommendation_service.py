import os
import json
import time
import logging
import asyncio
from typing import List, Optional, AsyncGenerator
from fastapi import HTTPException
from openai import AsyncOpenAI, OpenAI
import replicate

# ========== CONFIGURATION ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment (only for local dev)
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
    """Stream OpenAI response token-by-token in real time."""
    style = style or []
    primary_item_description = f"{color} {clothing_item}".strip()

    style_instruction = (
        f"Generate 3 distinct style inspirations strictly following: {', '.join(style)}."
        if style else f"Generate 3 distinct style inspirations for {gender}'s {primary_item_description}."
    )

    prompt = f"""
You are a skilled AI fashion stylist for {gender}'s fashion.
Given a primary clothing item (including color if specified),
generate color palette, style inspirations, and outfit recommendations.
Respond in structured JSON format.
Primary clothing item: {primary_item_description}
"""

    try:
        logger.info(f"Streaming response for: {primary_item_description}")
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


# ========== MAIN RECOMMENDATION GENERATOR ==========
async def get_recommendations(
    clothing_item: str,
    color: str = "",
    style: Optional[List[str]] = None,
    gender: str = "men",
) -> dict:
    """
    Generate fashion style recommendations, color palette, and outfit prompts.
    """
    style = style or []
    primary_item_description = f"{color} {clothing_item}".strip()

    if not style:
        style_instruction = (
            f"Generate 3 distinct style inspirations and their corresponding image prompts. "
            f"These styles should be common complementary styles for {gender}'s {primary_item_description}."
        )
    else:
        style_instruction = (
            f"Generate 3 distinct style inspirations and their corresponding image prompts, "
            f"strictly adhering to: {', '.join(style)}. "
            f"If you cannot generate 3, include additional common complementary styles."
        )

    prompt = f"""
You are a highly skilled fashion stylist AI specializing in {gender}'s fashion.
Given a primary clothing item (already described with color if provided), generate:

1. A color palette (5 colors, name + hex).
   - First color MUST match the provided primary item color if available.
2. {style_instruction}
3. Three outfit recommendations that complement the primary clothing item.
Each outfit includes:
- top
- pants
- shoes
- a descriptive image_prompt (full-body fashion photo).

RULES:
- Color palette MUST prioritize the input color if given.
- Outfit parts must match color palette and adhere to provided styles.
- Full-body photo, realistic, editorial fashion photography.
- Respond ONLY in JSON format.
Primary clothing item: {primary_item_description}
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a professional fashion stylist AI for {gender}'s fashion."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        start, end = content.find("{"), content.rfind("}") + 1
        json_str = content[start:end]
        data = json.loads(json_str)

        # Add improved image prompts
        for i, outfit in enumerate(data.get("outfits", [])):
            style_desc = data["style_inspirations"][i % len(data["style_inspirations"])]["description"]
            parts = [p for p in [outfit.get("top"), outfit.get("pants"), outfit.get("shoes")] if p]
            outfit_text = ", ".join(parts)
            data["outfits"][i]["image_prompt"] = (
                f"Full body fashion photo of a {gender} wearing: {outfit_text}. "
                f"Primary item: {primary_item_description}. "
                f"Style: {style_desc.lower()}. "
                f"Editorial lighting, clean background, sharp focus."
            )

        for i, style_insp in enumerate(data.get("style_inspirations", [])):
            desc = style_insp["description"]
            data["style_inspirations"][i]["main_image_prompt"] = (
                f"Full body fashion photo of a {gender} in {desc}. "
                f"Include the {primary_item_description}. Clean background, professional lighting."
            )

        return data

    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        fallback_styles = style or ["Casual", "Elegant", "Sporty"]
        return {
            "color_palette": [
                {"name": color.capitalize() or "Red", "hex": "#FF0000"},
                {"name": "White", "hex": "#FFFFFF"},
                {"name": "Black", "hex": "#000000"},
                {"name": "Gray", "hex": "#808080"},
                {"name": "Navy", "hex": "#000080"},
            ],
            "style_inspirations": [
                {"description": f"{s} style for {gender}'s {primary_item_description}", "main_image_prompt": ""}
                for s in fallback_styles[:3]
            ],
            "outfits": [
                {"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."} for _ in range(3)
            ],
        }


# ========== IMAGE GENERATION (Replicate with smart fallback) ==========
async def generate_sdxl_image(prompt: str) -> str:
    """
    Generate a fashion image using Stable Diffusion XL or Flux via Replicate.
    Automatically adjusts parameters per model and retries with fallback if needed.
    """
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not set")

    model_candidates = [
        os.getenv("REPLICATE_MODEL") or "stability-ai/stable-diffusion-xl-base-1.0",
        "black-forest-labs/flux-schnell",
    ]

    max_retries, delay = 3, 3
    prompt = prompt.strip()[:4000]
    enhanced_prompt = (
        f"{prompt}. Full body, head to toe visible, centered subject, professional studio lighting, "
        f"neutral background, editorial fashion photo. Do not alter specified garments or colors."
    )
    negative_prompt = (
        "cropped, out of frame, missing feet, cut off legs, lowres, blurry, "
        "wrong color, mismatched outfit, text, watermark, logo"
    )

    last_error = None

    for attempt in range(1, max_retries + 1):
        for model_slug in model_candidates:
            try:
                if "flux" in model_slug:
                    input_params = {
                        "prompt": enhanced_prompt,
                        "num_inference_steps": 4,
                        "guidance_scale": 1.0,
                    }
                else:
                    input_params = {
                        "prompt": enhanced_prompt,
                        "width": 768,
                        "height": 1344,
                        "num_inference_steps": 40,
                        "guidance_scale": 9.0,
                        "negative_prompt": negative_prompt,
                    }

                output = await asyncio.to_thread(
                    replicate.run,
                    model_slug,
                    input=input_params,
                    timeout=120,
                )

                urls = list(output) if output else []
                if urls:
                    logger.info(f"Image generated successfully via {model_slug}")
                    return urls[0]
                else:
                    raise ValueError("No image URL returned")

            except Exception as e:
                logger.warning(f"Attempt {attempt} failed for {model_slug}: {e}")
                last_error = e
                continue

        if attempt < max_retries:
            await asyncio.sleep(delay * attempt)

    logger.error(f"All attempts failed. Last error: {last_error}")
    raise HTTPException(
        status_code=500,
        detail=f"Image generation failed after {max_retries} retries. Last error: {last_error}",
    )
