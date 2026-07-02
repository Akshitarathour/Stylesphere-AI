from agents.base_agent import StyleSphereAgent
import json

class StyleAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Style Recommendation Agent for StyleSphere AI. Your expertise is in color theory "
            "(monochromatic, analogous, complementary, triadic, and neutral matching), silhouette coordination, "
            "and styling outfits. You combine wardrobe items (e.g. tops, bottoms, outerwear, shoes, accessories) "
            "to create outfits that look fashionable, appropriate, and cohesive. "
            "Always return your recommendation in structured JSON formats as requested."
        )
        super().__init__(name="Style Recommendation Agent", instruction=instruction)

    def recommend_outfits(self, wardrobe_items: list, occasion: str, weather_advice: str, api_key: str = None) -> list:
        """Suggests 1-2 cohesive outfits from the available wardrobe items list."""
        if not wardrobe_items:
            return []

        # Simplify items list to send to the LLM to save token space
        simplified_items = []
        for it in wardrobe_items:
            simplified_items.append({
                "id": it["id"],
                "category": it["category"],
                "colors": it["colors"],
                "pattern": it.get("pattern", "solid"),
                "sleeve_type": it.get("sleeve_type", "short"),
                "season_suitability": it.get("season_suitability", "all-season"),
                "fabric": it.get("fabric", "unknown"),
                "notes": it.get("notes", ""),
                "tags": it.get("tags", "")
            })

        items_str = json.dumps(simplified_items, indent=2)

        prompt = (
            f"Build 1 or 2 styling outfits from the available wardrobe items list below.\n"
            f"Occasion: {occasion}\n"
            f"Weather styling instructions: {weather_advice}\n\n"
            f"Available Wardrobe Items:\n{items_str}\n\n"
            f"Guidelines:\n"
            f"1. A complete outfit must contain either:\n"
            f"   - A top, a bottom, shoes, and optionally outerwear (if weather requires) and accessories.\n"
            f"   - A dress, shoes, and optionally outerwear and accessories.\n"
            f"2. Ensure color compatibility (e.g., matching neutrals, complementary color pairs, analogous shades).\n"
            f"3. Ensure the outfit matches the occasion (casual, formal, etc.) and weather rules.\n"
            f"4. ONLY use item IDs from the list provided. Do not invent items.\n\n"
            f"Return a JSON list of objects matching this schema exactly:\n"
            "[\n"
            "  {\n"
            '    "name": "Creative name for the outfit, e.g. Navy Casual Blazer Combo",\n'
            '    "description": "Short explanation of the style vibe and colors",\n'
            '    "item_ids": [1, 2, 3], -- List of integer item IDs forming the outfit\n'
            '    "stylist_notes": "Detailed stylist explanation of why these items match, color theory used, and why it is suitable for this weather and occasion"\n'
            "  }\n"
            "]"
        )

        res = self.run(prompt, api_key=api_key, json_mode=True)
        if res.startswith("Error"):
            # Return basic fallback outfit if LLM fails
            return self._generate_fallback_outfits(wardrobe_items, occasion)

        try:
            outfits = json.loads(res.strip())
            # Clean and validate that item_ids are integers
            for o in outfits:
                o["item_ids"] = [int(i) for i in o.get("item_ids", []) if str(i).isdigit()]
            return outfits
        except Exception:
            return self._generate_fallback_outfits(wardrobe_items, occasion)

    def _generate_fallback_outfits(self, items: list, occasion: str) -> list:
        """Deterministic basic fallback outfit generator in case of API failure."""
        tops = [it for it in items if it["category"] == "top"]
        bottoms = [it for it in items if it["category"] == "bottom"]
        shoes = [it for it in items if it["category"] == "shoes"]
        dresses = [it for it in items if it["category"] == "dress"]

        outfits = []
        if tops and bottoms and shoes:
            outfits.append({
                "name": f"Classic {occasion.title()} Combination",
                "description": "A reliable, comfortable daily combination.",
                "item_ids": [tops[0]["id"], bottoms[0]["id"], shoes[0]["id"]],
                "stylist_notes": f"This classic combination matching your {tops[0]['notes']} and {bottoms[0]['notes']} is clean and simple, ideal for a {occasion} look."
            })
        elif dresses and shoes:
            outfits.append({
                "name": f"Elegant {occasion.title()} Dress",
                "description": "A stylish dress setup.",
                "item_ids": [dresses[0]["id"], shoes[0]["id"]],
                "stylist_notes": f"Pairing the {dresses[0]['notes']} with {shoes[0]['notes']} creates a quick, attractive outfit."
            })
        return outfits
