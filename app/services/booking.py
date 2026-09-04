import json
import uuid
from datetime import date
from typing import Optional

from groq import Groq
from sqlalchemy.orm import Session

from app.config import settings
from app.database.models import InterviewBooking
from app.schemas.booking import BookingSchema, BookingExtraction


groq_client = Groq(api_key=settings.GROQ_API_KEY)


def extract_booking_info(user_input: str) -> BookingExtraction:
    today = date.today().isoformat()

    prompt = f"""
You extract interview booking information.

Today: {today}

Return ONLY JSON:
{{
    "booking_intent": false,
    "name": null,
    "email": null,
    "date": null,
    "time": null
}}

Rules:
- booking_intent=true if the user wants to book or schedule an interview.
- Never invent information.
- Missing values must be null.
- Keep name and email exactly as provided.
- Convert dates to YYYY-MM-DD.
- Convert times to 24-hour HH:MM.
- Understand dates like tomorrow, next Monday, this Friday.
"""

    try:
        response = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content or "{}")

        return BookingExtraction(
            booking_intent=data.get("booking_intent", False),
            name=data.get("name"),
            email=data.get("email"),
            date=data.get("date"),
            time=data.get("time")
        )

    except Exception as e:
        print(f"Booking extraction error: {e}")
        return BookingExtraction()


def parse_booking_intent_with_llm(
    user_input: str
) -> Optional[BookingSchema]:

    result = extract_booking_info(user_input)

    if not result.booking_intent:
        return None

    return BookingSchema(
        name=result.name,
        email=result.email,
        date=result.date,
        time=result.time
    )


def merge_booking_data(
    old_data: Optional[BookingSchema],
    new_data: BookingExtraction
) -> BookingSchema:

    return BookingSchema(
        name=new_data.name or (old_data.name if old_data else None),
        email=new_data.email or (old_data.email if old_data else None),
        date=new_data.date or (old_data.date if old_data else None),
        time=new_data.time or (old_data.time if old_data else None)
    )


def get_missing_booking_fields(
    booking_data: BookingSchema
) -> list[str]:

    fields = ["name", "email", "date", "time"]

    return [
        field for field in fields
        if not getattr(booking_data, field)
    ]


def save_booking(
    db: Session,
    session_id: str,
    booking_data: BookingSchema
) -> InterviewBooking:

    missing = get_missing_booking_fields(booking_data)

    if missing:
        raise ValueError(
            f"Cannot save incomplete booking. Missing: {', '.join(missing)}"
        )

    booking = InterviewBooking(
        id=str(uuid.uuid4()),
        session_id=session_id,
        name=booking_data.name,
        email=booking_data.email,
        date=booking_data.date,
        time=booking_data.time
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    except Exception:
        db.rollback()
        raise