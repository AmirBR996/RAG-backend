from typing import Optional

from sqlalchemy.orm import Session

from app.services.booking import (
    extract_booking_info,
    merge_booking_data,
    get_missing_booking_fields,
    save_booking
)

from app.schemas.booking import BookingSchema

pending_bookings: dict[str, BookingSchema] = {}


def format_missing_fields(
    missing_fields: list[str]
) -> str:

    labels = {
        "name": "your full name",
        "email": "your email address",
        "date": "your preferred interview date",
        "time": "your preferred interview time"
    }

    readable = [
        labels[field]
        for field in missing_fields
    ]

    if len(readable) == 1:

        return readable[0]

    if len(readable) == 2:

        return (
            f"{readable[0]} and {readable[1]}"
        )

    return (
        ", ".join(readable[:-1])
        + ", and "
        + readable[-1]
    )

def custom_rag_query(
    query: str,
    session_id: str,
    db: Session
):


    extracted = extract_booking_info(query)


    if (
        extracted.booking_intent
        or session_id in pending_bookings
    ):

        # Get previous incomplete booking
        previous_booking = pending_bookings.get(
            session_id
        )

        # Merge old + new information
        booking_data = merge_booking_data(
            previous_booking,
            extracted
        )


        missing_fields = get_missing_booking_fields(
            booking_data
        )


        if missing_fields:

            # Save incomplete information in memory
            pending_bookings[session_id] = booking_data

            missing_text = format_missing_fields(
                missing_fields
            )

            return {
                "answer": (
                    "I'd be happy to help schedule "
                    "your interview. Please provide "
                    f"{missing_text}."
                ),

                "booking_detected": True,

                "booking_completed": False,

                "booking_details": {
                    "name": booking_data.name,
                    "email": booking_data.email,
                    "date": booking_data.date,
                    "time": booking_data.time
                }
            }


        try:

            saved_booking = save_booking(
                db=db,
                session_id=session_id,
                booking_data=booking_data
            )

        except Exception as e:

            print(
                f"Booking save error: {e}"
            )

            return {
                "answer": (
                    "I couldn't save your interview "
                    "booking because of a server error. "
                    "Please try again."
                ),

                "booking_detected": True,

                "booking_completed": False,

                "booking_details": None
            }

        pending_bookings.pop(
            session_id,
            None
        )

        return {
            "answer": (
                "Your interview booking has been "
                f"confirmed for {saved_booking.date} "
                f"at {saved_booking.time}. "
                f"Details sent to {saved_booking.email}."
            ),

            "booking_detected": True,

            "booking_completed": True,

            "booking_details": {
                "id": saved_booking.id,
                "name": saved_booking.name,
                "email": saved_booking.email,
                "date": saved_booking.date,
                "time": saved_booking.time
            }
        }

    return {
        "answer": (
            "Normal RAG processing goes here."
        ),

        "booking_detected": False,

        "booking_completed": False,

        "booking_details": None
    }