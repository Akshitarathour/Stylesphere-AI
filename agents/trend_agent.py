from agents.base_agent import StyleSphereAgent

class FashionTrendAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Fashion Trend Agent for StyleSphere AI. Your expertise is in high-fashion trends, "
            "classic timeless styles, and smart styling adjustments. Your goal is to guide users to look modern "
            "and stylish WITHOUT buying fast-fashion clothes. You recommend timeless styling formulas (e.g. monochromatic "
            "layering, sandwich color rule) and teach styling techniques (e.g. cuffing jeans, French tucks) that elevate "
            "the appearance of basic garments."
        )
        super().__init__(name="Fashion Trend Agent", instruction=instruction)

    def get_timeless_tips(self) -> list:
        """Returns standard styling formulas."""
        return [
            {
                "formula": "The Sandwich Rule",
                "explanation": "Match the color of your top/outerwear with your shoes, sandwiching a contrasting pants color in between. This balances the outfit visually."
            },
            {
                "formula": "The Third Piece Rule",
                "explanation": "Add a 'third piece' (blazer, cardigan, statement jacket, scarf, or belt) to a basic top-and-bottom outfit to immediately make it look styled and complete."
            },
            {
                "formula": "Proportions Balance",
                "explanation": "If your bottom is wide-leg or baggy, wear a fitted top. If your top is oversized, pair it with structured, slimmer bottoms. This maintains a clean silhouette."
            },
            {
                "formula": "Monochromatic Depth",
                "explanation": "Wear different shades and textures of the same color family (e.g., cream wool sweater, beige trousers, and tan leather shoes). This looks sophisticated and clean."
            }
        ]

    def generate_styling_trend_tips(self, wardrobe_items: list, api_key: str = None) -> str:
        """Suggests styling techniques using the user's current wardrobe items."""
        if not wardrobe_items:
            return "Add items to your wardrobe to get custom trend-matching tips!"

        item_desc = ", ".join([f"{it['colors']} {it['category']}" for it in wardrobe_items[:5]])

        prompt = (
            f"Provide 2 styling styling recommendations (1-2 sentences each) based on current classic-modern trends, "
            f"specifically showing how the user can restyle their existing wardrobe pieces: {item_desc}.\n\n"
            f"Focus on simple styling tweaks (like rolling sleeves, French tuck, or accessory additions) rather than purchasing new items. "
            f"Speak in a friendly, high-fashion expert tone."
        )

        return self.run(prompt, api_key=api_key)
