import os
import httpx
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

IS_WHATSAPP_CONFIGURED = bool(WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID)

async def send_text(phone: str, text: str) -> bool:
    """Sends a text message to a farmer's WhatsApp number."""
    if IS_WHATSAPP_CONFIGURED:
        url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": text}
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code in [200, 201]:
                    return True
                print(f"WhatsApp send_text failed: {response.text}")
        except Exception as e:
            print(f"WhatsApp send_text exception: {e}")
            
    # Mock/Local simulator output
    print(f"[MOCK WHATSAPP SEND_TEXT] To: {phone} | Text: {text}")
    return True

async def send_audio(phone: str, audio_url: str) -> bool:
    """Sends an audio voice note (.ogg Opus) to a farmer's WhatsApp number."""
    if IS_WHATSAPP_CONFIGURED:
        url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "audio",
            "audio": {"link": audio_url}
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code in [200, 201]:
                    return True
                print(f"WhatsApp send_audio failed: {response.text}")
        except Exception as e:
            print(f"WhatsApp send_audio exception: {e}")
            
    # Mock/Local simulator output
    print(f"[MOCK WHATSAPP SEND_AUDIO] To: {phone} | Audio URL: {audio_url}")
    return True

async def get_image_url(image_id: str) -> str:
    """Fetches the actual media URL from Meta's API for download."""
    if IS_WHATSAPP_CONFIGURED:
        url = f"https://graph.facebook.com/v20.0/{image_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json().get("url")
        except Exception as e:
            print(f"WhatsApp get_image_url exception: {e}")
            
    # For local testing, the image_id itself might be a direct web URL
    return image_id
