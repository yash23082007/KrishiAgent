import os
import uuid
from jinja2 import Environment, FileSystemLoader
from tools.bhashini_tool import translate_text, text_to_speech
from utils.audio import upload_audio

class VoiceAgent:
    def __init__(self):
        self.role = "Agri-Linguist Voice Advisor"
        self.goal = "Formulate and translate factual agricultural advice into trusted regional audio."
        self.backstory = "Expert translator specializing in local Indian dialects and audio delivery."

    async def execute(self, data: dict, dialect: str) -> dict:
        """
        Renders the advisory template, translates to local dialect, and synthesizes to OGG voice note.
        """
        # 1. Setup Jinja2 environment and render template
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("advisory_template.j2")
        
        # Render template in English first
        english_advisory = template.render(**data)
        
        # 2. Translate English text to target dialect
        translated_text = await translate_text(english_advisory, dialect)
        
        # 3. Create temp file for audio synthesis
        temp_audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
        os.makedirs(temp_audio_dir, exist_ok=True)
        ogg_filename = f"voice_{uuid.uuid4().hex}.ogg"
        ogg_path = os.path.join(temp_audio_dir, ogg_filename)
        
        # Synthesize Speech
        success = await text_to_speech(translated_text, ogg_path)
        
        # Estimate duration as fallback
        duration_seconds = max(3, len(translated_text) // 12) # Approximate speech speed: 12 chars/sec
        
        if success and os.path.exists(ogg_path):
            try:
                # Try to get actual duration if pydub is installed and working
                from pydub import AudioSegment
                sound = AudioSegment.from_file(ogg_path)
                duration_seconds = int(len(sound) / 1000)
            except Exception:
                pass
                
            # 4. Upload to Cloudinary or save to static files
            audio_url = upload_audio(ogg_path)
            
            # Clean up temp file
            try:
                os.remove(ogg_path)
            except Exception:
                pass
        else:
            # Fallback URL if synthesis completely failed
            audio_url = "/static/audio/default_fallback.ogg"
            
        return {
            "audio_url": audio_url,
            "audio_duration": duration_seconds,
            "translated_text": translated_text
        }

    def get_crewai_agent(self):
        """CrewAI agent initialization wrapper (if CrewAI is used)."""
        try:
            from crewai import Agent
            from crewai_tools import tool

            @tool("Render Advisory and Synthesize Dialect Audio")
            def crew_synthesize_voice(data_json: str, dialect: str) -> str:
                """Renders case variables into Jinja2 templates, translates, and synthesizes audio."""
                import asyncio
                import json
                data = json.loads(data_json)
                res = asyncio.run(self.execute(data, dialect))
                return json.dumps(res)

            return Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                tools=[crew_synthesize_voice],
                verbose=True
            )
        except ImportError:
            return None
