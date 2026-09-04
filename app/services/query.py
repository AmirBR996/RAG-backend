from groq import Groq

from app.config import settings
from app.clients.llm import get_embeddings
from app.clients.qdrant import qdrant_client
from app.services.memory import memory_service


groq_client = Groq(api_key=settings.GROQ_API_KEY)


def rag_query(
    query: str,
    session_id: str
):
    query_vector = get_embeddings([query])[0]

    results = qdrant_client.query_points(
        collection_name=settings.COLLECTION_NAME,
        query=query_vector,
        limit=5,
        with_payload=True
    ).points

    context = "\n\n".join(
        result.payload["text"]
        for result in results
        if result.payload and "text" in result.payload
    )

    history = memory_service.get_history(session_id)

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )

    prompt = f"""
You are a helpful assistant.

Use the document context to answer the user's question.

Document context:
{context}

Conversation history:
{history_text}

Rules:
- Answer using the document context.
- Use conversation history when useful.
- If the answer is not in the documents, say you don't know.
- Do not invent information.
"""

    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0
    )

    answer = response.choices[0].message.content

    memory_service.add_message(
        session_id,
        "user",
        query
    )

    memory_service.add_message(
        session_id,
        "assistant",
        answer
    )

    return answer