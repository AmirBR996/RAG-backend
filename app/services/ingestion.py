import uuid
import pypdf

from sqlalchemy.orm import Session
from qdrant_client.http.models import PointStruct

from app.schemas.document import ChunkStrategy
from app.clients.llm import get_embeddings
from app.clients.qdrant import qdrant_client
from app.config import settings
from app.database.models import DocumentMeta, ChunkMeta


def extract_text(file_path: str, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(file_path)
        return "".join(page.extract_text() or "" for page in reader.pages)

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def apply_chunking(
    text: str,
    strategy: ChunkStrategy,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:

    if strategy == ChunkStrategy.CHARACTER:
        step = chunk_size - overlap

        chunks = [
            text[i:i + chunk_size]
            for i in range(0, len(text), step)
        ]

    else:
        chunks = []
        current = ""

        for paragraph in text.split("\n\n"):
            if len(current) + len(paragraph) <= chunk_size:
                current += ("\n\n" if current else "") + paragraph
            else:
                if current:
                    chunks.append(current)
                current = paragraph

        if current:
            chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def process_and_store_document(
    db: Session,
    file_path: str,
    filename: str,
    strategy: ChunkStrategy
) -> DocumentMeta:

    text = extract_text(file_path, filename)
    chunks = apply_chunking(text, strategy)

    doc_id = str(uuid.uuid4())
    embeddings = get_embeddings(chunks)

    points = []
    chunk_metas = []

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = str(uuid.uuid4())

        points.append(
            PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "document_id": doc_id,
                    "text": chunk,
                    "index": index
                }
            )
        )

        chunk_metas.append(
            ChunkMeta(
                id=chunk_id,
                document_id=doc_id,
                chunk_index=index,
                content_snippet=chunk[:100]
            )
        )

    qdrant_client.upsert(
        collection_name=settings.COLLECTION_NAME,
        points=points
    )

    document = DocumentMeta(
        id=doc_id,
        filename=filename,
        chunking_strategy=strategy.value,
        chunk_count=len(chunks),
        chunks=chunk_metas
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document