from fastapi import FastAPI

from app.routers import chat, cs_agent, documents, health, rag, users

app = FastAPI()

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(cs_agent.router)
