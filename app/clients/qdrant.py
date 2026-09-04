from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.config import settings


qdrant_client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT
)


def init_qdrant():
    collections = qdrant_client.get_collections().collections

    if settings.COLLECTION_NAME not in [c.name for c in collections]:
        qdrant_client.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )