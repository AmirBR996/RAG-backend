from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag import custom_rag_query

router = APIRouter(prefix="/chat", tags=["Conversational RAG"])

@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    res = custom_rag_query(db, session_id=request.session_id, query=request.query)
    return ChatResponse(**res)