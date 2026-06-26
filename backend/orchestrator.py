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
from utils.logger import get_logger

logger = get_logger("orchestrator")


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
        
        Lifecycle:
            1. Vision + Climate agents run in PARALLEL (asyncio.gather)
            2. Economic agent runs with outputs from both
            3. Voice agent renders, translates, and synthesizes audio
        
        Each agent goes through: think → act → validate → reflect
        with automatic retry and self-correction on failure.
        """
        start_time = time.time()
        agent_traces = {}

        # 0. Geocode/Resolve location details first
        loc_details = await resolve_location(lat, lon)
        district = loc_details.get("district", "Churu")
        state = loc_details.get("state", "Rajasthan")
        location_pin = loc_details.get("location_pin", "331507")

        logger.info(
            f"Pipeline started for farmer '{farmer_name}' | "
            f"Location: {district}, {state} | Dialect: {dialect}"
        )

        # ─── STAGE 1: Vision + Climate in PARALLEL ──────────────────────
        logger.info("Stage 1: Starting Vision and Climate Agents in parallel...")
        
        vision_task = self.vision_agent.execute_with_reasoning(image_url=image_url)
        climate_task = self.climate_agent.execute_with_reasoning(
            lat=lat, lon=lon, is_fungal=False
        )

        (vision_res, vision_trace), (climate_res, climate_trace) = await asyncio.gather(
            vision_task, climate_task
        )
        agent_traces["vision"] = vision_trace.to_dict()
        agent_traces["climate"] = climate_trace.to_dict()

        logger.info(
            f"Vision: {vision_res.get('crop', '?')}/{vision_res.get('disease', '?')} "
            f"(conf: {vision_res.get('confidence', 0):.0%}) | "
            f"Climate: {'SAFE' if climate_res.get('weather_safe') else 'UNSAFE'}"
        )

        # Conditional re-evaluation: if disease is fungal, re-check climate with fungal rules
        is_fungal = (
            "fungi" in str(vision_res.get("treatment_keywords", [])).lower()
            or "rust" in vision_res.get("disease", "").lower()
            or "blight" in vision_res.get("disease", "").lower()
        )
        if is_fungal and not climate_res.get("weather_safe"):
            logger.info(
                "Fungal disease detected + unsafe conditions — "
                "re-running Climate Agent with fungal urgency rules..."
            )
            climate_res, climate_trace = await self.climate_agent.execute_with_reasoning(
                lat=lat, lon=lon, is_fungal=True
            )
            agent_traces["climate"] = climate_trace.to_dict()

        # ─── STAGE 2: Economic Agent ────────────────────────────────────
        logger.info("Stage 2: Starting Economic Agent...")
        treatment_keywords = vision_res.get("treatment_keywords", ["fungicide"])
        crop = vision_res.get("crop", "wheat")

        economic_res, economic_trace = await self.economic_agent.execute_with_reasoning(
            crop=crop,
            treatment_keywords=treatment_keywords,
            lat=lat,
            lon=lon,
        )
        agent_traces["economic"] = economic_trace.to_dict()

        logger.info(
            f"Economic: ₹{economic_res.get('treatment_price', 0)} → "
            f"₹{economic_res.get('net_cost', 0)} "
            f"(subsidy: ₹{economic_res.get('subsidy_amount', 0)})"
        )

        # ─── STAGE 3: Voice Agent ──────────────────────────────────────
        logger.info("Stage 3: Starting Voice Agent...")
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
            "urgency": vision_res.get("urgency", "48 hours"),
        }

        voice_res, voice_trace = await self.voice_agent.execute_with_reasoning(
            data=advisory_data, dialect=dialect
        )
        agent_traces["voice"] = voice_trace.to_dict()

        logger.info(
            f"Voice: {voice_res.get('audio_duration', 0)}s audio in {dialect} dialect"
        )

        # ─── STAGE 4: Compile Case Record ──────────────────────────────
        latency_ms = int((time.time() - start_time) * 1000)
        case_id = str(uuid.uuid4())

        # Determine if case needs human expert review (confidence < 0.60)
        confidence = float(vision_res.get("confidence", 0.5))
        needs_review = confidence < 0.60

        # Extract reasoning summaries for the case record
        reasoning_summary = {
            "vision": vision_res.get("_reasoning", {}),
            "climate": climate_res.get("_reasoning", {}),
            "economic": economic_res.get("_reasoning", {}),
            "voice": voice_res.get("_reasoning", {}),
        }

        # Clean _reasoning from result dicts before saving
        for res in [vision_res, climate_res, economic_res, voice_res]:
            res.pop("_reasoning", None)

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
                "voice": voice_res,
                "reasoning": reasoning_summary,
                "execution_traces": agent_traces,
            },
        }

        # Save case record in Database (Supabase/SQLite)
        saved_case = await create_case(case_record)

        # Deliver Voice Note back to farmer via WhatsApp (if configured)
        await send_audio(phone_hash, voice_res.get("audio_url"))

        logger.info(
            f"Pipeline complete | Case: {case_id[:8]}... | "
            f"Latency: {latency_ms}ms | "
            f"Diagnosis: {crop}/{vision_res.get('disease')} | "
            f"Review needed: {needs_review}"
        )

        return saved_case
