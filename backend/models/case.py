from pydantic import BaseModel
from typing import List, Optional, Any

class Case(BaseModel):
    id: Optional[str] = None
    wa_phone_hash: str
    wa_phone_prefix: Optional[str] = None
    image_url: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_pin: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    dialect: Optional[str] = "marwari"
    
    # Vision Output
    crop: Optional[str] = None
    disease: Optional[str] = None
    scientific_name: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None
    affected_area: Optional[int] = None
    symptoms: Optional[List[str]] = None
    urgency: Optional[str] = None
    
    # Climate Output
    weather_safe: Optional[bool] = None
    weather_reason: Optional[str] = None
    safe_spray_window: Optional[str] = None
    
    # Economic Output
    treatment_name: Optional[str] = None
    treatment_dose: Optional[str] = None
    treatment_price: Optional[int] = None
    subsidy_amount: Optional[int] = None
    net_cost: Optional[int] = None
    subsidy_scheme: Optional[str] = None
    dealer_name: Optional[str] = None
    dealer_phone: Optional[str] = None
    dealer_distance: Optional[float] = None
    
    # Voice Output
    audio_url: Optional[str] = None
    audio_duration: Optional[int] = None
    translated_text: Optional[str] = None
    
    # Metadata
    latency_ms: Optional[int] = None
    agent_trace: Optional[dict] = None
    needs_review: Optional[bool] = False
    created_at: Optional[str] = None
