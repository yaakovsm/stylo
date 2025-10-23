import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Palette, ShirtIcon, X } from "lucide-react";
import { Spinner } from "@/components/ui/Spinner";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "@/components/ui/use-toast";
import React, { useState, useEffect } from "react";
import { generateImage } from "@/utils/api";
import { Button } from "@/components/ui/button";

interface ColorPaletteItem {
  name: string;
  hex: string;
}

interface OutfitRecommendation {
  top?: string;
  pants?: string;
  shoes?: string;
  imageUrl?: string;
  imagePrompt?: string;
}

interface StyleInspiration {
  description: string;
  mainImagePrompt: string;
  imageUrl?: string;
}

interface StyleRecommendationsProps {
  clothingItem: string;
  color: string;
  gender: 'men' | 'women';
  recommendations: {
    colorPalette: ColorPaletteItem[];
    styleInspirations: StyleInspiration[];
    outfits: OutfitRecommendation[];
  };
}

export const StyleRecommendations = ({ clothingItem, color, gender, recommendations }: StyleRecommendationsProps) => {
  const [selectedItem, setSelectedItem] = useState<OutfitRecommendation | StyleInspiration | null>(null);

  const handleImageClick = (item: OutfitRecommendation | StyleInspiration) => {
    setSelectedItem(item);
  };

  const handleCloseImage = () => {
    setSelectedItem(null);
  };

  const getModalTitle = (outfit: OutfitRecommendation) => {
    const parts: string[] = [];
    if (outfit.top && outfit.top !== 'N/A (complete dress look)') parts.push(outfit.top);
    if (outfit.pants && outfit.pants !== 'N/A (complete dress look)') parts.push(outfit.pants);
    if (outfit.shoes) parts.push(outfit.shoes);
    return parts.length > 0 ? parts.join(', ') : "Full Image";
  };

  return (
    <div className="space-y-8">
      {/* Color Palette */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Color Palette for "{clothingItem} in {color}"
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-6 justify-center">
            {recommendations.colorPalette.map((color, idx) => (
              <div key={idx} className="flex flex-col items-center w-20">
                <span
                  className="w-10 h-10 rounded-full border border-border mb-2"
                  style={{ backgroundColor: color.hex }}
                />
                <span className="text-xs text-muted-foreground text-center break-words">{color.name}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Outfit Recommendations */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <ShirtIcon className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold text-foreground">Outfit Recommendations for "{clothingItem} in {color}"</h2>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {recommendations.outfits.map((outfit, idx) => (
            <Card key={idx} className="flex flex-col h-full shadow-md">
              <CardContent className="flex flex-col gap-4 p-6">
                {outfit.top && outfit.top !== 'N/A (complete dress look)' && (
                  <div>
                    <span className="block text-sm font-medium text-muted-foreground mb-1">Top</span>
                    <div className="text-foreground text-base font-normal pl-2">{outfit.top}</div>
                  </div>
                )}
                <div>
                  <span className="block text-sm font-medium text-muted-foreground mb-1">Pants</span>
                  <div className="text-foreground text-base font-normal pl-2">{outfit.pants}</div>
                </div>
                <div>
                  <span className="block text-sm font-medium text-muted-foreground mb-1">Shoes</span>
                  <div className="text-foreground text-base font-normal pl-2">{outfit.shoes}</div>
                </div>
                {recommendations.styleInspirations[idx] && (
                  <StyleInspirationCard
                    description={recommendations.styleInspirations[idx].description}
                    imagePrompt={`Fashion photograph, ${recommendations.styleInspirations[idx].description.toLowerCase()} style. ${gender === 'men' ? 'Male model' : 'Female model'}. Outfit based on ${clothingItem} in ${color}. Include: ${
                      (outfit.top && outfit.top !== 'N/A (complete dress look)') ? outfit.top : ''
                    }${(outfit.top && outfit.top !== 'N/A (complete dress look)') ? ', ' : ''}${
                      outfit.pants || ''
                    }${outfit.shoes ? ', ' : ''}${outfit.shoes || ''}. Photorealistic, full outfit visible, studio lighting.`}
                    regeneratePrompt={`Fashion photograph, ${recommendations.styleInspirations[idx].description.toLowerCase()} style. ${gender === 'men' ? 'Male model' : 'Female model'}. Outfit based on ${clothingItem} in ${color}. Include: ${
                      (outfit.top && outfit.top !== 'N/A (complete dress look)') ? outfit.top : ''
                    }${(outfit.top && outfit.top !== 'N/A (complete dress look)') ? ', ' : ''}${
                      outfit.pants || ''
                    }${outfit.shoes ? ', ' : ''}${outfit.shoes || ''}. Photorealistic, full outfit visible, studio lighting.`}
                    onImageClick={(data) => handleImageClick(data)}
                  />
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {selectedItem && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75"
          onClick={handleCloseImage}
        >
          <Card className="max-w-3xl max-h-[90vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <CardHeader className="flex flex-row items-center justify-between p-4">
              <CardTitle>
                {"description" in selectedItem ? selectedItem.description : getModalTitle(selectedItem as OutfitRecommendation)}
              </CardTitle>
              <Button variant="ghost" size="icon" onClick={handleCloseImage}>
                <X className="h-5 w-5" />
              </Button>
            </CardHeader>
            <CardContent className="p-0">
              <img src={selectedItem.imageUrl} alt="Full outfit image" className="max-h-[80vh] w-auto max-w-full object-contain mx-auto" />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

interface StyleInspirationCardProps {
  description: string;
  imagePrompt: string;
  regeneratePrompt: string;
  onImageClick: (data: { imageUrl: string; description: string; }) => void;
}

const StyleInspirationCard: React.FC<StyleInspirationCardProps> = ({
  description, 
  imagePrompt,
  regeneratePrompt,
  onImageClick
}) => {
  const [mainImageUrl, setMainImageUrl] = useState<string | undefined>(undefined);
  const [imageStatus, setImageStatus] = useState<'pending' | 'loading' | 'success' | 'failed'>(
    imagePrompt ? 'pending' : 'failed'
  );
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const generateImageForCard = async () => {
      if (!imagePrompt || imageStatus !== 'pending') {
        return;
      }

      setImageStatus('loading');
      try {
        const imageUrl = await generateImage(imagePrompt);
        setMainImageUrl(imageUrl);
        setImageStatus('success');
      } catch (error) {
        console.error(`Failed to generate image for prompt "${imagePrompt}":`, error);
        // Retry up to 2 times with a delay
        if (retryCount < 2) {
          setRetryCount(prev => prev + 1);
          setTimeout(() => {
            setImageStatus('pending');
          }, 2000); // Wait 2 seconds before retrying
        } else {
          setImageStatus('failed');
        }
      }
    };

    generateImageForCard();
  }, [imagePrompt, imageStatus, retryCount]);

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShirtIcon className="h-5 w-5" />
          Style Inspiration
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground text-base mb-4">{description}</p>
        <ImageWithLoading
          imageUrl={mainImageUrl}
          alt={`Image for ${description}`}
          imageStatus={imageStatus}
          onClick={mainImageUrl ? () => onImageClick({ imageUrl: mainImageUrl, description: description }) : undefined}
        />
        <div className="mt-3 flex items-center justify-between">
          {imageStatus === 'failed' && (
            <div className="text-destructive text-sm">Failed to generate image.</div>
          )}
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={async () => {
              setImageStatus('loading');
              try {
                // Use a slightly varied prompt to encourage a new generation
                const url = await generateImage(`${regeneratePrompt} Variation ${Date.now() % 1000}`);
                setMainImageUrl(url);
                setImageStatus('success');
                toast({ title: 'Image updated', description: 'Generated a new variation.' });
              } catch (err) {
                setImageStatus('failed');
                toast({ title: 'Failed to regenerate', description: 'Please try again.', variant: 'destructive' });
              }
            }}
          >
            Regenerate image
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

interface ImageWithLoadingProps {
  imageUrl: string | undefined;
  alt: string;
  imageStatus: 'pending' | 'loading' | 'success' | 'failed';
  onClick?: () => void;
}

const ImageWithLoading: React.FC<ImageWithLoadingProps> = ({ imageUrl, alt, imageStatus, onClick }) => {
  if (imageStatus === 'failed') {
    return (
      <div className="w-full h-32 bg-destructive/10 border-2 border-dashed border-destructive/30 rounded-lg flex items-center justify-center text-destructive text-sm">
        Failed to generate image
      </div>
    );
  }

  if (imageStatus === 'pending' || imageStatus === 'loading') {
    return (
      <div className="w-full h-32 bg-muted border-2 border-dashed border-border rounded-lg flex items-center justify-center text-muted-foreground text-sm">
        <div className="text-center">
          <Spinner className="w-6 h-6 mb-2" />
          <p>Generating outfit visualization...</p>
        </div>
      </div>
    );
  }

  if (imageStatus === 'success' && imageUrl) {
    return (
      <div className="w-full h-32 relative flex items-center justify-center cursor-pointer group" onClick={onClick} title="Open full picture">
        <img
          src={imageUrl}
          alt={alt}
          className="w-full h-32 object-cover rounded-lg border border-border"
          style={{ aspectRatio: '1 / 1' }}
        />
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 flex items-center justify-center rounded-lg transition-all duration-300">
          <span className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-sm">View Full Image</span>
        </div>
      </div>
    );
  }

  return null; // Should not happen if status is always one of the defined values
};
