from tools.weather_tool import fetch_weather_and_evaluate

class ClimateAgent:
    def __init__(self):
        self.role = "Agri-Meteorologist"
        self.goal = "Analyze local microclimates to suggest safe pesticide spraying windows."
        self.backstory = "Expert weather analyst specializing in micro-climatic impacts on agricultural operations."

    async def execute(self, lat: float, lon: float, is_fungal: bool = False) -> dict:
        """Runs the microclimate safety evaluation."""
        return await fetch_weather_and_evaluate(lat, lon, is_fungal)

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
                verbose=True
            )
        except ImportError:
            return None
