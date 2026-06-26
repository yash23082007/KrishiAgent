import os
import hashlib
import time
from fastapi import APIRouter, Request, Response, BackgroundTasks, HTTPException
from models.message import SimulatorPayload
from orchestrator import PipelineOrchestrator
from utils.location import get_dialect_from_prefix
from utils.whatsapp import get_image_url
from db.redis_client import redis_client
from utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger("webhook")
router = APIRouter()
orchestrator = PipelineOrchestrator()

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "krishi_verify_token")

# Simple in-memory rate limiter (per phone hash)
_rate_limit_store: dict = {}
RATE_LIMIT_WINDOW = 30  # seconds between allowed requests per phone
MAX_REQUESTS_PER_WINDOW = 3


def _check_rate_limit(phone_hash: str) -> bool:
    """Returns True if request is allowed, False if rate-limited."""
    now = time.time()
    if phone_hash in _rate_limit_store:
        window_start, count = _rate_limit_store[phone_hash]
        if now - window_start < RATE_LIMIT_WINDOW:
            if count >= MAX_REQUESTS_PER_WINDOW:
                return False
            _rate_limit_store[phone_hash] = (window_start, count + 1)
            return True
    _rate_limit_store[phone_hash] = (now, 1)
    return True


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
            logger.info("Webhook verified successfully by Meta.")
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
    farmer_name: str,
):
    """Helper method to run the pipeline in a background thread with error handling."""
    try:
        resolved_url = await get_image_url(image_url)
        await orchestrator.run_pipeline(
            phone_hash=phone_hash,
            phone_prefix=phone_prefix,
            image_url=resolved_url,
            lat=lat,
            lon=lon,
            dialect=dialect,
            farmer_name=farmer_name,
        )
    except Exception as e:
        logger.error(f"Pipeline execution failed for {phone_hash[:8]}...: {e}")
        # Pipeline failures are caught gracefully — farmer gets no response
        # but we don't crash the server


@router.post("/webhook")
async def handle_whatsapp_message(
    request: Request, background_tasks: BackgroundTasks
):
    """
    WhatsApp Incoming Message Webhook Endpoint.
    Processes photos and location shares, links them via session state,
    and triggers the multi-agent pipeline asynchronously.
    """
    try:
        payload = await request.json()
        logger.info(f"Incoming WhatsApp webhook payload received")

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
        farmer_name = (
            value.get("contacts", [{}])[0]
            .get("profile", {})
            .get("name", "Kisan Bhai")
        )

        # Rate limit check
        if not _check_rate_limit(phone_hash):
            logger.warning(f"Rate limit exceeded for {phone_hash[:8]}...")
            return {"status": "rate_limited", "message": "too many requests"}

        if msg_type == "location":
            # Save location in session cache for the next image message
            loc = message["location"]
            lat = loc["latitude"]
            lon = loc["longitude"]

            # Store in Redis/InMemoryCache with 10-minute TTL
            session_key = f"session:{phone_hash}:location"
            redis_client.setex(
                session_key,
                600,  # 10 minutes
                f"{lat},{lon}",
            )
            logger.info(
                f"Location saved for {phone_hash[:8]}...: {lat}, {lon}"
            )
            return {"status": "accepted", "message": "location saved to session"}

        elif msg_type == "image":
            image_id = message["image"]["id"]

            # Try to retrieve saved location from session
            session_key = f"session:{phone_hash}:location"
            saved_location = redis_client.get(session_key)

            if saved_location:
                try:
                    lat_str, lon_str = saved_location.split(",")
                    lat, lon = float(lat_str), float(lon_str)
                    logger.info(
                        f"Using session location for {phone_hash[:8]}...: {lat}, {lon}"
                    )
                    # Clear the session location after use
                    redis_client.delete(session_key)
                except Exception:
                    lat, lon = 27.7011, 74.4712
            else:
                # Default to Rajasthan coordinates for demo
                lat, lon = 27.7011, 74.4712
                logger.info(
                    f"No session location for {phone_hash[:8]}..., using default"
                )

            # Kick off multi-agent pipeline in background
            background_tasks.add_task(
                run_async_pipeline,
                phone_hash=phone_hash,
                phone_prefix=phone_prefix,
                image_url=image_id,
                lat=lat,
                lon=lon,
                dialect=dialect,
                farmer_name=farmer_name,
            )

            return {
                "status": "accepted",
                "message": "processing pipeline in background",
            }

    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {e}")
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
            farmer_name=payload.name,
        )
        return case_data
    except Exception as e:
        logger.error(f"Pipeline simulation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Pipeline simulation failed: {e}"
        )
