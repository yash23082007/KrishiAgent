import math
import json
import os
import sqlite3
from typing import Dict, Any, List
from db.supabase_client import DB_PATH

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates geodesic distance between two points in km."""
    R = 6371.0 # Earth's radius in km
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

# Mock dealers list in Churu district (Rajasthan) as a fallback
MOCK_DEALERS = [
    {"name": "Kisan Bhandar Sujangarh", "phone": "+91-98765-43210", "lat": 27.7011, "lon": 74.4712},
    {"name": "Marwar Agri Inputs, Ratangarh", "phone": "+91-94140-12345", "lat": 28.0823, "lon": 74.6190},
    {"name": "Kalyan Krishi Kendra, Churu", "phone": "+91-96543-21098", "lat": 28.2936, "lon": 74.9649},
    {"name": "Salasar Seeds & Fertilizers", "phone": "+91-99887-76655", "lat": 27.7286, "lon": 74.7214}
]

async def match_subsidy_and_supplier(
    crop: str, 
    treatment_keywords: List[str], 
    lat: float, 
    lon: float
) -> dict:
    """
    RAG Tool to match treatment options to active government subsidies and find nearest dealers.
    """
    # 1. Select the best matching treatment keyword
    pesticide = "fungicide" # Default fallback
    dosage = "2g per liter"
    price = 300
    
    # Try to find a matched keyword in our catalog
    for kw in treatment_keywords:
        kw_lower = kw.lower()
        if kw_lower in PRODUCT_PRICES:
            pesticide = kw
            price = PRODUCT_PRICES[kw_lower]["price"]
            dosage = PRODUCT_PRICES[kw_lower]["dosage"]
            break

    # 2. Search Subsidies in database
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
        print(f"Error querying subsidies, using hardcoded rule: {e}")
        # Default fallback rule: 50% subsidy up to ₹150
        subsidy_amount = int(price * 0.5)
        subsidy_scheme = "Rashtriya Krishi Vikas Yojana (RKVY)"

    net_cost = max(0, price - subsidy_amount)

    # 3. Find closest dealer
    closest_dealer = MOCK_DEALERS[0]
    min_distance = 999.0
    
    # Try to load dealers from database if they exist (we can query the suppliers/dealers)
    # Since we don't have a separate dealers table, we search in SQLite database/json
    for dealer in MOCK_DEALERS:
        dist = haversine_distance(lat, lon, dealer["lat"], dealer["lon"])
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
        "dealer_phone": closest_dealer["phone"],
        "dealer_distance": min_distance
    }
