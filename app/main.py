from fastapi import FastAPI

from app.routers import chat, documents, health, users

app = FastAPI()

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(documents.router)
