import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Palette, Star, X } from "lucide-react";
import { StyleRecommendations } from "@/components/StyleRecommendations";
import { fetchRecommendations } from "@/utils/api";
import { Spinner } from "@/components/ui/Spinner";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

const Index = () => {
  const [clothingItem, setClothingItem] = useState("");
  const [color, setColor] = useState("");
  const [selectedStyles, setSelectedStyles] = useState<string[]>([]);
  const [currentStyleInput, setCurrentStyleInput] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [gender, setGender] = useState<"men" | "women">("men");
  // Load persisted preferences
  useEffect(() => {
    try {
      const savedGender = localStorage.getItem('pref_gender');
      const savedStyles = localStorage.getItem('pref_styles');
      if (savedGender === 'men' || savedGender === 'women') {
        setGender(savedGender);
      }
      if (savedStyles) {
        const parsed = JSON.parse(savedStyles);
        if (Array.isArray(parsed)) {
          setSelectedStyles(parsed.slice(0, 3));
        }
      }
    } catch (_) {
      // ignore
    }
  }, []);

  // Persist preferences on change
  useEffect(() => {
    try {
      localStorage.setItem('pref_gender', gender);
    } catch (_) {}
  }, [gender]);

  useEffect(() => {
    try {
      localStorage.setItem('pref_styles', JSON.stringify(selectedStyles));
    } catch (_) {}
  }, [selectedStyles]);

  const handleStyleAdd = () => {
    const styleToAdd = currentStyleInput.trim();
    if (styleToAdd && !selectedStyles.includes(styleToAdd)) {
      setSelectedStyles([...selectedStyles, styleToAdd]);
      setCurrentStyleInput("");
    }
  };

  const handleStyleRemove = (styleToRemove: string) => {
    setSelectedStyles(selectedStyles.filter((s) => s !== styleToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clothingItem.trim()) return;
    setIsLoading(true);
    try {
      const results = await fetchRecommendations(clothingItem, color, selectedStyles, gender);
      setRecommendations(results);
    } catch (error) {
      alert("Failed to get recommendations from backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const colors = ["red", "blue", "green", "yellow", "black", "white", "beige", "navy", "purple", "pink", "olive green", "gray", "brown", "cream", "khaki", "silver", "burgundy", "camel", "denim", "tan", "light blue", "dark wash"];
  const categories = ["t-shirt", "sneakers", "pants", "polo shirt", "jeans", "shirt", "blouse", "hoodie", "sweater", "pullover", "top", "jacket", "blazer", "trousers", "shorts", "skirt", "leggings", "culottes", "shoes", "boots", "sandals", "loafers", "heels", "flats", "dress"];
  const styles = ["elegant", "sportive", "casual", "smart", "street", "business casual", "professional", "date night", "edgy casual", "smart casual", "business formal", "sophisticated casual", "feminine casual", "relaxed casual", "cozy smart casual", "chic Parisian", "urban chic", "street style"];

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-6">
        <section className="py-14 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <span className="inline-flex items-center rounded-full border px-3 py-1 text-xs text-muted-foreground">Your AI-powered personal stylist</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-foreground mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Elevate your wardrobe with confident, curated looks
          </h1>
          <p className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto">
            Describe what you have in mind and instantly get polished outfit suggestions, color palettes, and inspiration images.
          </p>
        </section>

        <Card className="mb-12 shadow-sm border-muted">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5" />
              Get your style recommendations
            </CardTitle>
            <CardDescription>
              For example: "shirt" in "red" or "jeans" for a "casual" look.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>Gender</Label>
                <RadioGroup
                  value={gender}
                  onValueChange={(value) => setGender(value as "men" | "women")}
                  className="flex gap-4 mt-1"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="men" id="men" />
                    <Label htmlFor="men">Men</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="women" id="women" />
                    <Label htmlFor="women">Women</Label>
                  </div>
                </RadioGroup>
              </div>

              <div>
                <Label htmlFor="color">Specific Color (e.g., red)</Label>
                <Input
                  id="color"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  placeholder="e.g., red"
                  className="mt-1"
                  list="colors"
                />
                <datalist id="colors">
                  {colors.map((c) => (
                    <option key={c} value={c} />
                  ))}
                </datalist>
              </div>

              <div>
                <Label htmlFor="clothing-item">Clothing Item (e.g., shirt)</Label>
                <Input
                  id="clothing-item"
                  value={clothingItem}
                  onChange={(e) => setClothingItem(e.target.value)}
                  placeholder="e.g., shirt"
                  className="mt-1"
                  list="clothing-categories"
                />
                <datalist id="clothing-categories">
                  {categories.map((cat) => (
                    <option key={cat} value={cat} />
                  ))}
                </datalist>
              </div>

              <div>
                <Label htmlFor="style">Desired Style (Optional, up to 3)</Label>
                <div className="flex items-center gap-2 mt-1">
                  <Input
                    id="style"
                    value={currentStyleInput}
                    onChange={(e) => setCurrentStyleInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleStyleAdd();
                      }
                    }}
                    placeholder="e.g., casual"
                    className="flex-grow"
                    list="styles"
                  />
                  <Button type="button" onClick={handleStyleAdd} disabled={selectedStyles.length >= 3}>
                    Add Style
                  </Button>
                </div>
                <datalist id="styles">
                  {styles.map((s) => (
                    <option key={s} value={s} />
                  ))}
                </datalist>
                <div className="mt-2 flex flex-wrap gap-2">
                  {selectedStyles.map((s) => (
                    <Badge key={s} className="flex items-center gap-1 pr-1">
                      {s}
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleStyleRemove(s)}
                        className="h-auto p-0.5"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-primary hover:bg-primary/90"
                disabled={isLoading || !clothingItem.trim()}
              >
                <div className="flex items-center gap-2">
                  <Star className="h-4 w-4" />
                  Get Style Recommendations
                </div>
              </Button>
            </form>
          </CardContent>
        </Card>

        {isLoading && (
          <div className="flex justify-center my-8">
            <Spinner />
          </div>
        )}
        {recommendations && !isLoading && (
          <StyleRecommendations 
            clothingItem={clothingItem}
            color={color}
            gender={gender}
            recommendations={recommendations}
          />
        )}

        {/* Features */}
        <section id="features" className="py-16">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-3">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-accent"><rect x="3" y="4" width="18" height="14" rx="3" stroke="currentColor" strokeWidth="2"/><path d="M7 8h10M7 12h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
                  Personalized Outfits
                </CardTitle>
                <CardDescription>Looks tailored to your item, color, and style.</CardDescription>
              </CardHeader>
            </Card>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-3">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-accent"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2"/><path d="M12 3v18M3 12h18" stroke="currentColor" strokeWidth="2"/></svg>
                  Curated Palettes
                </CardTitle>
                <CardDescription>Harmonized color suggestions that elevate.</CardDescription>
              </CardHeader>
            </Card>
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-3">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-accent"><rect x="4" y="6" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="2"/><path d="M10 9l3 3-3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                  Visual Inspiration
                </CardTitle>
                <CardDescription>Instant concept images to guide your choices.</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="py-12 border-t">
          <div className="grid gap-8 md:grid-cols-3">
            <div>
              <h3 className="text-lg font-medium mb-1">1. Describe</h3>
              <p className="text-muted-foreground">Tell us the item, color, and up to 3 styles.</p>
            </div>
            <div>
              <h3 className="text-lg font-medium mb-1">2. Review</h3>
              <p className="text-muted-foreground">Explore suggested outfits and color palettes.</p>
            </div>
            <div>
              <h3 className="text-lg font-medium mb-1">3. Decide</h3>
              <p className="text-muted-foreground">Open visuals to validate the final look.</p>
            </div>
          </div>
        </section>

        <section id="contact" className="py-12 border-t text-center text-sm text-muted-foreground">
          <p>Questions? Reach us at contact@stylesync.app</p>
        </section>
      </div>

    </div>
  );
};

export default Index;
