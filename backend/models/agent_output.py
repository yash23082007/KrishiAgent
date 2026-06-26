from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class AgentReasoning(BaseModel):
    """Captures the reasoning trace from an autonomous agent."""
    thinking: str = ""
    reflection: str = ""
    retries: int = 0


class VisionOutput(BaseModel):
    crop: str = "unknown"
    disease: str = "unknown"
    scientific_name: Optional[str] = None
    severity: str = Field(default="low", description="low|medium|high|critical")
    confidence: float = 0.5
    affected_area_percent: int = 0
    symptoms_observed: List[str] = Field(default_factory=list)
    treatment_keywords: List[str] = Field(default_factory=list)
    organic_alternatives: List[str] = Field(default_factory=list)
    urgency: str = "monitor for 48 hours"
    if_untreated: str = "potential yield loss"
    _reasoning: Optional[Dict[str, Any]] = None


class ClimateOutput(BaseModel):
    weather_safe: bool = True
    weather_reason: str = "Good conditions. Spray now for best results."
    safe_spray_window: str = "Immediately"
    _reasoning: Optional[Dict[str, Any]] = None


class EconomicOutput(BaseModel):
    treatment_name: str = "fungicide"
    treatment_dose: str = "2g per liter"
    treatment_price: int = 300
    subsidy_amount: int = 0
    net_cost: int = 300
    subsidy_scheme: Optional[str] = None
    dealer_name: str = "Kisan Store"
    dealer_phone: str = "+91-00000-00000"
    dealer_distance: float = 0.0
    _reasoning: Optional[Dict[str, Any]] = None


class VoiceOutput(BaseModel):
    audio_url: str = ""
    audio_duration: int = 0
    translated_text: str = ""
    _reasoning: Optional[Dict[str, Any]] = None
