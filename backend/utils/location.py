import httpx
from typing import Tuple, Dict, Any

async def resolve_location(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse geocodes lat/lon into district, state, and pin_code using Nominatim (OpenStreetMap).
    Includes a local offline mock fallback.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
    headers = {"User-Agent": "KrishiAgent/1.0"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                address = data.get("address", {})
                
                # Extract district, state, pincode
                district = address.get("district") or address.get("county") or address.get("city") or "Sujangarh"
                state = address.get("state") or "Rajasthan"
                postcode = address.get("postcode") or "331507"
                
                return {
                    "district": district,
                    "state": state,
                    "location_pin": postcode,
                    "lat": lat,
                    "lon": lon
                }
    except Exception as e:
        print(f"Nominatim lookup failed, using fallback: {e}")
        
    # Local demo fallback (e.g. Sujangarh, Churu, Rajasthan)
    return {
        "district": "Churu",
        "state": "Rajasthan",
        "location_pin": "331507",
        "lat": lat,
        "lon": lon
    }

def get_dialect_from_prefix(phone: str) -> str:
    """Guesses dialect based on phone number prefix or country code."""
    # Simple demo heuristics: Rajasthan numbers might use marwari, UP/Bihar might use bhojpuri
    # Default dialect mappings: marwari for Rajasthan, bhojpuri for East India, and hindi otherwise
    if phone.startswith("+919414") or phone.startswith("9414") or phone.startswith("+91800") or phone.startswith("800"):
        return "marwari"
    elif phone.startswith("+91993") or phone.startswith("993") or phone.startswith("+91700") or phone.startswith("700"):
        return "bhojpuri"
    return "hindi"
