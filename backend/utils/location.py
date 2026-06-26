import httpx
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger("location")

# Expanded dialect mapping with phone prefix heuristics
# Covers major Indian telecom circles and regional codes
DIALECT_PREFIX_MAP = [
    # Rajasthan (Marwari)
    ("+919414", "marwari"), ("9414", "marwari"),
    ("+91800", "marwari"), ("800", "marwari"),
    ("+919460", "marwari"), ("9460", "marwari"),
    ("+919829", "marwari"), ("9829", "marwari"),
    # UP East / Bihar (Bhojpuri)
    ("+91993", "bhojpuri"), ("993", "bhojpuri"),
    ("+91700", "bhojpuri"), ("700", "bhojpuri"),
    ("+91954", "bhojpuri"), ("954", "bhojpuri"),
    ("+91631", "bhojpuri"), ("631", "bhojpuri"),
    # Gujarat (Gujarati)
    ("+91979", "gujarati"), ("979", "gujarati"),
    ("+91982", "gujarati"), ("982", "gujarati"),
    ("+91902", "gujarati"), ("902", "gujarati"),
    # Andhra Pradesh / Telangana (Telugu)
    ("+91984", "telugu"), ("984", "telugu"),
    ("+91939", "telugu"), ("939", "telugu"),
    ("+91900", "telugu"), ("900", "telugu"),
    ("+91770", "telugu"), ("770", "telugu"),
    ("+91636", "telugu"), ("636", "telugu"),
    # Kashmir / Pakistan codes (Urdu)
    ("+91194", "urdu"), ("194", "urdu"),
    ("+91962", "urdu"), ("962", "urdu"),
    ("+92", "urdu"),  # Pakistan country code
    ("+91796", "urdu"), ("796", "urdu"),
]


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

                district = (
                    address.get("district")
                    or address.get("county")
                    or address.get("city")
                    or "Sujangarh"
                )
                state = address.get("state") or "Rajasthan"
                postcode = address.get("postcode") or "331507"

                return {
                    "district": district,
                    "state": state,
                    "location_pin": postcode,
                    "lat": lat,
                    "lon": lon,
                }
    except Exception as e:
        logger.warning(f"Nominatim lookup failed, using fallback: {e}")

    # Local demo fallback (e.g. Sujangarh, Churu, Rajasthan)
    return {
        "district": "Churu",
        "state": "Rajasthan",
        "location_pin": "331507",
        "lat": lat,
        "lon": lon,
    }


def get_dialect_from_prefix(phone: str) -> str:
    """
    Guesses dialect based on phone number prefix or country code.
    Supports: Marwari, Bhojpuri, Gujarati, Telugu, Urdu, Hindi (default).
    """
    phone_clean = phone.replace("-", "").replace(" ", "")

    for prefix, dialect in DIALECT_PREFIX_MAP:
        if phone_clean.startswith(prefix):
            logger.info(f"Dialect detected from prefix {prefix}: {dialect}")
            return dialect

    # Default to Hindi
    return "hindi"
