from agents.base_agent import StyleSphereAgent
import json
import os

class ImageAgent(StyleSphereAgent):
    def __init__(self):
        instruction = (
            "You are an expert AI fashion stylist and computer vision analyst. "
            "Your task is to analyze the provided image of a clothing item and return a structured JSON object containing key metadata. "
            "You must ensure the JSON complies EXACTLY with the requested fields. "
            "Do not include any formatting, markdown markers (like ```json), or text outside the JSON object itself."
        )
        super().__init__(
            name="Image Recognition Agent",
            instruction=instruction,
            model="gemini-2.5-flash"
        )

    def analyze_clothing_image(self, image_bytes: bytes, mime_type: str = "image/jpeg", api_key: str = None) -> dict:
        """Analyze clothing image using Gemini."""

        prompt = (
            "Carefully analyze this clothing image and extract the following properties. "
            "You must output a single, valid JSON object containing exactly these keys:\n"
            "{\n"
            "  \"category\": \"top\" | \"bottom\" | \"shoes\" | \"outer\" | \"dress\" | \"accessory\",\n"
            "  \"colors\": \"comma-separated list of dominant colors (e.g. navy blue, white)\",\n"
            "  \"pattern\": \"solid\" | \"striped\" | \"plaid\" | \"floral\" | \"graphic\" | \"dotted\" | \"animal print\" | \"camouflage\" | \"other\",\n"
            "  \"sleeve_type\": \"short\" | \"long\" | \"sleeveless\" | \"none\" | \"other\",\n"
            "  \"season_suitability\": \"comma-separated list of seasons (e.g. spring, summer, fall, winter) or all-season\",\n"
            "  \"fabric\": \"e.g. cotton, denim, leather, wool, polyester, silk, linen, knit, nylon, unknown\",\n"
            "  \"tags\": [\"array\", \"of\", \"3-5\", \"descriptive\", \"style/fashion\", \"tags\", \"e.g.\", \"casual\", \"athleisure\"],\n"
            "  \"notes\": \"A brief 1-2 sentence description highlighting style, fit, and key details.\"\n"
            "}\n"
            "Ensure the category, pattern, and sleeve_type fields strictly match one of the allowed options."
        )

        gemini_key = api_key or os.environ.get("GEMINI_API_KEY")

        response_text = self.run(
            prompt,
            api_key=gemini_key,
            json_mode=True,
            image_bytes=image_bytes,
            image_mime=mime_type
        )

        print("\n========== GEMINI RESPONSE ==========")
        print(response_text)
        print("=====================================\n")

        if response_text.startswith("Error"):
            raise Exception(response_text)

        try:
            clean_text = response_text.strip()

            if clean_text.startswith("```json"):
                clean_text = clean_text.replace("```json", "").replace("```", "").strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text.replace("```", "").strip()

            result = json.loads(clean_text)

            print("\n========== PARSED JSON ==========")
            print(result)
            print("=================================\n")

            return result

        except Exception as e:
            print("\n========== JSON PARSE ERROR ==========")
            print(e)
            print("Raw Response:")
            print(response_text)
            print("======================================\n")
            raise