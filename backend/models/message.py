from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Profile(BaseModel):
    name: Optional[str] = None

class Contact(BaseModel):
    profile: Profile
    wa_id: str

class ImageMedia(BaseModel):
    id: str
    mime_type: str
    sha256: str

class LocationMedia(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None

class MessageText(BaseModel):
    body: str

class MessageItem(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[MessageText] = None
    image: Optional[ImageMedia] = None
    location: Optional[LocationMedia] = None

class Value(BaseModel):
    messaging_product: str
    metadata: dict
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[MessageItem]] = None

class Change(BaseModel):
    value: Value
    field: str

class EntryItem(BaseModel):
    id: str
    changes: List[Change]

class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[EntryItem]

# Simulator direct test payload
class SimulatorPayload(BaseModel):
    phone: str
    name: str
    image_url: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    dialect: Optional[str] = "marwari"
