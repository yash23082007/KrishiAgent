from agents.base_agent import BaseAgent
from tools.gemini_tool import analyze_crop_image
from models.agent_output import VisionOutput
from utils.logger import get_logger

logger = get_logger("vision_agent")


class VisionAgent(BaseAgent):
    role = "Dr. Krishi Crop Pathologist"
    goal = "Accurately diagnose crop diseases from images and recommend active ingredients."
    backstory = (
        "An expert Indian agricultural scientist with 30 years of field "
        "pathology experience across wheat, rice, cotton, sugarcane, and vegetables."
    )
    max_retries = 2
    output_schema = VisionOutput

    async def think(self, **kwargs) -> str:
        """Reason about the image before analyzing it."""
        image_url = kwargs.get("image_url", "")
        _retry = kwargs.get("_retry_attempt", 0)
        _last_error = kwargs.get("_last_error", "")

        reasoning = (
            f"I am analyzing a crop disease image from URL: {image_url[:80]}... "
            f"My approach: (1) Identify the crop species from leaf morphology and color. "
            f"(2) Detect visible disease symptoms — pustules, lesions, discoloration, curling, spots. "
            f"(3) Cross-reference symptoms with known pathogens in my 30-year field database. "
            f"(4) Assess severity from affected leaf area percentage. "
            f"(5) Recommend chemical and organic countermeasures with urgency level."
        )

        if _retry > 0:
            reasoning += (
                f" SELF-CORRECTION: Previous attempt failed ({_last_error}). "
                f"Switching to stricter JSON output mode and reducing response complexity."
            )

        return reasoning

    async def act(self, **kwargs) -> dict:
        """Execute Gemini Vision analysis on the crop image."""
        image_url = kwargs.get("image_url", "")
        strict_mode = kwargs.get("_strict_mode", False)
        result = await analyze_crop_image(image_url, strict_mode=strict_mode)
        return result

    async def reflect(self, result: dict, thinking: str) -> str:
        """Self-assess the quality of the diagnosis."""
        confidence = result.get("confidence", 0)
        disease = result.get("disease", "unknown")
        crop = result.get("crop", "unknown")
        severity = result.get("severity", "unknown")
        treatments = result.get("treatment_keywords", [])

        if confidence < 0.5:
            return (
                f"LOW CONFIDENCE ({confidence:.0%}): Identified {crop} with possible "
                f"{disease}, but I am not confident. The image may be blurry, non-crop, "
                f"or showing a disease outside my training data. Flagging for human expert review."
            )
        elif confidence < 0.7:
            return (
                f"MODERATE CONFIDENCE ({confidence:.0%}): Detected {disease} on {crop} "
                f"({severity} severity). Treatments suggested: {', '.join(treatments[:2])}. "
                f"Recommend farmer sends a closer, well-lit photo for confirmation."
            )
        else:
            return (
                f"HIGH CONFIDENCE ({confidence:.0%}): Positively identified {disease} "
                f"(severity: {severity}) on {crop}. Affected area: "
                f"{result.get('affected_area_percent', '?')}%. "
                f"Recommended active ingredients: {', '.join(treatments)}. "
                f"Urgency: {result.get('urgency', 'N/A')}."
            )

    def _get_fallback_result(self, **kwargs) -> dict:
        """Return safe fallback if all retries fail."""
        return {
            "crop": "unknown",
            "disease": "unidentified pathology",
            "scientific_name": None,
            "severity": "medium",
            "confidence": 0.3,
            "affected_area_percent": 0,
            "symptoms_observed": ["unable to analyze image"],
            "treatment_keywords": ["fungicide"],
            "organic_alternatives": ["neem oil"],
            "urgency": "consult local agricultural officer",
            "if_untreated": "potential yield loss — seek expert advice",
        }

    def get_crewai_agent(self):
        """CrewAI agent initialization wrapper (if CrewAI is used)."""
        try:
            from crewai import Agent
            from crewai_tools import tool

            @tool("Crop Pathologist Image Analysis")
            def crew_analyze_crop(image_url: str) -> str:
                """Analyzes crop image from URL and returns structured JSON."""
                import asyncio
                res = asyncio.run(analyze_crop_image(image_url))
                import json
                return json.dumps(res)

            return Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                tools=[crew_analyze_crop],
                verbose=True,
            )
        except ImportError:
            return None
