import os
import base64
import json
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_shared_groq_client = None

def get_groq_client(api_key: str = None) -> Groq:
    global _shared_groq_client
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not set.")
    if _shared_groq_client is None or _shared_groq_client.api_key != key:
        _shared_groq_client = Groq(api_key=key)
    return _shared_groq_client

def get_shared_client(api_key: str = None) -> Groq:
    return get_groq_client(api_key)

class StyleSphereAgent:
    """मल्टी-मॉडल बेस एजेंट: जो Groq और Gemini दोनों को सपोर्ट करता है।"""
    def __init__(self, name: str, instruction: str, model: str = "llama-3.3-70b-versatile"):
        self.name = name
        self.instruction = instruction
        self.model = model

    def run(self, prompt: str, api_key: str = None, json_mode: bool = False, image_bytes: bytes = None, image_mime: str = None) -> str:
        # रास्ता A: अगर मॉडल जेमिनी है, तो सीधे Google API को कॉल करो
        if "gemini" in self.model.lower():
            key = api_key or os.environ.get("GEMINI_API_KEY")
            if key:
                key = key.strip('"\'')
            if not key:
                print("[DEBUG] Gemini API key is missing or not set.")
                return "Error: GEMINI_API_KEY is not set."
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={key}"
            headers = {"Content-Type": "application/json"}
            
            user_parts = [{"text": str(prompt)}]
            if image_bytes:
                encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                user_parts.append({
                    "inlineData": {"mimeType": image_mime or "image/jpeg", "data": encoded_image}
                })
                
            payload = {
                "contents": [{"role": "user", "parts": user_parts}],
                "system_instruction": {"parts": [{"text": self.instruction}]},
                "generationConfig": {"temperature": 0.2 if json_mode else 0.7}
            }
            if json_mode:
                payload["generationConfig"]["responseMimeType"] = "application/json"
                
            # Log debug information
            redacted_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key=REDACTED"
            print(f"\n[DEBUG] Gemini API URL: {redacted_url}")
            print(f"[DEBUG] Gemini Headers: {headers}")
            
            # Log payload structure without printing raw image bytes
            log_payload = json.loads(json.dumps(payload))
            if image_bytes:
                for part in log_payload["contents"][0]["parts"]:
                    if "inlineData" in part:
                        part["inlineData"]["data"] = part["inlineData"]["data"][:50] + "... [TRUNCATED IMAGE DATA]"
            print(f"[DEBUG] Gemini Request Payload: {json.dumps(log_payload, indent=2)}")
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                print(f"[DEBUG] Gemini Response Status Code: {response.status_code}")
                print(f"[DEBUG] Gemini Response Body: {response.text}")
                
                if response.status_code == 200:
                    resp_json = response.json()
                    try:
                        return resp_json['candidates'][0]['content']['parts'][0]['text']
                    except (KeyError, IndexError) as parse_err:
                        print(f"[DEBUG] Failed to parse Gemini response structure: {parse_err}")
                        return f"Error: Failed to parse Gemini response candidates structure. Response: {response.text}"
                return f"Error: Gemini API error {response.status_code}. Response: {response.text}"
            except Exception as e:
                print(f"[DEBUG] Exception connecting to Gemini: {str(e)}")
                return f"Error connecting to Gemini: {str(e)}"

        # रास्ता B: बाकी सभी चीजों के लिए Groq का इस्तेमाल करो
        else:
            try:
                client = get_groq_client(api_key)
            except ValueError as e:
                return f"Error: {str(e)}"
                
            messages = [
                {"role": "system", "content": self.instruction},
                {"role": "user", "content": prompt}
            ]
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.4 if json_mode else 0.7,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
                
            try:
                response = client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                return f"Error running Groq model {self.model}: {str(e)}"