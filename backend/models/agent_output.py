from pydantic import BaseModel, Field
from typing import List, Optional

class VisionOutput(BaseModel):
    crop: str
    disease: str
    scientific_name: Optional[str] = None
    severity: str = Field(..., description="low|medium|high|critical")
    confidence: float
    affected_area_percent: int
    symptoms_observed: List[str]
    treatment_keywords: List[str]
    organic_alternatives: List[str]
    urgency: str
    if_untreated: str

class ClimateOutput(BaseModel):
    weather_safe: bool
    weather_reason: str
    safe_spray_window: str

class EconomicOutput(BaseModel):
    treatment_name: str
    treatment_dose: str
    treatment_price: int
    subsidy_amount: int
    net_cost: int
    subsidy_scheme: Optional[str] = None
    dealer_name: str
    dealer_phone: str
    dealer_distance: float

class VoiceOutput(BaseModel):
    audio_url: str
    audio_duration: int
    translated_text: str
