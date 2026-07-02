from agents.base_agent import StyleSphereAgent
import database

class SustainabilityAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are the Sustainability Agent for StyleSphere AI. Your goal is to promote sustainable fashion. "
            "You analyze clothing usage statistics, calculate wardrobe utilization rates, identify clothes that "
            "are rarely worn (underused) or frequently worn (overused), and offer tips to reduce fashion waste "
            "by restyling underused clothing and recommending against buying duplicate clothes."
        )
        super().__init__(name="Sustainability Agent", instruction=instruction)

    def calculate_utilization(self) -> dict:
        """Calculates wardrobe statistics and returns underused/overused items."""
        items = database.get_all_clothing_items()
        if not items:
            return {
                "total_items": 0,
                "worn_items": 0,
                "utilization_rate": 0.0,
                "underused": [],
                "overused": [],
                "sustainability_score": 100
            }

        total_items = len(items)
        worn_items = len([it for it in items if it["wear_count"] > 0])
        utilization_rate = (worn_items / total_items) * 100

        # Define thresholds:
        # Underused: items that have been worn < 2 times and owned for some time (or just worn low relative to others)
        # Overused: items worn > 10 times
        underused = [it for it in items if it["wear_count"] <= 1]
        overused = [it for it in items if it["wear_count"] >= 10]

        # Calculate a basic sustainability score (0-100) based on:
        # 1. Utilization rate (higher is better, 50% weight)
        # 2. Average wear count per item (higher is better, indicating they get used, 30% weight)
        # 3. Sustainable fabrics like cotton, linen, wool vs synthetics like polyester, nylon (20% weight)
        avg_wears = sum(it["wear_count"] for it in items) / total_items
        wear_score = min(avg_wears * 10, 100)  # Caps at average 10 wears

        sustainable_fabrics = ["cotton", "wool", "linen", "silk", "denim"]
        sustainable_count = len([it for it in items if str(it["fabric"]).lower() in sustainable_fabrics])
        fabric_score = (sustainable_count / total_items) * 100

        sustainability_score = int((utilization_rate * 0.5) + (wear_score * 0.3) + (fabric_score * 0.2))
        sustainability_score = max(min(sustainability_score, 100), 10)  # Floor at 10, cap at 100

        return {
            "total_items": total_items,
            "worn_items": worn_items,
            "utilization_rate": round(utilization_rate, 1),
            "underused": underused,
            "overused": overused,
            "sustainability_score": sustainability_score
        }

    def generate_sustainability_report(self, stats: dict, api_key: str = None) -> str:
        """Calls Groq to write a personalized, encouraging sustainability advisory report."""
        if stats["total_items"] == 0:
            return "Upload clothes to your wardrobe to generate your first Wardrobe Sustainability Report!"

        underused_names = ", ".join([it["notes"] for it in stats["underused"][:3]])
        overused_names = ", ".join([it["notes"] for it in stats["overused"][:3]])

        prompt = (
            f"Write a brief, engaging sustainability report for the user's wardrobe:\n"
            f"- Total clothing items: {stats['total_items']}\n"
            f"- Wardrobe utilization rate: {stats['utilization_rate']}%\n"
            f"- Sustainability score: {stats['sustainability_score']}/100\n"
            f"- Underused clothes (rarely worn): {underused_names or 'None (Good job!)'}\n"
            f"- Most loved clothes (overused): {overused_names or 'None yet'}\n\n"
            f"Provide 2-3 specific, encouraging, actionable styling tips to increase utilization, "
            f"such as styling underused items in new ways. Keep the tone friendly, positive, and fashion-conscious."
        )

        return self.run(prompt, api_key=api_key)
