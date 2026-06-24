import os
import uuid
import shutil
from dotenv import load_dotenv

load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

IS_CLOUDINARY_CONFIGURED = bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

if IS_CLOUDINARY_CONFIGURED:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

STATIC_AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "audio")
os.makedirs(STATIC_AUDIO_DIR, exist_ok=True)

def wav_to_ogg(input_wav_path: str, output_ogg_path: str) -> bool:
    """
    Converts a WAV or MP3 file to OGG Opus format.
    Falls back to a simple file copy if pydub/ffmpeg fails.
    """
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_file(input_wav_path)
        # Export as ogg with opus codec
        sound.export(output_ogg_path, format="ogg", codec="libopus")
        return True
    except Exception as e:
        print(f"pydub/ffmpeg audio conversion failed, falling back to simple file copy: {e}")
        try:
            # Just copy file to destination (WhatsApp and browsers might still be able to play it depending on browser capabilities)
            shutil.copy(input_wav_path, output_ogg_path)
            return True
        except Exception as e2:
            print(f"Fallback file copy failed: {e2}")
            return False

def save_audio_locally(temp_audio_path: str) -> str:
    """Saves the audio to static folder and returns local URL."""
    filename = f"audio_{uuid.uuid4().hex}.ogg"
    dest_path = os.path.join(STATIC_AUDIO_DIR, filename)
    shutil.copy(temp_audio_path, dest_path)
    # Return local URL path
    return f"/static/audio/{filename}"

def upload_audio(file_path: str) -> str:
    """
    Uploads audio to Cloudinary or saves locally.
    Returns the public web URL.
    """
    if IS_CLOUDINARY_CONFIGURED:
        try:
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="video", # Cloudinary handles audio files as video
                folder="krishiagent/audio",
                format="ogg"
            )
            return result.get("secure_url") or result.get("url")
        except Exception as e:
            print(f"Cloudinary upload failed, falling back to local: {e}")
            
    # Fallback: Save in FastAPI static folder and return simulated web link
    local_path = save_audio_locally(file_path)
    # The caller will prefix the server host e.g. http://localhost:8000
    return local_path
