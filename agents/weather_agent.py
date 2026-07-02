from agents.base_agent import StyleSphereAgent
import json
class WeatherAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Weather Agent for StyleSphere AI. Your job is to advise users on how to dress "
            "for the weather. You suggest layers, advise about rain/wind protections, and flag warnings "
            "for outfits that might be uncomfortable or dangerous in the current forecast (e.g., wearing suede in the rain, "
            "shorts in freezing weather, or heavy coats in hot weather)."
        )
        super().__init__(name="Weather Agent", instruction=instruction)

    def get_weather_rules(self, temp_c: float, condition: str) -> dict:
        """Returns deterministic guidelines based on temp and weather state, to be enriched by LLM."""
        condition = condition.lower()
        rules = {
            "need_outer": False,
            "layering_suggested": False,
            "waterproof_needed": False,
            "warnings": [],
            "suitable_seasons": []
        }

        # Temperature checks
        if temp_c < 10:
            rules["need_outer"] = True
            rules["layering_suggested"] = True
            rules["suitable_seasons"] = ["winter", "autumn"]
            if temp_c < 0:
                rules["warnings"].append("Extremely cold temperature! Insulated heavy coat, gloves, and thermal wear are highly recommended.")
            else:
                rules["warnings"].append("Chilly outside. You will need a heavy jacket, sweater, or coat.")
        elif 10 <= temp_c < 18:
            rules["need_outer"] = True
            rules["layering_suggested"] = True
            rules["suitable_seasons"] = ["spring", "autumn", "winter"]
            rules["warnings"].append("Cool weather. A light jacket, sweater, or cardigan is recommended.")
        elif 18 <= temp_c < 25:
            rules["suitable_seasons"] = ["spring", "summer", "autumn"]
        else: # temp_c >= 25
            rules["suitable_seasons"] = ["summer"]
            rules["warnings"].append("Warm weather. Keep it light and breathable. Avoid heavy materials or layers.")

        # Condition checks
        if any(w in condition for w in ["rain", "drizzle", "shower", "thunderstorm"]):
            rules["waterproof_needed"] = True
            rules["warnings"].append("Rain detected. Bring an umbrella/raincoat and avoid suede or canvas shoes.")
        elif "snow" in condition:
            rules["waterproof_needed"] = True
            rules["warnings"].append("Snow detected. Wear waterproof boots and warm layers.")
        elif "wind" in condition:
            rules["warnings"].append("Windy conditions. A windbreaker or structured outer layer is recommended.")

        return rules

    def generate_weather_advice(self, temp_c: float, condition: str, api_key: str = None) -> str:
        """Calls Groq to formulate styling advice based on the temperature and conditions."""
        rules = self.get_weather_rules(temp_c, condition)
        warnings_str = "\n".join([f"- {w}" for w in rules["warnings"]])
        
        prompt = (
            f"Provide a brief, stylish recommendation (2-3 sentences) on how to dress for this weather:\n"
            f"Temperature: {temp_c}°C\n"
            f"Condition: {condition}\n"
            f"System Flags:\n"
            f"- Layering needed: {rules['layering_suggested']}\n"
            f"- Outerwear needed: {rules['need_outer']}\n"
            f"- Waterproof needed: {rules['waterproof_needed']}\n"
            f"Warnings:\n{warnings_str}\n\n"
            f"Address the user directly with style-focused, practical advice."
        )
        
        advice = self.run(prompt, api_key=api_key)
        if advice.startswith("Error"):
            # Fallback advice if LLM fails
            fallback = f"Dress comfortably for {temp_c}°C and {condition} conditions. "
            if rules['need_outer']:
                fallback += "Be sure to add an outerwear layer like a jacket or coat. "
            if rules['waterproof_needed']:
                fallback += "Bring an umbrella and wear water-resistant shoes."
            return fallback
        return advice
        
    def evaluate_outfit_suitability(self, outfit_items: list, temp_c: float, condition: str, api_key: str = None) -> dict:
        """Evaluates a list of outfit items against weather and flags warnings if any item is unsuitable."""
        # Convert items to text descriptions
        item_details = []
        for it in outfit_items:
            item_details.append(f"- {it['notes']} (Category: {it['category']}, Fabric: {it['fabric']}, Season: {it['season_suitability']})")
        items_str = "\n".join(item_details)
        
        prompt = (
            f"Analyze if the following outfit items are suitable for {temp_c}°C weather with '{condition}' conditions:\n"
            f"{items_str}\n\n"
            f"Return a JSON object with this schema:\n"
            "{\n"
            '  "is_suitable": true/false,\n'
            '  "reason": "explanation of suitability",\n'
            '  "warnings": ["list of specific warning messages if any item is unsuitable or if layering is missing"]\n'
            "}"
        )
        
        res = self.run(prompt, api_key=api_key, json_mode=True)
        if res.startswith("Error"):
            # Fallback deterministic checks
            rules = self.get_weather_rules(temp_c, condition)
            has_outer = any(it['category'] == 'outer' for it in outfit_items)
            is_suitable = True
            warnings = []
            
            if rules['need_outer'] and not has_outer:
                is_suitable = False
                warnings.append("It is cool or cold, but you are missing an outerwear layer.")
                
            for it in outfit_items:
                if rules['waterproof_needed'] and it['fabric'] == 'leather':
                    warnings.append("Avoid wearing premium leather items in wet rain conditions.")
                if temp_c < 10 and it['category'] == 'top' and it['sleeve_type'] == 'sleeveless':
                    warnings.append("A sleeveless top is too cold for this weather without heavy layers.")
            
            return {
                "is_suitable": len(warnings) == 0,
                "reason": "Evaluated based on database weather rules." if len(warnings) == 0 else "Outfit lacks weather compatibility.",
                "warnings": warnings
            }
            
        try:
            return json.loads(res)
        except Exception:
            return {
                "is_suitable": True,
                "reason": "Could not parse detailed evaluation, default to suitable.",
                "warnings": []
            }
