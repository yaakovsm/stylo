import os
import openai
from dotenv import load_dotenv
from fastapi import HTTPException
import time
import replicate

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_recommendations(clothing_item: str, color: str = "", style: list[str] = None, gender: str = "men"):
    if style is None:
        style = []

    # Construct a more detailed description for the AI based on user input
    # Always include color in the detailed_clothing_description if provided
    if color:
        primary_item_description = f"{color} {clothing_item}"
    else:
        primary_item_description = clothing_item
    
    # If no styles provided, ask AI to pick 3 random ones
    if not style:
        style_instruction = f"Generate 3 distinct style inspirations and their corresponding image prompts. These styles should be common complementary styles for {gender}'s {primary_item_description}."
        style_list_for_prompt = ""
    else:
        style_instruction = f"Generate 3 distinct style inspirations and their corresponding image prompts, strictly adhering to the following styles: {', '.join(style)}. If you cannot generate 3 from the provided styles, generate additional common complementary styles for {gender}'s fashion."
        style_list_for_prompt = f" and the following styles: {', '.join(style)}"

    prompt = f"""
You are a highly skilled fashion stylist AI specializing in {gender}'s fashion. Given a primary clothing item (which is already described with its color if provided){style_list_for_prompt}, generate:
1. A color palette (5 colors, each with a name and hex code) that perfectly matches or complements the given primary clothing item. **The first color in the palette MUST be the specified color of the primary item if provided.**
2. {style_instruction}
3. Three distinct outfit recommendations that *complement* the provided primary clothing item, generally adhering to the style inspirations you generated or the styles provided. For each outfit, provide:
   - Top (e.g., a shirt, sweater, or blazer. If the input primary item is a top, use the input primary item itself as the 'top' here, ensuring its color is exactly as specified or a complementary color from the generated palette.)
   - Pants (e.g., jeans, trousers, shorts. If the input primary item is a bottom, use the input primary item itself as the 'pants' here, ensuring its color is exactly as specified or a complementary color from the generated palette.)
   - Shoes (e.g., sneakers, loafers, boots. If the input primary item is footwear, use the input primary item itself as the 'shoes' here, ensuring its color is exactly as specified or a complementary color from the generated palette.)

RULES:
- The color palette MUST prioritize and prominently feature the exact color of the primary item if specified. Otherwise, derive colors from the primary item implicitly.
- All generated style inspirations, main image prompts, and outfit recommendations MUST strictly align with the provided styles if specified. If no styles are given, suggest common complementary styles for {gender}'s fashion.
- If the primary item is a top (e.g., shirt, hoodie, sweater, blazer), the 'top' in the recommendation should be the original primary item. Recommend complementary pants and shoes, ensuring their colors match the color palette.
- If the primary item is pants/jeans/shorts/skirt, the 'pants' in the recommendation should be the original primary item. Recommend a complementary top and shoes, ensuring their colors match the color palette.
- If the primary item is footwear (e.g., sneakers, loafers, boots), the 'shoes' in the recommendation should be the original primary item. Recommend a complementary top and pants, ensuring their colors match the color palette.
- If the primary item is a dress, only recommend shoes, and set pants and top to "N/A (complete dress look)".
- The recommended items (top, pants, shoes) should complement the input primary item in style and color, strongly adhering to the generated color palette and the overall style inspirations.
- Each main image prompt should encompass one of the generated style inspirations, the primary clothing item (explicitly mentioning its color if provided), and clearly state that it's a full body fashion photo of a {gender} wearing ONLY that item.
- Each main image prompt for an outfit should clearly state that it's a full body fashion photo of a {gender} wearing the recommended top, pants, and shoes, along with the primary clothing item (if applicable), and one of the generated style inspirations. For example: "Full body fashion photo of a {gender} wearing a [recommended_top], [recommended_pants], and [recommended_shoes] in a [style_inspiration] style, with a [primary_clothing_item] in [color]."
- All recommendations should be appropriate for {gender}'s fashion and body type.

Respond in JSON format like this:
{{
  "color_palette": [{{"name": "Beige", "hex": "#F5F5DC"}}, ...],
  "style_inspirations": [
    {{"description": "...", "main_image_prompt": "..."}},
    {{"description": "...", "main_image_prompt": "..."}},
    {{"description": "...", "main_image_prompt": "..."}}
  ],
  "outfits": [
    {{"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."}},
    {{"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."}},
    {{"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."}}
  ]
}}

Primary clothing item: {primary_item_description}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a highly skilled fashion stylist AI specializing in {gender}'s fashion that generates fashion recommendations, style inspiration, and image prompts based on user input, strictly adhering to specified colors and styles. Always prioritize the user's specified color in the color palette and ensure style inspirations, image prompts, and outfit recommendations are consistent with the chosen styles and appropriate for {gender}'s fashion."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        import json
        content = response.choices[0].message.content
        # Try to extract JSON from the response
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        data = json.loads(json_str)
        # Ensure each outfit has an image_prompt that details the full outfit and enforces exact items/colors
        for i, outfit in enumerate(data["outfits"]):
            style_desc = data["style_inspirations"][i % len(data["style_inspirations"])]["description"]
            # Construct a detailed image prompt for the outfit
            outfit_parts = []
            if outfit["top"] and outfit["top"] != 'N/A (complete dress look)':
                outfit_parts.append(outfit["top"])
            if outfit["pants"] and outfit["pants"] != 'N/A (complete dress look)':
                outfit_parts.append(outfit["pants"])
            if outfit["shoes"]:
                outfit_parts.append(outfit["shoes"])
            
            outfit_description_for_prompt = ", ".join(outfit_parts)

            data["outfits"][i]["image_prompt"] = (
                f"Full body fashion photo of a {gender} wearing: {outfit_description_for_prompt}. "
                f"Primary item must be present and prominent: {primary_item_description}. "
                f"Exact match required – no substitutions: Top='{outfit['top']}', Pants='{outfit['pants']}', Shoes='{outfit['shoes']}'. "
                f"Each garment is a solid color (no patterns), with clean edges. Colors must exactly match the descriptions. "
                f"No text, no logos, no graphics on clothing. "
                f"Head to toe visible, shoes clearly visible. The style is {style_desc.lower()}. "
                f"Photorealistic, editorial street style, natural lighting, clean unobtrusive background."
            )
        
        # Ensure main_image_prompt for style_inspirations is also descriptive and enforces full body
        for i, style_insp in enumerate(data["style_inspirations"]):
            data["style_inspirations"][i]["main_image_prompt"] = (
                f"Full body fashion photo of a {gender} showcasing a {style_insp['description']}. "
                f"Include the {primary_item_description}. Head to toe visible, shoes clearly visible. "
                f"Photorealistic, editorial street style, natural lighting, clean background."
            )
        
        return data
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Fallback to placeholder
        color_name = color.capitalize() if color else "Red" # Use specified color name for fallback
        # Fallback for styles
        fallback_styles = style if style else ["Casual", "Elegant", "Sporty"]
        fallback_style_inspirations = []
        fallback_main_image_prompts = []
        for s in fallback_styles[:3]: # Limit to 3 fallback styles
            fallback_style_inspirations.append({"description": f"A versatile and comfortable everyday look with a touch of {s} style for {gender}'s {primary_item_description}.", "main_image_prompt": f"Full body fashion photo of {gender} wearing a {primary_item_description} in a {s} style, urban setting, professional photography, clean background"})

        return {
            "color_palette": [
                {"name": color_name, "hex": "#FF0000"}, # Use specified color for the first entry
                {"name": "White", "hex": "#FFFFFF"},
                {"name": "Black", "hex": "#000000"},
                {"name": "Gray", "hex": "#808080"},
                {"name": "Navy", "hex": "#000080"}
            ],
            "style_inspirations": fallback_style_inspirations if fallback_style_inspirations else [
                {"description": f"A versatile and comfortable everyday style for {gender}.", "main_image_prompt": f"Full body fashion photo of {gender} wearing a {primary_item_description}, casual style, urban setting, professional photography, clean background"},
                {"description": f"An elegant and sophisticated look for {gender}.", "main_image_prompt": f"Full body fashion photo of {gender} wearing a {primary_item_description}, elegant style, urban setting, professional photography, clean background"},
                {"description": f"A sporty and functional ensemble for {gender}.", "main_image_prompt": f"Full body fashion photo of {gender} wearing a {primary_item_description}, sporty style, urban setting, professional photography, clean background"},
            ],
            "outfits": [
                {"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."},
                {"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."},
                {"top": "...", "pants": "...", "shoes": "...", "image_prompt": "..."}
            ]
        }

def generate_sdxl_image(prompt: str) -> str:
    """
    Generate an image using Stable Diffusion XL via Replicate.
    Returns the URL of the generated image.
    """
    if not os.getenv("REPLICATE_API_TOKEN"):
        raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN is not set")

    max_retries = 3
    retry_delay = 2  # seconds

    model_candidates = []
    # Prefer explicitly configured model (including version) if provided
    configured_model = os.getenv("REPLICATE_MODEL")
    if configured_model:
        model_candidates.append(configured_model)
    # Fallback candidates (may require version pinning on Replicate; override with REPLICATE_MODEL if these fail)
    model_candidates.extend([
        "stability-ai/stable-diffusion-xl-base-1.0",
        "stability-ai/sdxl",
    ])

    for attempt in range(max_retries):
        try:
            # SDXL prompts are typically shorter than 8k chars; trim if absurdly long
            if len(prompt) > 4000:
                prompt = prompt[:3997] + "..."

            enhanced_prompt = (
                f"{prompt}. Full body, head to toe, feet and shoes visible, standing pose, subject centered. "
                f"Do not change the specified items or their colors."
            )

            last_error: Exception | None = None
            for model_slug in model_candidates:
                try:
                    # Strong negative prompt to reduce mismatches
                    neg = "cropped, out of frame, missing feet, cut off legs, close-up, zoomed-in, partial body, lowres, blurry, wrong color, color mismatch, different garment than specified, text, watermark, logo"

                    output = replicate.run(
                        model_slug,
                        input={
                            "prompt": enhanced_prompt,
                            # Portrait aspect ratio to include shoes
                            "width": 768,
                            "height": 1344,
                            "num_inference_steps": 40,
                            "guidance_scale": 9.0,
                            "negative_prompt": neg,
                        },
                    )

                    urls = list(output) if output is not None else []
                    if not urls:
                        raise Exception("No image URL returned from SDXL")
                    return urls[0]
                except Exception as model_err:
                    # Keep the error and try next candidate
                    last_error = model_err
                    print(f"Replicate error for model '{model_slug}': {model_err}")
                    continue

            # If all candidates failed, raise last error
            if last_error:
                raise last_error

        except Exception as e:
            print(f"SDXL error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                hint = (
                    "Consider setting REPLICATE_MODEL to an exact model version, e.g. "
                    "'stability-ai/sdxl:<version-hash>' from the Replicate model page."
                )
                raise HTTPException(status_code=500, detail=f"{e}. {hint}")
            time.sleep(retry_delay * (attempt + 1))
