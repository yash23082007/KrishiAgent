import os
import math
import json
import sqlite3
import difflib
from typing import Dict, Any, List
import google.generativeai as genai
from db.supabase_client import DB_PATH
from utils.logger import get_logger

logger = get_logger("rag_tool")

# Initialize genai if configured
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
IS_GEMINI_CONFIGURED = bool(GEMINI_API_KEY)
if IS_GEMINI_CONFIGURED:
    genai.configure(api_key=GEMINI_API_KEY)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates geodesic distance between two points in km."""
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# Hardcoded product catalog with average prices in INR
PRODUCT_PRICES = {
    "propiconazole": {"price": 360, "dosage": "2 ml per liter"},
    "tebuconazole": {"price": 420, "dosage": "1.5 ml per liter"},
    "fungicide": {"price": 300, "dosage": "2g per liter"},
    "streptocycline": {"price": 120, "dosage": "0.5g per liter"},
    "copper oxychloride": {"price": 280, "dosage": "3g per liter"},
    "bactericide": {"price": 150, "dosage": "2g per liter"},
    "imidacloprid": {"price": 350, "dosage": "0.5 ml per liter"},
    "thiamethoxam": {"price": 400, "dosage": "0.3g per liter"},
    "insecticide": {"price": 300, "dosage": "1.5 ml per liter"},
    "carbendazim": {"price": 180, "dosage": "2g per liter"},
    "mancozeb": {"price": 220, "dosage": "2.5g per liter"},
    "chlorothalonil": {"price": 380, "dosage": "2g per liter"},
    "neem oil": {"price": 150, "dosage": "5 ml per liter"},
    "trichoderma": {"price": 90, "dosage": "5g per liter"}
}

SUPPLIERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "knowledge_base", "suppliers.json"
)

def load_dealers() -> List[dict]:
    """Loads dealers from the knowledge base JSON file with fallback lists."""
    if os.path.exists(SUPPLIERS_FILE):
        try:
            with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading suppliers.json: {e}")
    # Fallback to hardcoded Churu district dealers
    return [
        {"name": "Kisan Bhandar Sujangarh", "phone": "+91-98765-43210", "latitude": 27.7011, "longitude": 74.4712},
        {"name": "Marwar Agri Inputs, Ratangarh", "phone": "+91-94140-12345", "latitude": 28.0823, "longitude": 74.6190},
        {"name": "Kalyan Krishi Kendra, Churu", "phone": "+91-96543-21098", "latitude": 28.2936, "longitude": 74.9649},
        {"name": "Salasar Seeds & Fertilizers", "phone": "+91-99887-76655", "latitude": 27.7286, "longitude": 74.7214}
    ]

def resolve_semantic_product(treatment_keywords: List[str]) -> str:
    """
    Resolves recommended treatment keywords to the most semantically similar 
    catalog product. Uses exact match, substring checks, fuzzy matching, 
    and LLM-based mapping fallback.
    """
    catalog_products = list(PRODUCT_PRICES.keys())
    
    cleaned_keywords = [kw.lower().strip() for kw in treatment_keywords if kw]
    if not cleaned_keywords:
        return "fungicide"
        
    # 1. Exact or substring match
    for kw in cleaned_keywords:
        for product in catalog_products:
            if product == kw or product in kw or kw in product:
                logger.info(f"RAG Semantic Match (Exact/Substring): {kw} -> {product}")
                return product

    # 2. Fuzzy match using difflib
    for kw in cleaned_keywords:
        matches = difflib.get_close_matches(kw, catalog_products, n=1, cutoff=0.5)
        if matches:
            logger.info(f"RAG Semantic Match (Fuzzy): {kw} -> {matches[0]}")
            return matches[0]

    # 3. LLM-based semantic matching fallback
    if IS_GEMINI_CONFIGURED:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"You are a semantic mapping agent. Map the following recommended treatment keywords from a crop diagnostic report: "
                f"{json.dumps(treatment_keywords)} to exactly one of the available catalog product names listed below.\n\n"
                f"Catalog Products:\n{json.dumps(catalog_products)}\n\n"
                f"Provide ONLY the matched product name from the list. If no product fits, respond with 'fungicide'."
            )
            response = model.generate_content(prompt)
            matched_product = response.text.strip().lower()
            
            if matched_product in PRODUCT_PRICES:
                logger.info(f"RAG Semantic Match (LLM): {matched_product}")
                return matched_product
        except Exception as e:
            logger.warning(f"RAG LLM semantic resolution failed: {e}")

    # Final fallback to standard fungicide
    return "fungicide"

async def match_subsidy_and_supplier(
    crop: str, 
    treatment_keywords: List[str], 
    lat: float, 
    lon: float
) -> dict:
    """
    RAG Tool to match treatment options to active government subsidies and find nearest dealers.
    Uses semantic match to map treatments and haversine formula for dealer distance.
    """
    # 1. Select the best matching treatment keyword via semantic search
    pesticide = resolve_semantic_product(treatment_keywords)
    price = PRODUCT_PRICES[pesticide]["price"]
    dosage = PRODUCT_PRICES[pesticide]["dosage"]
    
    # 2. Search Subsidies in SQLite database
    subsidy_amount = 0
    subsidy_scheme = "None"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subsidies WHERE active = 1")
        rows = cursor.fetchall()
        conn.close()
        
        best_subsidy = None
        for row in rows:
            sub = dict(row)
            
            # Check crop eligibility (if specified)
            crops = sub["eligible_crops"].split(",") if sub["eligible_crops"] else []
            if crops and not any(crop.lower() in c.lower() for c in crops):
                continue
                
            # Check input eligibility
            inputs = sub["eligible_inputs"].split(",") if sub["eligible_inputs"] else []
            if inputs and not any(pesticide.lower() in inp.lower() for inp in inputs):
                continue
                
            # Valid match! Check benefit
            best_subsidy = sub
            break
            
        if best_subsidy:
            subsidy_scheme = best_subsidy["scheme_name"]
            benefit = best_subsidy["benefit_type"].lower()
            max_amt = best_subsidy["amount_inr"]
            
            if "50%" in benefit:
                subsidy_amount = min(int(price * 0.5), max_amt)
            elif "40%" in benefit:
                subsidy_amount = min(int(price * 0.4), max_amt)
            elif "free" in benefit:
                subsidy_amount = price
            else:
                subsidy_amount = min(100, max_amt) # Default flat rate
    except Exception as e:
        logger.error(f"Error querying subsidies, using fallback rule: {e}")
        # Default fallback rule: 50% subsidy up to ₹150
        subsidy_amount = int(price * 0.5)
        subsidy_scheme = "Rashtriya Krishi Vikas Yojana (RKVY)"

    net_cost = max(0, price - subsidy_amount)

    # 3. Find closest dealer from suppliers knowledge base
    dealers = load_dealers()
    closest_dealer = dealers[0]
    min_distance = 999.0
    
    for dealer in dealers:
        dealer_lat = dealer.get("latitude") or dealer.get("lat") or 0.0
        dealer_lon = dealer.get("longitude") or dealer.get("lon") or 0.0
        dist = haversine_distance(lat, lon, dealer_lat, dealer_lon)
        if dist < min_distance:
            min_distance = dist
            closest_dealer = dealer

    return {
        "treatment_name": pesticide,
        "treatment_dose": dosage,
        "treatment_price": price,
        "subsidy_amount": subsidy_amount,
        "net_cost": net_cost,
        "subsidy_scheme": subsidy_scheme,
        "dealer_name": closest_dealer["name"],
        "dealer_phone": closest_dealer.get("phone", "+91-99999-99999"),
        "dealer_distance": min_distance
    }
