# ai-engineering-playground

Hands-on practice for backend, AI engineering, RAG, agents, observability, and CS fundamentals.

## Current features

- FastAPI and Swagger UI
- User CRUD with Router, Service, and Repository layers
- SQLAlchemy and Alembic migrations
- Document storage and LangChain text chunking
- OpenAI embeddings stored with document chunks

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Add your OpenAI API key to `.env` before using the embedding endpoint.

```dotenv
OPENAI_API_KEY=your-api-key
```

Open Swagger UI at <http://127.0.0.1:8000/docs>.

## Main endpoints

- `GET /health`
- `POST /chat`
- `GET`, `POST`, `PATCH`, `DELETE /users`
- `GET`, `POST /documents`
- `POST /documents/{document_id}/chunk-preview`
- `POST /documents/{document_id}/embed`
