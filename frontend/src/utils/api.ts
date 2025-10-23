// frontend/src/utils/api.ts

// === Base URLs ===
const LOCAL_API_URL = "http://localhost:8000";
const PROD_API_URL = "https://stylo-backend.onrender.com";

// automatically choose the API base URL based on the environment
const API_BASE =
  typeof window !== "undefined" && window.location.hostname === "localhost"
    ? LOCAL_API_URL
    : PROD_API_URL;

// === Fetch Recommendations ===
export async function fetchRecommendations(
  clothingItem: string,
  color: string = "",
  style: string[] = [],
  gender: "men" | "women" = "men"
) {
  const response = await fetch(`${API_BASE}/ai/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      clothing_item: clothingItem,
      color,
      style,
      gender,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Failed to fetch recommendations:", errorText);
    throw new Error("Failed to fetch recommendations");
  }

  const data = await response.json();

  // convert to camelCase to match the frontend
  return {
    colorPalette: data.color_palette,
    styleInspirations: data.style_inspirations.map((s: any) => ({
      description: s.description,
      mainImagePrompt: s.main_image_prompt,
    })),
    outfits: data.outfits.map((outfit: any) => ({
      top: outfit.top,
      pants: outfit.pants,
      shoes: outfit.shoes,
      imagePrompt: outfit.image_prompt,
    })),
  };
}

// === Generate Image ===
export async function generateImage(prompt: string): Promise<string> {
  const response = await fetch(`${API_BASE}/ai/generate-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Failed to generate image:", errorText);
    throw new Error("Failed to generate image");
  }

  const data = await response.json();
  return data.image_url;
}

// === Optional Helper ===
export const getApiBase = () => API_BASE;
