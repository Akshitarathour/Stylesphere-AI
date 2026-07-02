from agents.base_agent import StyleSphereAgent
import json

class PackingAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Packing Agent for StyleSphere AI. Your expertise is in travel styling, "
            "minimizing luggage, and creating travel checklists. You design packing lists based on "
            "destination, weather conditions, trip duration (number of days), and ensure the selected items "
            "follow a 'capsule wardrobe' approach (items mix-and-match easily to form multiple outfits so the "
            "user doesn't need to carry separate outfits for every single day)."
        )
        super().__init__(name="Packing Agent", instruction=instruction)

    def generate_packing_list(self, wardrobe_items: list, destination: str, weather_condition: str, duration_days: int, api_key: str = None) -> dict:
        """Returns a travel packing recommendation using existing clothing items."""
        if not wardrobe_items:
            return {
                "packing_list": [],
                "mix_match_ideas": "Add items to your digital wardrobe first!",
                "explanation": "No wardrobe inventory available."
            }

        # Simplify items list
        simplified_items = []
        for it in wardrobe_items:
            simplified_items.append({
                "id": it["id"],
                "category": it["category"],
                "colors": it["colors"],
                "fabric": it.get("fabric", "unknown"),
                "notes": it.get("notes", "")
            })

        prompt = (
            f"Create a travel packing checklist from the user's existing wardrobe items list below.\n"
            f"Trip Details:\n"
            f"- Destination: {destination}\n"
            f"- Expected Weather: {weather_condition}\n"
            f"- Trip Duration: {duration_days} days\n\n"
            f"Available Wardrobe Items:\n{json.dumps(simplified_items, indent=2)}\n\n"
            f"Requirements:\n"
            f"1. Select specific items from the user's wardrobe that fit this trip (weather, duration).\n"
            f"2. Follow a capsule wardrobe philosophy (e.g. choose 2 bottoms, 3 tops, 1 outerwear, 1 pair of shoes that can all mix and match).\n"
            f"3. Do not pack more items than necessary for a {duration_days}-day trip.\n\n"
            f"Return a JSON response matching this schema:\n"
            "{\n"
            '  "packing_list": [\n'
            "    {\n"
            '      "item_id": 1,\n'
            '      "notes": "Navy blue t-shirt",\n'
            '      "category": "top",\n'
            '      "reason": "Lightweight, matches both bottoms"\n'
            "    }\n"
            "  ],\n"
            '  "mix_match_ideas": "List 2-3 outfit combination ideas from the packed items (e.g. Day 1: Item A + Item B, Day 2: Item C + Item B)",\n'
            '  "explanation": "Brief advice on packing strategies for this trip"\n'
            "}"
        )

        res = self.run(prompt, api_key=api_key, json_mode=True)
        if res.startswith("Error"):
            # Simple fallback packing list
            packed = []
            categories_selected = set()
            for it in wardrobe_items:
                if it["category"] not in categories_selected:
                    packed.append({
                        "item_id": it["id"],
                        "notes": it["notes"],
                        "category": it["category"],
                        "reason": "Essential category piece."
                    })
                    # Limit to 1 of each category
                    categories_selected.add(it["category"])
            return {
                "packing_list": packed,
                "mix_match_ideas": "Mix tops and bottoms dynamically.",
                "explanation": f"Basic packing list for {duration_days} days in {destination}."
            }

        try:
            return json.loads(res)
        except Exception:
            return {
                "packing_list": [],
                "mix_match_ideas": "Mix items together.",
                "explanation": f"Error parsing packing list for {destination}."
            }
