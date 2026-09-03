from app.services.booking import parse_booking_intent_with_llm

def test_parse_booking_intent():
    query = "I would like to book an interview on 2026-09-10 at 10:00 AM. My email is amir@example.com."
    booking = parse_booking_intent_with_llm(query)
    assert booking is not None
    assert booking.email == "amir@example.com"
    assert booking.date == "2026-09-10"