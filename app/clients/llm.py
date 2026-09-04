from groq import Groq
from sentence_transformers import SentenceTransformer
from app.config import settings

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = embedding_model.encode(texts)
    return embeddings.tolist()

groq_client = Groq(api_key=settings.GROQ_API_KEY)


def generate_llm_response(prompt: str) -> str:
    """Generate an answer using Groq."""

    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=100
    )
    return response.choices[0].message.content