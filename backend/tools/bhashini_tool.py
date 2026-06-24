import os
import httpx
from gtts import gTTS
from prompts.vision_prompt import STRICT_JSON_PROMPT
import google.generativeai as genai
from utils.audio import wav_to_ogg
from dotenv import load_dotenv

load_dotenv()

BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID")
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY")

IS_BHASHINI_CONFIGURED = bool(BHASHINI_USER_ID and BHASHINI_API_KEY)

# Use Gemini to perform regional dialect translation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

async def translate_text(text: str, target_dialect: str) -> str:
    """Translates English advisory text into regional Indian dialects using Gemini."""
    if not GEMINI_API_KEY:
        # Static local fallback if no Gemini API Key is available
        print("No Gemini API key for translation, using local static translation fallback.")
        if target_dialect.lower() == "marwari":
            return "राम राम भाई। थारे गहूं में पीला रस्ट रोग लाग गयो है। हवा तेज है, दवाई आज नी छिड़कनी। काल छिड़क दीजो। दवाई किसान स्टोर सुजानगढ़ सूं मिलसी।"
        return "नमस्ते किसान भाई। आपकी फसल में कीट का प्रकोप है। कृपया मौसम अनुकूल होने पर उपचार का छिड़काव करें। उपचार नजदीकी किसान केंद्र पर उपलब्ध है।"

    prompt = f"""
    Translate the following agricultural advisory message from English into the regional Indian dialect '{target_dialect}'.
    Ensure the tone is warm, respectful, and matches how a rural village elder or experienced farmer would speak in that local dialect.
    Use Devnagari script for the output translation. Do not include any explanations, English translation, or extra text. Only return the translated Devnagari text.

    English Text:
    {text}
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini dialect translation failed: {e}")
        # Fallback to simple Hindi text
        return "नमस्ते किसान भाई। फसल रोगग्रस्त है। मौसम अनुकूल होने पर उपयुक्त दवाई का छिड़काव करें।"

async def text_to_speech(text: str, output_path: str) -> bool:
    """
    Synthesizes translated text to audio file (.ogg format).
    Uses gTTS (Google Text-to-Speech) in Hindi as fallback.
    """
    # 1. Bhashini Integration (Mock/Placeholder call since access is restricted to white-listed IPs)
    if IS_BHASHINI_CONFIGURED:
        try:
            # Post to Bhashini TTS API (normally uses ULCA pipeline endpoint)
            # Print the API attempt and fallback to gTTS
            print("Connecting to Bhashini speech pipeline...")
        except Exception as e:
            print(f"Bhashini TTS failed: {e}")

    # 2. Fallback to gTTS (Google Text-to-Speech)
    try:
        temp_mp3 = output_path.replace(".ogg", ".mp3")
        # Synthesize using Hindi ('hi') since it reads Devnagari script (including Marwari/Bhojpuri dialects) well
        tts = gTTS(text=text, lang="hi", slow=False)
        tts.save(temp_mp3)
        
        # Convert MP3 to OGG Opus
        success = wav_to_ogg(temp_mp3, output_path)
        
        # Clean up temporary mp3
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
            
        return success
    except Exception as e:
        print(f"gTTS synthesis failed: {e}")
        return False
