const PROD_API_URL = "https://YOUR-STYLO-API.example.com";
const API_BASE =
  (typeof window !== "undefined" && window.location.hostname === "localhost")
    ? "http://localhost:8000"
    : PROD_API_URL;

export async function fetchRecommendations(
  clothingItem: string, 
  color: string = "", 
  style: string[] = [], 
  gender: "men" | "women" = "men"
) {
  const response = await fetch("http://127.0.0.1:8000/api/recommend/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      clothing_item: clothingItem, 
      color: color, 
      style: style,
      gender: gender 
    }),
  });
  if (!response.ok) throw new Error("Failed to fetch recommendations");
  const data = await response.json();
  const rec = data.recommendations;
  // Convert snake_case to camelCase for frontend
  return {
    colorPalette: rec.color_palette,
    styleInspirations: rec.style_inspirations.map((s: any) => ({
      description: s.description,
      mainImagePrompt: s.main_image_prompt,
    })),
    outfits: rec.outfits.map((outfit: any) => ({
      top: outfit.top,
      pants: outfit.pants,
      shoes: outfit.shoes,
      imagePrompt: outfit.image_prompt,
    })),
  };
}

export async function generateImage(prompt: string): Promise<string> {
  const response = await fetch("http://127.0.0.1:8000/api/recommend/image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!response.ok) throw new Error("Failed to generate image");
  const data = await response.json();
  return data.image_url;
} 