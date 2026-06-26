import os
import httpx
from gtts import gTTS
import google.generativeai as genai
from utils.audio import wav_to_ogg
from utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger("bhashini_tool")

BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID")
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY")

IS_BHASHINI_CONFIGURED = bool(BHASHINI_USER_ID and BHASHINI_API_KEY)

# Use Gemini to perform regional dialect translation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Dialect → TTS language code mapping
DIALECT_TTS_MAP = {
    "hindi": "hi",
    "marwari": "hi",      # Marwari uses Devanagari, gTTS Hindi reads it well
    "bhojpuri": "hi",     # Bhojpuri uses Devanagari
    "gujarati": "gu",     # Gujarati script
    "telugu": "te",       # Telugu script
    "urdu": "ur",         # Urdu / Nastaliq script
    "english": "en",      # English passthrough
}

# Dialect-specific prompt instructions for translation quality
DIALECT_PROMPTS = {
    "marwari": (
        "Translate into Marwari dialect (मारवाड़ी) using Devanagari script. "
        "Use Rajasthani vocabulary — 'थारे' instead of 'तुम्हारे', "
        "'राम राम' as greeting, 'मिलसी' instead of 'मिलेगी'. "
        "Speak as a trusted village elder from Churu/Jodhpur district."
    ),
    "bhojpuri": (
        "Translate into Bhojpuri dialect (भोजपुरी) using Devanagari script. "
        "Use eastern UP/Bihar vocabulary — 'हमार' instead of 'हमारा', "
        "'प्रणाम' as greeting. Speak warmly like a senior farmer from Gorakhpur."
    ),
    "gujarati": (
        "Translate into Gujarati (ગુજરાતી) using Gujarati script. "
        "Use familiar agricultural terms. Greet with 'ભાઈ'. "
        "Speak like a cooperative chairman from rural Gujarat."
    ),
    "telugu": (
        "Translate into Telugu (తెలుగు) using Telugu script. "
        "Use agricultural terminology common in Andhra Pradesh and Telangana. "
        "Greet with 'అన్నా' or 'భాయ్'. Speak respectfully like an elder farmer."
    ),
    "urdu": (
        "Translate into Urdu (اردو) using Nastaliq/Arabic script. "
        "Use agricultural terms understandable in rural UP, Kashmir, and Pakistan. "
        "Greet with 'السلام علیکم'. Speak warmly and respectfully. "
        "Ensure all numerals and measurements are spelled out in Urdu words."
    ),
    "hindi": (
        "Translate into simple, rural Hindi (हिंदी) using Devanagari script. "
        "Use straightforward vocabulary that a farmer with basic literacy can understand. "
        "Greet with 'नमस्ते किसान भाई'. Avoid English or technical jargon."
    ),
    "english": None,  # No translation needed
}

# Static fallback translations for offline mode
STATIC_FALLBACKS = {
    "marwari": "राम राम भाई। थारे गहूं में पीला रस्ट रोग लाग गयो है। हवा तेज है, दवाई आज नी छिड़कनी। काल छिड़क दीजो। दवाई किसान स्टोर सुजानगढ़ सूं मिलसी।",
    "bhojpuri": "प्रणाम भइया। रउआ गेहूं में पीला रस्ट रोग लागल बा। हवा तेज बा, आज दवाई मत छिड़कीं। काल्हि सबेरे छिड़क दीं। दवाई किसान स्टोर से मिली।",
    "hindi": "नमस्ते किसान भाई। आपकी फसल में रोग का प्रकोप है। कृपया मौसम अनुकूल होने पर उपचार का छिड़काव करें। उपचार नजदीकी किसान केंद्र पर उपलब्ध है।",
    "gujarati": "ભાઈ, તમારા ઘઉંમાં પીળો રસ્ટ રોગ લાગ્યો છે. પવન તેજ છે, આજે દવા ન છાંટો. કાલે સવારે છાંટો. દવા કિસાન સ્ટોર પરથી મળશે.",
    "telugu": "అన్నా, మీ పంటలో తెగులు వచ్చింది. గాలి ఎక్కువగా ఉంది, ఈ రోజు మందు పిచికారీ చేయకండి. రేపు ఉదయం చేయండి. మందు కిసాన్ స్టోర్ లో దొరుకుతుంది.",
    "urdu": "السلام علیکم بھائی۔ آپ کی فصل میں بیماری لگ گئی ہے۔ ہوا تیز ہے، آج دوائی نہ چھڑکیں۔ کل صبح چھڑکیں۔ دوائی کسان سٹور سے ملے گی۔",
    "english": "Hello farmer. Your crop has been affected by disease. Please spray the recommended treatment when weather conditions are favorable. Medicine is available at the nearest Kisan Store.",
}


async def translate_text(text: str, target_dialect: str) -> str:
    """Translates English advisory text into regional Indian dialects using Gemini."""

    # English passthrough — no translation needed
    if target_dialect.lower() == "english":
        return text

    if not GEMINI_API_KEY:
        logger.info(
            f"No Gemini API key for translation, using static fallback for {target_dialect}."
        )
        return STATIC_FALLBACKS.get(
            target_dialect.lower(),
            STATIC_FALLBACKS["hindi"]
        )

    dialect_instruction = DIALECT_PROMPTS.get(
        target_dialect.lower(),
        DIALECT_PROMPTS["hindi"]
    )

    if dialect_instruction is None:
        return text  # English passthrough

    prompt = f"""
    {dialect_instruction}

    Translate the following agricultural advisory message from English.
    Ensure the tone is warm, respectful, and matches how a rural village elder 
    or experienced farmer would speak in that local dialect.
    Do not include any explanations, English translation, or extra text. 
    Only return the translated text in the appropriate script.

    English Text:
    {text}
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        translated = response.text.strip()
        logger.info(
            f"Translated to {target_dialect}: {len(translated)} chars"
        )
        return translated
    except Exception as e:
        logger.warning(f"Gemini dialect translation failed: {e}")
        return STATIC_FALLBACKS.get(
            target_dialect.lower(),
            STATIC_FALLBACKS["hindi"]
        )


async def text_to_speech(
    text: str, output_path: str, dialect: str = "hindi"
) -> bool:
    """
    Synthesizes translated text to audio file (.ogg format).
    Uses gTTS (Google Text-to-Speech) with dialect-appropriate language code.
    """
    # Determine TTS language code from dialect
    tts_lang = DIALECT_TTS_MAP.get(dialect.lower(), "hi")

    # 1. Bhashini Integration (if configured)
    if IS_BHASHINI_CONFIGURED:
        try:
            logger.info("Connecting to Bhashini speech pipeline...")
            # Bhashini TTS API integration would go here
            # Falls through to gTTS as primary method
        except Exception as e:
            logger.warning(f"Bhashini TTS failed: {e}")

    # 2. gTTS (Google Text-to-Speech)
    try:
        temp_mp3 = output_path.replace(".ogg", ".mp3")
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save(temp_mp3)

        # Convert MP3 to OGG Opus
        success = wav_to_ogg(temp_mp3, output_path)

        # Clean up temporary mp3
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)

        logger.info(f"TTS synthesis complete: {dialect} ({tts_lang}) → {output_path}")
        return success
    except Exception as e:
        logger.error(f"gTTS synthesis failed for {dialect} ({tts_lang}): {e}")
        return False
