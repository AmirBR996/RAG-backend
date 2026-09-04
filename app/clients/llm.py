from sentence_transformers import SentenceTransformer
from app.config import settings

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = embedding_model.encode(texts)
    return embeddings.tolist()



