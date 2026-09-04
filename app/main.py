from fastapi import FastAPI
from app.database.connection import engine, Base
from app.clients.qdrant import init_qdrant
from app.routes import documents, chat

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG Backend API",
    version="1.0.0",
    description="Backend for production grade rag"
)

@app.on_event("startup")
def startup_event():
    init_qdrant()

app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Hello this is RAG application backend!"}