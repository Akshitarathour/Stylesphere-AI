from agents.base_agent import StyleSphereAgent
import database
import json

class ClosetAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Closet Agent for StyleSphere AI. Your responsibility is to organize wardrobe inventory, "
            "recommend category tagging, analyze item properties, and maintain structured data. "
            "Always output logical, structural suggestions for clothing organization."
        )
        super().__init__(name="Closet Agent", instruction=instruction)

    def add_item(self, category, colors, pattern=None, sleeve_type=None, season_suitability=None,
                 fabric=None, brand=None, purchase_date=None, price=0.0, tags=None, notes=None, image_path=None):
        """Add a clothing item to the wardrobe database."""
        return database.add_clothing_item(
            category=category,
            colors=colors,
            pattern=pattern,
            sleeve_type=sleeve_type,
            season_suitability=season_suitability,
            fabric=fabric,
            brand=brand,
            purchase_date=purchase_date,
            price=price,
            tags=tags,
            notes=notes,
            image_path=image_path
        )

    def get_inventory(self, category=None):
        """Get inventory list, optionally filtered by category."""
        if category:
            return database.get_clothing_by_category(category)
        return database.get_all_clothing_items()

    def get_item(self, item_id):
        """Get a single item by its ID."""
        return database.get_clothing_item(item_id)

    def update_item(self, item_id, **kwargs):
        """Update fields of a clothing item."""
        database.update_clothing_item(item_id, **kwargs)

    def delete_item(self, item_id):
        """Delete an item from the wardrobe."""
        database.delete_clothing_item(item_id)

    def log_wear(self, item_id, occasion, date_worn=None, rating=0, feedback=None):
        """Record when a clothing item is worn."""
        database.log_clothing_wear(item_id, occasion, date_worn, rating, feedback)

    def get_usage_logs(self):
        """Fetch all historical logs of clothing worn."""
        return database.get_usage_history()

    def generate_tags(self, category, colors, pattern, fabric, api_key=None) -> list:
        """Call Groq to auto-suggest modern fashion tags for a clothing description."""
        prompt = (
            f"Suggest 4-6 style tags for a clothing item with the following details:\n"
            f"Category: {category}\n"
            f"Colors: {colors}\n"
            f"Pattern: {pattern}\n"
            f"Fabric: {fabric}\n"
            f"Return ONLY a JSON list of strings."
        )
        res = self.run(prompt, api_key=api_key, json_mode=True)
        if res.startswith("Error"):
            return ["casual", category.lower()]
        try:
            tags = json.loads(res)
            if isinstance(tags, list):
                return tags
            return list(tags.values())
        except Exception:
            return ["casual", category.lower()]
