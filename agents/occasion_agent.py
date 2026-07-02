from agents.base_agent import StyleSphereAgent

class OccasionAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Occasion Agent for StyleSphere AI. Your job is to define and guide the user on dress codes "
            "for specific life situations: College, Office, Interview, Wedding, Party, Festival, Casual, Date, and Travel. "
            "You specify style constraints, formalness scales, color restrictions (e.g. avoiding black/white at weddings in some cultures, "
            "or recommending blue/grey for interviews), and guide overall outfit coordination."
        )
        super().__init__(name="Occasion Agent", instruction=instruction)

    def get_occasion_profile(self, occasion: str) -> dict:
        """Returns standard style criteria for key occasions."""
        profiles = {
            "college": {
                "formalness": "Casual",
                "focus": "Comfort, mobility, layering",
                "rules": "Comfortable jeans, t-shirts, sneakers, backpacks, casual outerwear.",
                "color_themes": "Open/expressive"
            },
            "office": {
                "formalness": "Business Casual / Smart Casual",
                "focus": "Polished, clean, neat",
                "rules": "Collared shirts, blazers, slacks, chinos, blouses, loafers, oxfords. No graphic tees or distressed denim.",
                "color_themes": "Neutrals, blues, greys, whites"
            },
            "interview": {
                "formalness": "Formal",
                "focus": "Professionalism, competence",
                "rules": "Suits, pressed button-up shirts, blouses, dress pants, pencil skirts, ties, closed-toe dress shoes.",
                "color_themes": "Dark blue, charcoal grey, white, navy"
            },
            "wedding": {
                "formalness": "Festive / Elegant Formal",
                "focus": "Celebration, dressy",
                "rules": "Suits, tuxedos, evening dresses, formal sarees/sherwanis, elegant heels or dress shoes.",
                "color_themes": "Vibrant and celebratory colors. Avoid solid white or black (traditionally)."
            },
            "party": {
                "formalness": "Vibrant Semi-formal / Glamorous",
                "focus": "Fun, stylish, expressive",
                "rules": "Cocktail dresses, fashion-forward tops, shirts with chinos, boots, stylish jackets, clean denim is acceptable.",
                "color_themes": "Black, metallics, jewel tones, bold colors"
            },
            "festival": {
                "formalness": "Traditional / Expressive Casual",
                "focus": "Cultural, festive, comfortable",
                "rules": "Traditional wear or colorful bohemian styles. Breathable fabrics since festivals often require standing/walking.",
                "color_themes": "Bright, warm colors (yellows, reds, oranges, gold)"
            },
            "casual": {
                "formalness": "Casual / Relaxed",
                "focus": "Comfort, ease",
                "rules": "T-shirts, hoodies, jeans, shorts, sneakers, sandals, loungewear.",
                "color_themes": "Any colors"
            },
            "date": {
                "formalness": "Smart Casual / Romantic",
                "focus": "Attractive, well-fitted, approachable",
                "rules": "Nice shirts, dresses, well-fitted jeans or trousers, cardigans, boots or nice shoes, subtle accessories.",
                "color_themes": "Warm colors, deep red, black, pastel tones"
            },
            "travel": {
                "formalness": "Ultra Casual / Utility",
                "focus": "Comfort, practicality, weather-proofing",
                "rules": "Stretch pants, basic tees, hoodies, packable windbreakers, walking shoes or trainers, minimal jewelry.",
                "color_themes": "Neutral mix-and-match colors"
            }
        }
        
        occ_key = occasion.lower().strip()
        return profiles.get(occ_key, {
            "formalness": "Smart Casual",
            "focus": "Balanced styling",
            "rules": "Clean, matching clothing suitable for a general outing.",
            "color_themes": "Balanced palette"
        })

    def explain_occasion_guideline(self, occasion: str, api_key: str = None) -> str:
        """Uses Groq to explain what makes an outfit appropriate for a specific occasion."""
        profile = self.get_occasion_profile(occasion)
        prompt = (
            f"Explain the style guideline for a '{occasion}' occasion in a friendly, expert stylist voice (1-2 sentences).\n"
            f"Focus: {profile['focus']}\n"
            f"Dress Rules: {profile['rules']}\n"
            f"Preferred Colors: {profile['color_themes']}"
        )
        return self.run(prompt, api_key=api_key)
