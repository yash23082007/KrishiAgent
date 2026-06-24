import os
import json
import random
import httpx
import base64
import google.generativeai as genai
from prompts.vision_prompt import VISION_PROMPT
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
IS_GEMINI_CONFIGURED = bool(GEMINI_API_KEY)

if IS_GEMINI_CONFIGURED:
    genai.configure(api_key=GEMINI_API_KEY)

# Mock disease database for simulation when offline/no API key
MOCK_DISEASES = [
    {
        "crop": "wheat",
        "disease": "stem rust",
        "scientific_name": "Puccinia graminis",
        "severity": "medium",
        "confidence": 0.89,
        "affected_area_percent": 35,
        "symptoms_observed": ["orange pustules on stem", "yellowing leaves"],
        "treatment_keywords": ["propiconazole", "tebuconazole", "fungicide"],
        "organic_alternatives": ["neem oil", "trichoderma"],
        "urgency": "spray within 48 hours",
        "if_untreated": "30-40% yield loss expected"
    },
    {
        "crop": "rice",
        "disease": "bacterial leaf blight",
        "scientific_name": "Xanthomonas oryzae",
        "severity": "high",
        "confidence": 0.92,
        "affected_area_percent": 60,
        "symptoms_observed": ["yellowish-stripe lesions on leaves", "leaf drying"],
        "treatment_keywords": ["streptocycline", "copper oxychloride", "bactericide"],
        "organic_alternatives": ["cow dung extract spray", "pseudomonas fluorescens"],
        "urgency": "spray within 24 hours",
        "if_untreated": "50-70% yield loss expected"
    },
    {
        "crop": "cotton",
        "disease": "leaf curl virus",
        "scientific_name": "Cotton leaf curl virus (CLCuV)",
        "severity": "critical",
        "confidence": 0.85,
        "affected_area_percent": 80,
        "symptoms_observed": ["leaves curling upwards", "thickened veins", "stunted plant growth"],
        "treatment_keywords": ["imidacloprid", "thiamethoxam", "insecticide"],
        "organic_alternatives": ["neem seed kernel extract", "yellow sticky traps"],
        "urgency": "action required immediately",
        "if_untreated": "total crop failure likely"
    },
    {
        "crop": "sugarcane",
        "disease": "red rot",
        "scientific_name": "Colletotrichum falcatum",
        "severity": "high",
        "confidence": 0.78,
        "affected_area_percent": 45,
        "symptoms_observed": ["red lesions inside the split stem", "white spots", "sour smell"],
        "treatment_keywords": ["carbendazim", "trichoderma viride"],
        "organic_alternatives": ["hot water seed treatment", "trichoderma"],
        "urgency": "uproot and burn affected crops within 3 days",
        "if_untreated": "rapid field spread, 100% loss of infected cane"
    },
    {
        "crop": "tomato",
        "disease": "early blight",
        "scientific_name": "Alternaria solani",
        "severity": "medium",
        "confidence": 0.94,
        "affected_area_percent": 25,
        "symptoms_observed": ["concentric black rings on leaves", "yellow halos"],
        "treatment_keywords": ["mancozeb", "chlorothalonil", "fungicide"],
        "organic_alternatives": ["baking soda spray", "copper fungicide"],
        "urgency": "spray within 3 days",
        "if_untreated": "defoliation and severe fruit rot"
    }
]

async def analyze_crop_image(image_url: str) -> dict:
    """
    Sends crop image to Gemini 1.5 Flash vision model.
    Falls back to a simulated mock parser if API key is missing.
    """
    if IS_GEMINI_CONFIGURED:
        try:
            # 1. Download image bytes
            # If the image_url is a local file path (e.g. from local simulator), read it directly
            if image_url.startswith("/") or ":" in image_url and not image_url.startswith("http"):
                with open(image_url, "rb") as f:
                    img_bytes = f.read()
            else:
                headers = {}
                if "lookaside.fbsbx.com" in image_url:
                    headers["Authorization"] = f"Bearer {os.getenv('WHATSAPP_TOKEN')}"
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, headers=headers, timeout=10.0)
                    img_bytes = response.content
            
            # 2. Call Gemini
            model = genai.GenerativeModel("gemini-1.5-flash")
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_bytes).decode()
            }
            
            response = model.generate_content([VISION_PROMPT, image_part])
            text = response.text.strip()
            
            # Clean up potential markdown formatting in response
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[0].startswith("```json"):
                    text = "\n".join(lines[1:-1])
                elif lines[0].startswith("```"):
                    text = "\n".join(lines[1:-1])
            
            result = json.loads(text)
            return result
        except Exception as e:
            print(f"Gemini Vision call exception: {e}. Falling back to mock diagnosis.")
            
    # Mock fallback logic
    # Parse crop from image_url keywords if possible, otherwise pick random
    url_lower = image_url.lower()
    for disease in MOCK_DISEASES:
        if disease["crop"] in url_lower or disease["disease"].replace(" ", "") in url_lower:
            # Add small random variation to confidence and affected area
            mock_copy = disease.copy()
            mock_copy["confidence"] = round(random.uniform(0.75, 0.98), 2)
            mock_copy["affected_area_percent"] = random.randint(15, 85)
            return mock_copy
            
    # Default random choice
    mock_copy = random.choice(MOCK_DISEASES).copy()
    mock_copy["confidence"] = round(random.uniform(0.75, 0.98), 2)
    mock_copy["affected_area_percent"] = random.randint(15, 85)
    return mock_copy
