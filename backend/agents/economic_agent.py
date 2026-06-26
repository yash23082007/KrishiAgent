from typing import List
from agents.base_agent import BaseAgent
from tools.rag_tool import match_subsidy_and_supplier
from models.agent_output import EconomicOutput
from utils.logger import get_logger

logger = get_logger("economic_agent")


class EconomicAgent(BaseAgent):
    role = "Krishi Market Advisor"
    goal = (
        "Match pesticide recommendations to the lowest cost dealers "
        "and active government subsidies, maximizing farmer savings."
    )
    backstory = (
        "Expert in rural supply chains, eNAM trade, and agricultural "
        "subsidy programs across India. Knows every central and state "
        "government scheme that can reduce input costs for smallholder farmers."
    )
    max_retries = 1
    output_schema = EconomicOutput

    async def think(self, **kwargs) -> str:
        """Reason about subsidy matching and dealer selection strategy."""
        crop = kwargs.get("crop", "unknown")
        treatment_keywords = kwargs.get("treatment_keywords", [])
        lat = kwargs.get("lat", 0)
        lon = kwargs.get("lon", 0)

        reasoning = (
            f"Finding the most affordable treatment plan for {crop}. "
            f"Treatment keywords from Vision Agent: {', '.join(treatment_keywords)}. "
            f"My approach: (1) Search the product catalog for matching active ingredients "
            f"and their retail prices. "
            f"(2) Query the government subsidy database for schemes applicable to {crop} "
            f"and these specific chemicals — checking both central and state-level schemes. "
            f"(3) Calculate net cost after subsidy deduction. "
            f"(4) Find the nearest registered agri-dealer to coordinates "
            f"({lat:.4f}, {lon:.4f}) using haversine distance. "
            f"(5) Compile a cost-optimized recommendation with dealer contact info."
        )
        return reasoning

    async def act(self, **kwargs) -> dict:
        """Match treatments to subsidies and find nearest dealer."""
        crop = kwargs.get("crop", "wheat")
        treatment_keywords = kwargs.get("treatment_keywords", ["fungicide"])
        lat = kwargs.get("lat", 27.7011)
        lon = kwargs.get("lon", 74.4712)
        return await match_subsidy_and_supplier(crop, treatment_keywords, lat, lon)

    async def reflect(self, result: dict, thinking: str) -> str:
        """Self-assess the economic recommendation quality."""
        net_cost = result.get("net_cost", 0)
        subsidy = result.get("subsidy_amount", 0)
        scheme = result.get("subsidy_scheme", "None")
        dealer = result.get("dealer_name", "Unknown")
        distance = result.get("dealer_distance", 0)
        price = result.get("treatment_price", 0)

        savings_pct = (subsidy / price * 100) if price > 0 else 0

        reflection = (
            f"Treatment cost analysis complete. Retail: ₹{price} → "
            f"Net: ₹{net_cost} (saving ₹{subsidy}, {savings_pct:.0f}% subsidy). "
            f"Matched scheme: {scheme}. "
            f"Nearest dealer: {dealer} ({distance:.1f} km away). "
        )

        if distance > 20:
            reflection += (
                "⚠️ Dealer is far (>20km). Farmer may need transport assistance. "
            )
        if subsidy == 0:
            reflection += (
                "⚠️ No subsidy match found. Farmer pays full retail price. "
            )

        return reflection

    def _get_fallback_result(self, **kwargs) -> dict:
        """Fallback with generic pricing."""
        return {
            "treatment_name": "fungicide",
            "treatment_dose": "2g per liter",
            "treatment_price": 300,
            "subsidy_amount": 0,
            "net_cost": 300,
            "subsidy_scheme": "No matching scheme found",
            "dealer_name": "Local Kisan Store",
            "dealer_phone": "+91-00000-00000",
            "dealer_distance": 0.0,
        }

    def get_crewai_agent(self):
        """CrewAI agent initialization wrapper (if CrewAI is used)."""
        try:
            from crewai import Agent
            from crewai_tools import tool

            @tool("Match Subsidies and Dealers")
            def crew_match_subsidies(
                crop: str, treatment_keywords: List[str], lat: float, lon: float
            ) -> str:
                """Matches treatment inputs to cost subsidies and closest registered dealers."""
                import asyncio
                res = asyncio.run(
                    match_subsidy_and_supplier(crop, treatment_keywords, lat, lon)
                )
                import json
                return json.dumps(res)

            return Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                tools=[crew_match_subsidies],
                verbose=True,
            )
        except ImportError:
            return None
