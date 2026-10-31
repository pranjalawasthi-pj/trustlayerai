import re
from .config import settings

def fallback_parse(request: str) -> dict:
    text = request.lower()
    budget_match = re.search(r"(?:under|below|within|budget(?: of)?|₹|rs\.?)\s*₹?\s*([\d,]+)", text)
    if not budget_match:
        budget_match = re.search(r"₹\s*([\d,]+)", text)
    budget = float(budget_match.group(1).replace(",", "")) if budget_match else 70000.0
    ram_match = re.search(r"(\d+)\s*gb\s*ram", text)
    storage = "SSD" if "ssd" in text else None
    return {
        "category": "laptop" if "laptop" in text or "notebook" in text else "general",
        "max_budget": budget,
        "ram_gb": int(ram_match.group(1)) if ram_match else None,
        "storage_type": storage,
        "battery_preference": "good" if "battery" in text else None,
        "source": "deterministic_fallback"
    }

async def extract_intent(request: str) -> dict:
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            prompt = (
                "Extract shopping intent from the user request. Return ONLY JSON with keys "
                "category, max_budget (number in INR), ram_gb (number or null), "
                "storage_type (string or null), battery_preference (string or null). "
                "Do not recommend products or make security decisions. Request: " + request
            )
            response = model.generate_content(prompt)
            import json
            raw = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(raw)
            data["source"] = "gemini"
            return data
        except Exception:
            pass
    return fallback_parse(request)
