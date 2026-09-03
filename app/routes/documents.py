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
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc_meta = process_and_store_document(db, file_path, file.filename, strategy)
    
    return DocumentResponse(
        document_id=doc_meta.id,
        filename=doc_meta.filename,
        chunking_strategy=ChunkStrategy(doc_meta.chunking_strategy),
        total_chunks=doc_meta.chunk_count
    )