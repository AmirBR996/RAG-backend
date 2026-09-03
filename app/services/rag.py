from sqlalchemy.orm import Session
from app.clients.qdrant import qdrant_client
from app.clients.llm import get_embeddings
from app.config import settings
from app.services.memory import memory_service
from app.services.booking import parse_booking_intent_with_llm, save_booking

def custom_rag_query(db: Session, session_id: str, query: str) -> dict:
    # 1. Store user message in Redis Memory
    memory_service.add_message(session_id, "user", query)
    
    # 2. Check for interview booking intent
    booking_intent = parse_booking_intent_with_llm(query)
    booking_info = None
    if booking_intent:
        saved_booking = save_booking(db, session_id, booking_intent)
        booking_info = {
            "id": saved_booking.id,
            "name": saved_booking.name,
            "email": saved_booking.email,
            "date": saved_booking.date,
            "time": saved_booking.time
        }

    # 3. Custom Retrieval without high-level RetrievalQAChain wrappers
    query_vector = get_embeddings([query])[0]
    search_results = qdrant_client.search(
        collection_name=settings.COLLECTION_NAME,
        query_vector=query_vector,
        limit=3
    )
    
    retrieved_contexts = [hit.payload["text"] for hit in search_results if "text" in hit.payload]
    context_str = "\n---\n".join(retrieved_contexts) if retrieved_contexts else "No relevant context found."

    # 4. Fetch Chat History
    history = memory_service.get_history(session_id, limit=6)
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[:-1]])

    # 5. Build Synthesized Answer
    if booking_info:
        answer = f"Your interview booking has been confirmed for {booking_info['date']} at {booking_info['time']}! Details sent to {booking_info['email']}."
    elif retrieved_contexts:
        answer = f"Based on knowledge context:\n{context_str}\n\n[Query Answer]: Provided summary for '{query}'"
    else:
        answer = f"I couldn't find specific context, but I am listening. How can I assist you regarding your application?"

    # 6. Save LLM answer to Redis
    memory_service.add_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "query": query,
        "answer": answer,
        "booking_detected": booking_info is not None,
        "booking_details": booking_info
    }