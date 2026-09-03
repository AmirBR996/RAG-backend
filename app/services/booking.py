import uuid
import re
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import InterviewBooking
from app.schemas.booking import BookingSchema

def parse_booking_intent_with_llm(user_input: str) -> Optional[BookingSchema]:
    """
    Simulates tool calling/structured output extraction for booking details.
    Uses regex rule-based extraction or LLM structuring logic.
    """
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_input)
    date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}(st|nd|rd|th)?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b', user_input, re.I)
    time_match = re.search(r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)\b', user_input)
    
    if "book" in user_input.lower() or "interview" in user_input.lower():
        if email_match and date_match and time_match:
            # Fallback name extraction logic if not explicitly identified
            return BookingSchema(
                name="Applicant",
                email=email_match.group(0),
                date=date_match.group(0),
                time=time_match.group(0)
            )
    return None

def save_booking(db: Session, session_id: str, booking_data: BookingSchema) -> InterviewBooking:
    booking = InterviewBooking(
        id=str(uuid.uuid4()),
        session_id=session_id,
        name=booking_data.name,
        email=booking_data.email,
        date=booking_data.date,
        time=booking_data.time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking