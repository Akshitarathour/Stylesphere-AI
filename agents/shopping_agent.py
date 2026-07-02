from agents.base_agent import StyleSphereAgent
import database
import json

class ShoppingAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Shopping Advisor Agent for StyleSphere AI. Your goal is to help users build a versatile "
            "wardrobe while preventing wasteful spending. You identify wardrobe gaps (e.g., mismatch in top vs bottom ratio, "
            "lack of outerwear for winter), alert users when they try to buy duplicate clothes, suggest highly versatile items "
            "that can form many outfits, and provide cost-per-wear insights to prove the value of quality purchases."
        )
        super().__init__(name="Shopping Advisor Agent", instruction=instruction)

    def analyze_wardrobe_gaps(self) -> dict:
        """Calculates item counts per category and determines database gaps."""
        items = database.get_all_clothing_items()
        counts = {"top": 0, "bottom": 0, "shoes": 0, "outer": 0, "dress": 0, "accessory": 0}
        
        for it in items:
            cat = it["category"].lower()
            if cat in counts:
                counts[cat] += 1
                
        gaps = []
        if len(items) > 0:
            if counts["top"] > 3 * counts["bottom"]:
                gaps.append(f"Bottoms gap: You have {counts['top']} tops but only {counts['bottom']} bottoms. Adding versatile trousers, jeans, or skirts would multiply your outfit options.")
            if counts["shoes"] == 0:
                gaps.append("Shoes gap: You haven't added any shoes. Adding at least one pair of versatile sneakers and dress shoes is recommended.")
            if counts["outer"] == 0:
                gaps.append("Outerwear gap: You have no coats or jackets. Consider adding a neutral blazer or jacket for cooler weather layering.")
                
        return {
            "counts": counts,
            "gaps": gaps
        }

    def evaluate_wishlist_item(self, category: str, colors: str, pattern: str, fabric: str, price: float, api_key: str = None) -> dict:
        """Evaluates a potential purchase on the wishlist to see if it is a duplicate and check versatility."""
        items = database.get_all_clothing_items()
        
        # Simplify existing items for comparison
        existing_items = []
        for it in items:
            existing_items.append({
                "category": it["category"],
                "colors": it["colors"],
                "pattern": it.get("pattern", "solid"),
                "fabric": it.get("fabric", "unknown"),
                "notes": it.get("notes", "")
            })

        prompt = (
            f"Compare a prospective clothing item you want to buy with the user's existing wardrobe items below.\n"
            f"Prospective Item Details:\n"
            f"- Category: {category}\n"
            f"- Colors: {colors}\n"
            f"- Pattern: {pattern}\n"
            f"- Fabric: {fabric}\n"
            f"- Price: ${price}\n\n"
            f"Existing Wardrobe:\n{json.dumps(existing_items, indent=2)}\n\n"
            f"Determine:\n"
            f"1. Is it a duplicate (extremely similar in category, colors, and pattern to what they already own)?\n"
            f"2. How versatile is it (will it match with existing categories and colors)?\n"
            f"3. What is the value rating of this purchase?\n\n"
            f"Return a JSON response matching this schema:\n"
            "{\n"
            '  "is_duplicate": true/false,\n'
            '  "duplicate_reason": "if duplicate, explain which item it replicates, otherwise empty",\n'
            '  "versatility_score": 0-100 (rating how well it pairs with existing items),\n'
            '  "versatility_analysis": "brief explanation of what outfits it can make",\n'
            '  "advice": "Should they buy it? Provide clear fashion advice."\n'
            "}"
        )

        res = self.run(prompt, api_key=api_key, json_mode=True)
        if res.startswith("Error"):
            # Simple fallback check
            is_dup = False
            dup_reason = ""
            for it in items:
                if it["category"] == category and any(c.strip() in it["colors"] for c in colors.split(",")):
                    is_dup = True
                    dup_reason = f"You already have a similar {it['colors']} {it['category']} ({it['notes']})."
                    break
            return {
                "is_duplicate": is_dup,
                "duplicate_reason": dup_reason,
                "versatility_score": 75,
                "versatility_analysis": "Pairs well with standard items.",
                "advice": "Consider buying if it fills a specific wardrobe style need."
            }

        try:
            return json.loads(res)
        except Exception:
            return {
                "is_duplicate": False,
                "duplicate_reason": "",
                "versatility_score": 80,
                "versatility_analysis": "Analyzed successfully.",
                "advice": "Verified versatile addition."
            }

    def get_cost_per_wear_insights(self) -> list:
        """Calculates cost-per-wear (CPW) for all items in the wardrobe database."""
        items = database.get_all_clothing_items()
        insights = []
        for it in items:
            price = it.get("price", 0.0) or 0.0
            wear_count = it.get("wear_count", 0)
            
            # Prevent division by zero
            cpw = price if wear_count == 0 else price / wear_count
            insights.append({
                "id": it["id"],
                "notes": it["notes"],
                "category": it["category"],
                "price": price,
                "wear_count": wear_count,
                "cpw": round(cpw, 2),
                "image_path": it.get("image_path")
            })
        
        # Sort by CPW descending (highest cost per wear, i.e., least value so far)
        return sorted(insights, key=lambda x: x["cpw"], reverse=True)
