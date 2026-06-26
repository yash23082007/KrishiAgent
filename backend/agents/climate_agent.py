from agents.base_agent import BaseAgent
from tools.weather_tool import fetch_weather_and_evaluate
from models.agent_output import ClimateOutput
from utils.logger import get_logger

logger = get_logger("climate_agent")


class ClimateAgent(BaseAgent):
    role = "Agri-Meteorologist"
    goal = "Analyze local microclimates to suggest safe pesticide spraying windows."
    backstory = (
        "Expert weather analyst specializing in micro-climatic impacts on "
        "agricultural operations, with deep knowledge of Indian monsoon patterns "
        "and their effect on chemical spray efficacy."
    )
    max_retries = 1
    output_schema = ClimateOutput

    async def think(self, **kwargs) -> str:
        """Reason about spray safety given location and disease context."""
        lat = kwargs.get("lat", 0)
        lon = kwargs.get("lon", 0)
        is_fungal = kwargs.get("is_fungal", False)

        reasoning = (
            f"Evaluating spray safety for coordinates ({lat:.4f}, {lon:.4f}). "
            f"My approach: (1) Fetch hourly weather forecast from Open-Meteo API. "
            f"(2) Check wind speed — above 15 km/h causes chemical drift, wasting pesticide. "
            f"(3) Check precipitation probability — rain above 40% will wash off applied chemicals. "
            f"(4) Check temperature extremes — above 38°C reduces absorption, below 10°C slows uptake. "
        )

        if is_fungal:
            reasoning += (
                f"(5) SPECIAL: Disease is fungal — high humidity (>85%) accelerates spore spread, "
                f"so spraying is URGENT even in suboptimal conditions. "
                f"Will apply fungal-specific humidity urgency rules."
            )
        else:
            reasoning += (
                f"(5) Standard pest/bacterial protocol — no special humidity rules needed."
            )

        return reasoning

    async def act(self, **kwargs) -> dict:
        """Fetch weather data and evaluate spray conditions."""
        lat = kwargs.get("lat", 27.7011)
        lon = kwargs.get("lon", 74.4712)
        is_fungal = kwargs.get("is_fungal", False)
        return await fetch_weather_and_evaluate(lat, lon, is_fungal)

    async def reflect(self, result: dict, thinking: str) -> str:
        """Self-assess the weather safety recommendation."""
        weather_safe = result.get("weather_safe", True)
        reason = result.get("weather_reason", "")
        window = result.get("safe_spray_window", "")

        if not weather_safe:
            return (
                f"⚠️ UNSAFE CONDITIONS DETECTED: {reason}. "
                f"Recommending farmer to wait until: {window}. "
                f"This guardrail prevents chemical waste and environmental runoff — "
                f"a critical environmental safety function."
            )
        return (
            f"✅ Safe spray conditions confirmed. {reason} "
            f"Farmer can proceed with treatment application {window.lower()}."
        )

    def _get_fallback_result(self, **kwargs) -> dict:
        """Conservative fallback: assume unsafe to err on caution side."""
        return {
            "weather_safe": False,
            "weather_reason": "Unable to fetch weather data. Defaulting to cautious advisory.",
            "safe_spray_window": "Tomorrow morning (6-8 AM) after conditions are verified",
        }

    def get_crewai_agent(self):
        """CrewAI agent initialization wrapper (if CrewAI is used)."""
        try:
            from crewai import Agent
            from crewai_tools import tool

            @tool("Evaluate Spray Safety")
            def crew_weather_evaluate(lat: float, lon: float, is_fungal: bool) -> str:
                """Fetches microclimate data and runs pesticide spray safety checks."""
                import asyncio
                res = asyncio.run(fetch_weather_and_evaluate(lat, lon, is_fungal))
                import json
                return json.dumps(res)

            return Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                tools=[crew_weather_evaluate],
                verbose=True,
            )
        except ImportError:
            return None
