# RAG Backend

A simple Retrieval-Augmented Generation (RAG) backend built with FastAPI. This repository provides services to ingest documents, store embeddings in Qdrant, and query an LLM for conversational responses.

## Features
- FastAPI-based REST API
- Qdrant vector store integration
- Simple ingestion and chat routes

## Requirements
- Python 3.10+
- See `requirement.txt` for dependencies

## Setup
1. Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirement.txt
```

3. Configure any environment variables in `app/config.py` if needed.

## Run
Start the FastAPI server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open http://127.0.0.1:8000/docs for the interactive API docs.

## Project Structure

- `app/` — main application package
	- `clients/` — LLM and Qdrant clients
	- `database/` — DB connection and models
	- `routes/` — API route handlers (`documents`, `chat`)
	- `services/` — ingestion, query and RAG logic
	- `schemas/` — Pydantic schemas

- `uploads/` — uploaded documents
- `requirement.txt` — Python dependencies

## Contributing
Contributions are welcome. Open issues or pull requests for suggestions and bug fixes.

## License
This project does not include a license file. Add one if you plan to open source it.

