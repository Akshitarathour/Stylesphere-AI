from agents.base_agent import StyleSphereAgent
import database
import json

class PersonalPreferenceAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Personal Preference Agent for StyleSphere AI. Your job is to study user styling feedback, "
            "learn their fashion tastes (e.g. favorite colors, brands, styles), and update their profile. "
            "You analyze user ratings, liked combinations, and usage history to output personalized recommendations."
        )
        super().__init__(name="Personal Preference Agent", instruction=instruction)

    def load_preference_profile(self) -> dict:
        """Loads preference keys from the database and returns a parsed profile."""
        profile = {
            "favorite_colors": [],
            "preferred_occasions": [],
            "style_vibe": "Casual",
            "excluded_fabrics": []
        }
        
        fav_colors_str = database.get_preference("favorite_colors")
        if fav_colors_str:
            profile["favorite_colors"] = [c.strip() for c in fav_colors_str.split(",")]
            
        pref_occ_str = database.get_preference("preferred_occasions")
        if pref_occ_str:
            profile["preferred_occasions"] = [o.strip() for o in pref_occ_str.split(",")]
            
        profile["style_vibe"] = database.get_preference("style_vibe", "Casual")
        
        excluded_str = database.get_preference("excluded_fabrics")
        if excluded_str:
            profile["excluded_fabrics"] = [f.strip() for f in excluded_str.split(",")]
            
        return profile

    def save_preference_profile(self, profile: dict):
        """Saves styling profile properties back to the database."""
        database.set_preference("favorite_colors", ",".join(profile.get("favorite_colors", [])))
        database.set_preference("preferred_occasions", ",".join(profile.get("preferred_occasions", [])))
        database.set_preference("style_vibe", profile.get("style_vibe", "Casual"))
        database.set_preference("excluded_fabrics", ",".join(profile.get("excluded_fabrics", [])))

    def learn_preferences_from_history(self, api_key: str = None) -> str:
        """Analyzes wardrobe, favorite outfits, and wear history to update the profile automatically."""
        items = database.get_all_clothing_items()
        usage = database.get_usage_history()
        outfits = database.get_outfits(favorites_only=True)
        
        if not items:
            return "No clothing inventory found. Add items to let the AI learn your style preferences."

        # Aggregate inputs
        items_summary = []
        for it in items:
            items_summary.append({
                "notes": it["notes"],
                "category": it["category"],
                "colors": it["colors"],
                "wear_count": it["wear_count"]
            })
            
        outfits_summary = []
        for o in outfits:
            outfits_summary.append({
                "name": o["name"],
                "occasion": o["occasion"],
                "rating": o["rating"]
            })

        prompt = (
            f"Analyze the user's styling activity and wardrobe statistics below:\n"
            f"Wardrobe items details:\n{json.dumps(items_summary[:15], indent=2)}\n\n"
            f"Favorited outfits:\n{json.dumps(outfits_summary, indent=2)}\n\n"
            f"Summarize the user's implicit preferences. Identify:\n"
            f"1. Top 2 favorite colors (based on items and wear count)\n"
            f"2. Top 2 preferred occasions\n"
            f"3. General styling vibe (e.g., Casual, Classic, Bohemian, Minimalist, Bold)\n\n"
            f"Return a JSON response matching this schema:\n"
            "{\n"
            '  "favorite_colors": ["color1", "color2"],\n'
            '  "preferred_occasions": ["occasion1", "occasion2"],\n'
            '  "style_vibe": "vibe string"\n'
            "}"
        )

        res = self.run(prompt, api_key=api_key, json_mode=True)
        if res.startswith("Error"):
            return "Could not load preference analyzer."
            
        try:
            prefs = json.loads(res)
            
            # Save learned preferences
            profile = self.load_preference_profile()
            profile["favorite_colors"] = prefs.get("favorite_colors", profile["favorite_colors"])
            profile["preferred_occasions"] = prefs.get("preferred_occasions", profile["preferred_occasions"])
            profile["style_vibe"] = prefs.get("style_vibe", profile["style_vibe"])
            self.save_preference_profile(profile)
            
            return f"Updated preferences! Favorite Colors: {', '.join(profile['favorite_colors'])}. Style Vibe: {profile['style_vibe']}."
        except Exception:
            return "Failed to save parsed preferences."
