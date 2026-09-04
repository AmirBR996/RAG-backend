import uuid
import json
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from groq import Groq

from app.config import settings
from app.database.models import InterviewBooking
from app.schemas.booking import (
    BookingSchema,
    BookingExtraction
)

groq_client = Groq(
    api_key=settings.GROQ_API_KEY
)



def extract_booking_info(
    user_input: str
) -> BookingExtraction:

    today = date.today().isoformat()

    system_prompt = f"""
You are an interview booking information extraction assistant.

Today's date is {today}.

Determine whether the user wants to book or schedule
an interview.

Extract these fields:

- name
- email
- date
- time

Return ONLY valid JSON in this exact format:

{{
    "booking_intent": true,
    "name": null,
    "email": null,
    "date": null,
    "time": null
}}

If the message is not related to interview booking:

{{
    "booking_intent": false,
    "name": null,
    "email": null,
    "date": null,
    "time": null
}}

RULES:

1. Never invent information.

2. Missing fields must be null.

3. Preserve the user's name exactly.

Example:

"My name is Amir Bhattarai"

becomes:

"name": "Amir Bhattarai"

4. Extract email exactly.

5. Convert dates to YYYY-MM-DD.

Examples:

"September 15"
-> "{date.today().year}-09-15"

"September 15th"
-> "{date.today().year}-09-15"

"Sept 15"
-> "{date.today().year}-09-15"

"15 September"
-> "{date.today().year}-09-15"

6. Understand relative dates:

"tomorrow"
"next Monday"
"this Friday"

7. Convert times to HH:MM 24-hour format.

Examples:

"2 PM"
-> "14:00"

"2:30 PM"
-> "14:30"

"10 AM"
-> "10:00"

8. booking_intent must be true when the user wants to:

- book an interview
- schedule an interview
- arrange an interview
- set up an interview
- choose an interview time

9. A message can have booking_intent=true
even when some booking fields are missing.

10. Return ONLY JSON.
"""

    try:

        response = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0,
            max_tokens=300,
            response_format={
                "type": "json_object"
            }
        )

        content = response.choices[0].message.content

        if not content:
            return BookingExtraction()

        data = json.loads(content)

        return BookingExtraction(
            booking_intent=bool(
                data.get("booking_intent", False)
            ),
            name=data.get("name"),
            email=data.get("email"),
            date=data.get("date"),
            time=data.get("time")
        )

    except Exception as e:

        print(
            f"Booking extraction error: {e}"
        )

        return BookingExtraction()


 
# OLD FUNCTION NAME
 

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


 
# MERGE BOOKING INFORMATION
 

def merge_booking_data(
    old_data: Optional[BookingSchema],
    new_data: BookingExtraction
) -> BookingSchema:

    """
    Merge previously collected booking information
    with information from the latest user message.
    """

    return BookingSchema(

        name=(
            new_data.name
            if new_data.name
            else old_data.name
            if old_data
            else None
        ),

        email=(
            new_data.email
            if new_data.email
            else old_data.email
            if old_data
            else None
        ),

        date=(
            new_data.date
            if new_data.date
            else old_data.date
            if old_data
            else None
        ),

        time=(
            new_data.time
            if new_data.time
            else old_data.time
            if old_data
            else None
        )
    )


 
# MISSING FIELDS
 

def get_missing_booking_fields(
    booking_data: BookingSchema
) -> list[str]:

    missing = []

    if not booking_data.name:
        missing.append("name")

    if not booking_data.email:
        missing.append("email")

    if not booking_data.date:
        missing.append("date")

    if not booking_data.time:
        missing.append("time")

    return missing


 
# SAVE BOOKING
 

def save_booking(
    db: Session,
    session_id: str,
    booking_data: BookingSchema
) -> InterviewBooking:

    missing_fields = get_missing_booking_fields(
        booking_data
    )

    if missing_fields:

        raise ValueError(
            "Cannot save incomplete booking. "
            f"Missing: {', '.join(missing_fields)}"
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