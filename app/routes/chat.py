from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.chat import ChatRequest
from app.services.rag import custom_rag_query


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    result = custom_rag_query(
        query=request.query,
        session_id=request.session_id,
        db=db
    )

    return {
        "session_id": request.session_id,
        "query": request.query,
        "answer": result["answer"],
        "booking_detected": result["booking_detected"],
        "booking_completed": result["booking_completed"],
        "booking_details": result["booking_details"]
    }