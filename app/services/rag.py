from sqlalchemy.orm import Session

from app.services.booking import (
    extract_booking_info,
    merge_booking_data,
    get_missing_booking_fields,
    save_booking
)
from app.services.query import rag_query
from app.schemas.booking import BookingSchema


pending_bookings: dict[str, BookingSchema] = {}


def format_missing_fields(fields: list[str]) -> str:
    labels = {
        "name": "your full name",
        "email": "your email address",
        "date": "your preferred interview date",
        "time": "your preferred interview time"
    }

    fields = [labels[field] for field in fields]

    if len(fields) == 1:
        return fields[0]

    if len(fields) == 2:
        return f"{fields[0]} and {fields[1]}"

    return ", ".join(fields[:-1]) + ", and " + fields[-1]


def custom_rag_query(
    query: str,
    session_id: str,
    db: Session
):
    extracted = extract_booking_info(query)

    if extracted.booking_intent or session_id in pending_bookings:
        previous = pending_bookings.get(session_id)

        booking = merge_booking_data(
            previous,
            extracted
        )

        missing = get_missing_booking_fields(booking)

        if missing:
            pending_bookings[session_id] = booking

            return {
                "answer": (
                    "I'd be happy to help schedule your interview. "
                    f"Please provide {format_missing_fields(missing)}."
                ),
                "booking_detected": True,
                "booking_completed": False,
                "booking_details": {
                    "name": booking.name,
                    "email": booking.email,
                    "date": booking.date,
                    "time": booking.time
                }
            }

        try:
            saved = save_booking(
                db,
                session_id,
                booking
            )

        except Exception as e:
            print(f"Booking save error: {e}")

            return {
                "answer": "I couldn't save your interview booking. Please try again.",
                "booking_detected": True,
                "booking_completed": False,
                "booking_details": None
            }

        pending_bookings.pop(session_id, None)

        return {
            "answer": (
                f"Your interview booking has been confirmed for "
                f"{saved.date} at {saved.time}. "
                f"Details sent to {saved.email}."
            ),
            "booking_detected": True,
            "booking_completed": True,
            "booking_details": {
                "id": saved.id,
                "name": saved.name,
                "email": saved.email,
                "date": saved.date,
                "time": saved.time
            }
        }

    answer = rag_query(
        query=query,
        session_id=session_id
    )

    return {
        "answer": answer,
        "booking_detected": False,
        "booking_completed": False,
        "booking_details": None
    }