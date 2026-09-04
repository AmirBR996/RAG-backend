import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.document import DocumentResponse, ChunkStrategy
from app.services.ingestion import process_and_store_document


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "./uploads"


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    strategy: ChunkStrategy = Form(ChunkStrategy.RECURSIVE),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = process_and_store_document(
        db,
        file_path,
        file.filename,
        strategy
    )

    return DocumentResponse(
        document_id=document.id,
        filename=document.filename,
        chunking_strategy=ChunkStrategy(document.chunking_strategy),
        total_chunks=document.chunk_count
    )