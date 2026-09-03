from pydantic import BaseModel, EmailStr
from typing import Optional, List

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    session_id: str
    query: str
    answer: str
    booking_detected: bool = False
    booking_details: Optional[dict] = None