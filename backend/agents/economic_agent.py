from typing import List
from tools.rag_tool import match_subsidy_and_supplier

class EconomicAgent:
    def __init__(self):
        self.role = "Krishi Market Advisor"
        self.goal = "Match pesticide recommendations to the lowest cost dealers and active government subsidies."
        self.backstory = "Expert in rural supply chains, eNAM trade, and agricultural subsidy programs."

    async def execute(self, crop: str, treatment_keywords: List[str], lat: float, lon: float) -> dict:
        """Matches treatments to government schemes and nearest agri-dealers."""
        return await match_subsidy_and_supplier(crop, treatment_keywords, lat, lon)

    def get_crewai_agent(self):
        """CrewAI agent initialization wrapper (if CrewAI is used)."""
        try:
            from crewai import Agent
            from crewai_tools import tool

            @tool("Match Subsidies and Dealers")
            def crew_match_subsidies(crop: str, treatment_keywords: List[str], lat: float, lon: float) -> str:
                """Matches treatment inputs to cost subsidies and closest registered dealers."""
                import asyncio
                res = asyncio.run(match_subsidy_and_supplier(crop, treatment_keywords, lat, lon))
                import json
                return json.dumps(res)

            return Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                tools=[crew_match_subsidies],
                verbose=True
            )
        except ImportError:
            return None
