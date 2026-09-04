from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

class ChunkStrategy(str, Enum):
    CHARACTER = "character"
    RECURSIVE = "recursive"

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    chunking_strategy: ChunkStrategy
    total_chunks: int
    class Config:
        from_attributes = True