import os
import hashlib
from fastapi import APIRouter, Request, Response, BackgroundTasks, HTTPException
from models.message import SimulatorPayload
from orchestrator import PipelineOrchestrator
from utils.location import get_dialect_from_prefix
from utils.whatsapp import get_image_url
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
orchestrator = PipelineOrchestrator()

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "krishi_verify_token")

@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    WhatsApp Webhook Verification Endpoint.
    Meta hits this with a verification token when configuring webhooks.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            print("Webhook verified successfully by Meta.")
            return Response(content=challenge, media_type="text/plain")
        else:
            raise HTTPException(status_code=403, detail="Verification token mismatch")
    
    raise HTTPException(status_code=400, detail="Missing verification parameters")

async def run_async_pipeline(
    phone_hash: str,
    phone_prefix: str,
    image_url: str,
    lat: float,
    lon: float,
    dialect: str,
    farmer_name: str
):
    """Helper method to run the pipeline in a background thread."""
    try:
        resolved_url = await get_image_url(image_url)
        await orchestrator.run_pipeline(
            phone_hash=phone_hash,
            phone_prefix=phone_prefix,
            image_url=resolved_url,
            lat=lat,
            lon=lon,
            dialect=dialect,
            farmer_name=farmer_name
        )
    except Exception as e:
        print(f"Error running async pipeline from webhook: {e}")

@router.post("/webhook")
async def handle_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    """
    WhatsApp Incoming Message Webhook Endpoint.
    Processes photos and triggers the multi-agent pipeline asynchronously.
    """
    try:
        payload = await request.json()
        print(f"Incoming WhatsApp webhook payload: {payload}")
        
        # Parse fields from Meta schema
        entry = payload.get("entry", [])
        if not entry:
            return {"status": "ignored", "reason": "empty entry list"}
            
        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ignored", "reason": "empty changes list"}
            
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return {"status": "ignored", "reason": "no messages received"}
            
        message = messages[0]
        msg_type = message.get("type")
        from_phone = message.get("from")
        
        # Hash phone number for privacy
        phone_hash = hashlib.sha256(from_phone.encode()).hexdigest()
        phone_prefix = from_phone[:5] if from_phone else "91"
        dialect = get_dialect_from_prefix(from_phone)
        farmer_name = value.get("contacts", [{}])[0].get("profile", {}).get("name", "Kisan Bhai")

        if msg_type == "image":
            image_id = message["image"]["id"]
            
            # Resolve coordinates (if location shared, else fallback)
            # Location is sometimes shared in a separate message, we default to central coordinates
            # of Rajasthan for local demo (e.g. Sujangarh: 27.7011, 74.4712)
            lat, lon = 27.7011, 74.4712
            
            # Kick off multi-agent pipeline in background
            background_tasks.add_task(
                run_async_pipeline,
                phone_hash=phone_hash,
                phone_prefix=phone_prefix,
                image_url=image_id, # whatsapp.py handles fetching download link from ID
                lat=lat,
                lon=lon,
                dialect=dialect,
                farmer_name=farmer_name
            )
            
            return {"status": "accepted", "message": "processing pipeline in background"}
            
        elif msg_type == "location":
            # If the message contains location sharing, we save it in cache/session
            loc = message["location"]
            lat = loc["latitude"]
            lon = loc["longitude"]
            print(f"Received shared location for phone {from_phone}: {lat}, {lon}")
            return {"status": "accepted", "message": "location received"}

    except Exception as e:
        print(f"Error handling WhatsApp webhook: {e}")
        # Always return 200 so Meta doesn't retry spamming the endpoint
        return {"status": "error", "detail": str(e)}

    return {"status": "ignored", "reason": "message type not handled"}

@router.post("/api/simulator")
async def run_simulator(payload: SimulatorPayload):
    """
    Direct simulator endpoint.
    Triggers the multi-agent pipeline and returns the complete result immediately.
    """
    phone_hash = hashlib.sha256(payload.phone.encode()).hexdigest()
    phone_prefix = payload.phone[:5]
    
    # Coordinates default to Sujangarh if not provided
    lat = payload.latitude if payload.latitude is not None else 27.7011
    lon = payload.longitude if payload.longitude is not None else 74.4712
    
    try:
        # Run synchronously for the dashboard to get feedback instantly
        case_data = await orchestrator.run_pipeline(
            phone_hash=phone_hash,
            phone_prefix=phone_prefix,
            image_url=payload.image_url,
            lat=lat,
            lon=lon,
            dialect=payload.dialect,
            farmer_name=payload.name
        )
        return case_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline simulation failed: {e}")
