from pydantic import BaseModel
from typing import Optional


class BookingSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None


class BookingExtraction(BaseModel):
    booking_intent: bool = False
    name: Optional[str] = None
    email: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None