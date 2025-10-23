interface OutfitRecommendation {
  top?: string; // Optional, represents the main clothing item if different from pants/shoes
  pants: string;
  shoes: string;
  styleDescription: string;
  imagePrompt: string;
}

interface StyleRecommendations {
  colorPalette: string[];
  outfits: OutfitRecommendation[];
}

// The generateOutfitRecommendations function is no longer used as recommendations are fetched from the backend.
// It can be removed or kept as a placeholder if future local generation logic is planned.
// For now, it's being removed to simplify the codebase.
