import pytest
from app.schemas.document import ChunkStrategy
from app.services.ingestion import apply_chunking

def test_character_chunking():
    text = "Hello world! This is a test for character chunking algorithm."
    chunks = apply_chunking(text, ChunkStrategy.CHARACTER, chunk_size=20, overlap=5)
    assert len(chunks) > 1

def test_recursive_chunking():
    text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    chunks = apply_chunking(text, ChunkStrategy.RECURSIVE, chunk_size=15, overlap=2)
    assert len(chunks) >= 3