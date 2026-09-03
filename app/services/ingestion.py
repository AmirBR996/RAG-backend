import uuid
import pypdf
from typing import List
from sqlalchemy.orm import Session
from qdrant_client.http.models import PointStruct
from app.schemas.document import ChunkStrategy
from app.clients.llm import get_embeddings
from app.clients.qdrant import qdrant_client
from app.config import settings
from app.database.models import DocumentMeta, ChunkMeta

def extract_text(file_path: str, filename: str) -> str:
    if filename.endswith(".pdf"):
        text = ""
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

def apply_chunking(text: str, strategy: ChunkStrategy, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    if strategy == ChunkStrategy.CHARACTER:
        step = chunk_size - overlap
        for i in range(0, len(text), step):
            chunks.append(text[i:i + chunk_size])
    elif strategy == ChunkStrategy.RECURSIVE:
        delimiters = ["\n\n", "\n", " ", ""]
        def split_text(txt, idx=0):
            if len(txt) <= chunk_size or idx >= len(delimiters):
                return [txt]
            sep = delimiters[idx]
            parts = txt.split(sep)
            result = []
            current = ""
            for part in parts:
                if len(current) + len(part) + len(sep) <= chunk_size:
                    current += (sep if current else "") + part
                else:
                    if current:
                        result.append(current)
                    current = part
            if current:
                result.append(current)
            return result

        chunks = split_text(text)
    return [c.strip() for c in chunks if c.strip()]

def process_and_store_document(db: Session, file_path: str, filename: str, strategy: ChunkStrategy) -> DocumentMeta:
    text = extract_text(file_path, filename)
    chunks = apply_chunking(text, strategy)
    
    doc_id = str(uuid.uuid4())
    embeddings = get_embeddings(chunks)
    
    points = []
    chunk_metas = []
    
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        chunk_id = str(uuid.uuid4())
        points.append(
            PointStruct(
                id=chunk_id,
                vector=emb,
                payload={"document_id": doc_id, "text": chunk, "index": idx}
            )
        )
        chunk_metas.append(
            ChunkMeta(id=chunk_id, document_id=doc_id, chunk_index=idx, content_snippet=chunk[:100])
        )

    qdrant_client.upsert(collection_name=settings.COLLECTION_NAME, points=points)
    
    doc_meta = DocumentMeta(
        id=doc_id,
        filename=filename,
        chunking_strategy=strategy.value,
        chunk_count=len(chunks),
        chunks=chunk_metas
    )
    db.add(doc_meta)
    db.commit()
    db.refresh(doc_meta)
    
    return doc_meta