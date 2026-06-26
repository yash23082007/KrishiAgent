import os
import uuid
from jinja2 import Environment, FileSystemLoader
from agents.base_agent import BaseAgent
from tools.bhashini_tool import translate_text, text_to_speech
from models.agent_output import VoiceOutput
from utils.audio import upload_audio
from utils.logger import get_logger

logger = get_logger("voice_agent")

# Supported dialects and their display names
SUPPORTED_DIALECTS = {
    "hindi": "Hindi (हिंदी)",
    "english": "English",
    "marwari": "Marwari (मारवाड़ी)",
    "bhojpuri": "Bhojpuri (भोजपुरी)",
    "gujarati": "Gujarati (ગુજરાતી)",
    "telugu": "Telugu (తెలుగు)",
    "urdu": "Urdu (اردو)",
}


class VoiceAgent(BaseAgent):
    role = "Agri-Linguist Voice Advisor"
    goal = (
        "Formulate and translate factual agricultural advice into trusted "
        "regional audio voice notes that farmers can understand and act on."
    )
    backstory = (
        "Expert translator specializing in local Indian dialects and audio "
        "delivery. Understands the cultural nuances of Marwari, Bhojpuri, "
        "Gujarati, Telugu, Urdu and Hindi communication styles. Creates "
        "warm, respectful audio advisories that build farmer trust."
    )
    max_retries = 1
    output_schema = VoiceOutput

    async def think(self, **kwargs) -> str:
        """Reason about translation and voice synthesis approach."""
        data = kwargs.get("data", {})
        dialect = kwargs.get("dialect", "hindi")
        farmer_name = data.get("farmer_name", "Kisan Bhai")
        disease = data.get("disease", "unknown")
        weather_safe = data.get("weather_safe", True)

        dialect_name = SUPPORTED_DIALECTS.get(dialect, dialect)

        reasoning = (
            f"Preparing voice advisory for farmer '{farmer_name}' in {dialect_name}. "
            f"Disease: {disease}. Weather safe: {weather_safe}. "
            f"My approach: (1) Render the English advisory template with case variables "
            f"using Jinja2. (2) Translate the English text into {dialect_name} using "
            f"Gemini LLM with dialect-specific prompt engineering — ensuring the tone is "
            f"warm, respectful, and matches how a village elder would speak. "
        )

        if dialect == "urdu":
            reasoning += (
                f"(3) SPECIAL: Urdu output uses Nastaliq/Arabic script. "
                f"Will use 'ur' language code for TTS synthesis. "
            )
        elif dialect == "telugu":
            reasoning += (
                f"(3) SPECIAL: Telugu output uses Telugu script. "
                f"Will use 'te' language code for TTS synthesis. "
            )
        elif dialect == "english":
            reasoning += (
                f"(3) English mode — skip translation, synthesize directly. "
            )
        else:
            reasoning += (
                f"(3) Hindi/Devanagari script output. Using 'hi' TTS language code "
                f"which reads Devanagari dialects (including {dialect_name}) well. "
            )

        reasoning += (
            f"(4) Synthesize speech to OGG Opus audio file via gTTS/Bhashini. "
            f"(5) Upload to Cloudinary CDN (or local static) and return public URL."
        )
        return reasoning

    async def act(self, **kwargs) -> dict:
        """Render template, translate, and synthesize voice note."""
        data = kwargs.get("data", {})
        dialect = kwargs.get("dialect", "hindi")

        # 1. Setup Jinja2 environment and render template
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts"
        )
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("advisory_template.j2")

        # Render template in English first
        english_advisory = template.render(**data)

        # 2. Translate English text to target dialect
        translated_text = await translate_text(english_advisory, dialect)

        # 3. Create temp file for audio synthesis
        temp_audio_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "temp"
        )
        os.makedirs(temp_audio_dir, exist_ok=True)
        ogg_filename = f"voice_{uuid.uuid4().hex}.ogg"
        ogg_path = os.path.join(temp_audio_dir, ogg_filename)

        # Synthesize Speech
        success = await text_to_speech(translated_text, ogg_path, dialect)

        # Estimate duration as fallback
        duration_seconds = max(3, len(translated_text) // 12)

        if success and os.path.exists(ogg_path):
            try:
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
            audio_url = "/static/audio/default_fallback.ogg"

        return {
            "audio_url": audio_url,
            "audio_duration": duration_seconds,
            "translated_text": translated_text,
        }

    async def reflect(self, result: dict, thinking: str) -> str:
        """Self-assess the voice note quality."""
        text = result.get("translated_text", "")
        duration = result.get("audio_duration", 0)
        url = result.get("audio_url", "")

        if not text or text == "":
            return "⚠️ Translation produced empty text. Voice note may be silent."

        if "default_fallback" in url:
            return (
                "⚠️ Audio synthesis failed — using fallback audio. "
                "The text advisory was generated but TTS conversion had issues."
            )

        return (
            f"✅ Voice note generated successfully. "
            f"Duration: {duration}s. Text length: {len(text)} chars. "
            f"Audio hosted at: {url[:60]}..."
        )

    def _get_fallback_result(self, **kwargs) -> dict:
        """Fallback with default advisory text."""
        return {
            "audio_url": "/static/audio/default_fallback.ogg",
            "audio_duration": 0,
            "translated_text": "कृपया स्थानीय कृषि अधिकारी से सम्पर्क करें।",
        }

    def get_crewai_agent(self):
        """CrewAI agent initialization wrapper (if CrewAI is used)."""
        try:
            from crewai import Agent
            from crewai_tools import tool

            @tool("Render Advisory and Synthesize Dialect Audio")
            def crew_synthesize_voice(data_json: str, dialect: str) -> str:
                """Renders case variables into templates, translates, and synthesizes audio."""
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
                verbose=True,
            )
        except ImportError:
            return None
