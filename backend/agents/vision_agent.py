from tools.gemini_tool import analyze_crop_image
from models.agent_output import VisionOutput

class VisionAgent:
    def __init__(self):
        self.role = "Dr. Krishi Crop Pathologist"
        self.goal = "Accurately diagnose crop diseases from images and recommend active ingredients."
        self.backstory = "An expert Indian agricultural scientist with 30 years of field pathology experience."

    async def execute(self, image_url: str) -> dict:
        """Runs the vision diagnostic pipeline."""
        result = await analyze_crop_image(image_url)
        # Ensure result has default fields if something was missing
        if "crop" not in result:
            result["crop"] = "wheat"
        if "disease" not in result:
            result["disease"] = "unknown"
        if "severity" not in result:
            result["severity"] = "low"
        if "confidence" not in result:
            result["confidence"] = 0.5
        return result

    def get_crewai_agent(self):
        """CrewAI agent initialization wrapper (if CrewAI is used)."""
        try:
            from crewai import Agent
            from crewai_tools import tool
            
            # Wrap tool for CrewAI compatibility
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
                verbose=True
            )
        except ImportError:
            return None
