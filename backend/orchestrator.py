import time
import asyncio
import uuid
import json
from datetime import datetime
from agents.vision_agent import VisionAgent
from agents.climate_agent import ClimateAgent
from agents.economic_agent import EconomicAgent
from agents.voice_agent import VoiceAgent
from utils.location import resolve_location
from utils.whatsapp import send_audio
from db.queries import create_case

class PipelineOrchestrator:
    def __init__(self):
        self.vision_agent = VisionAgent()
        self.climate_agent = ClimateAgent()
        self.economic_agent = EconomicAgent()
        self.voice_agent = VoiceAgent()

    async def run_pipeline(
        self,
        phone_hash: str,
        phone_prefix: str,
        image_url: str,
        lat: float,
        lon: float,
        dialect: str = "marwari",
        farmer_name: str = "Kisan Bhai"
    ) -> dict:
        """
        Coordinates the execution of the 4-agent autonomous pipeline.
        Task 1 (Vision) & Task 2 (Climate) run in parallel.
        Task 3 (Economic) runs next.
        Task 4 (Voice) runs last.
        """
        start_time = time.time()
        
        # 0. Geocode/Resolve location details first
        loc_details = await resolve_location(lat, lon)
        district = loc_details.get("district", "Churu")
        state = loc_details.get("state", "Rajasthan")
        location_pin = loc_details.get("location_pin", "331507")

        # 1. Run Vision & Climate agents in parallel
        # Note: Climate agent needs to know if the crop disease is fungal to apply specific humidity rules.
        # However, since they run in parallel, we'll fetch the general weather first and update later if needed.
        print("Starting Vision and Climate Agents in parallel...")
        vision_task = self.vision_agent.execute(image_url)
        climate_task = self.climate_agent.execute(lat, lon, is_fungal=False)
        
        vision_res, climate_res = await asyncio.gather(vision_task, climate_task)
        print("Vision & Climate Agents complete.")
        
        # If disease is fungal, we could recheck climate, but general rules already apply.
        is_fungal = "fungi" in str(vision_res.get("treatment_keywords", [])).lower() or "rust" in vision_res.get("disease", "").lower()
        if is_fungal and not climate_res.get("weather_safe"):
            # Update climate check with fungal rules if needed
            climate_res = await self.climate_agent.execute(lat, lon, is_fungal=True)

        # 2. Run Economic Agent
        print("Starting Economic Agent...")
        treatment_keywords = vision_res.get("treatment_keywords", ["fungicide"])
        crop = vision_res.get("crop", "wheat")
        
        economic_res = await self.economic_agent.execute(
            crop=crop,
            treatment_keywords=treatment_keywords,
            lat=lat,
            lon=lon
        )
        print("Economic Agent complete.")

        # 3. Run Voice Agent
        print("Starting Voice Agent...")
        # Prepare combined variables to render the template
        advisory_data = {
            "farmer_name": farmer_name,
            "crop": crop,
            "disease": vision_res.get("disease", "unknown rust"),
            "severity": vision_res.get("severity", "medium"),
            "weather_safe": climate_res.get("weather_safe", True),
            "weather_reason": climate_res.get("weather_reason", ""),
            "safe_spray_window": climate_res.get("safe_spray_window", "Immediately"),
            "treatment_name": economic_res.get("treatment_name", "Fungicide"),
            "treatment_dose": economic_res.get("treatment_dose", "2g per liter"),
            "net_cost": economic_res.get("net_cost", 150),
            "dealer_name": economic_res.get("dealer_name", "Kisan Store"),
            "dealer_distance": economic_res.get("dealer_distance", 5.0),
            "dealer_phone": economic_res.get("dealer_phone", "+91-98765-43210"),
            "organic_alternatives": vision_res.get("organic_alternatives", ["neem oil"]),
            "urgency": vision_res.get("urgency", "48 hours")
        }

        voice_res = await self.voice_agent.execute(advisory_data, dialect)
        print("Voice Agent complete.")

        # 4. Measure total latency
        latency_ms = int((time.time() - start_time) * 1000)

        # 5. Populate Case document
        case_id = str(uuid.uuid4())
        
        # Determine if case needs human expert review (confidence < 0.60)
        confidence = float(vision_res.get("confidence", 0.5))
        needs_review = confidence < 0.60

        case_record = {
            "id": case_id,
            "wa_phone_hash": phone_hash,
            "wa_phone_prefix": phone_prefix,
            "image_url": image_url,
            "location_lat": lat,
            "location_lon": lon,
            "location_pin": location_pin,
            "district": district,
            "state": state,
            "dialect": dialect,
            
            # Vision
            "crop": crop,
            "disease": vision_res.get("disease"),
            "scientific_name": vision_res.get("scientific_name"),
            "severity": vision_res.get("severity"),
            "confidence": confidence,
            "affected_area": vision_res.get("affected_area_percent"),
            "symptoms": vision_res.get("symptoms_observed", []),
            "urgency": vision_res.get("urgency"),
            
            # Climate
            "weather_safe": climate_res.get("weather_safe"),
            "weather_reason": climate_res.get("weather_reason"),
            "safe_spray_window": climate_res.get("safe_spray_window"),
            
            # Economic
            "treatment_name": economic_res.get("treatment_name"),
            "treatment_dose": economic_res.get("treatment_dose"),
            "treatment_price": economic_res.get("treatment_price"),
            "subsidy_amount": economic_res.get("subsidy_amount"),
            "net_cost": economic_res.get("net_cost"),
            "subsidy_scheme": economic_res.get("subsidy_scheme"),
            "dealer_name": economic_res.get("dealer_name"),
            "dealer_phone": economic_res.get("dealer_phone"),
            "dealer_distance": economic_res.get("dealer_distance"),
            
            # Voice
            "audio_url": voice_res.get("audio_url"),
            "audio_duration": voice_res.get("audio_duration"),
            "translated_text": voice_res.get("translated_text"),
            
            # Metadata
            "latency_ms": latency_ms,
            "needs_review": needs_review,
            "agent_trace": {
                "vision": vision_res,
                "climate": climate_res,
                "economic": economic_res,
                "voice": voice_res
            }
        }

        # 6. Save case record in Database (Supabase/SQLite)
        saved_case = await create_case(case_record)

        # 7. Deliver Voice Note back to farmer via WhatsApp (if configured)
        # Note: If audio_url is local (e.g. "/static/audio/foo.ogg"), we append host during api response,
        # but for Meta API we send the full public URL or mock it.
        await send_audio(phone_hash, voice_res.get("audio_url"))

        return saved_case
