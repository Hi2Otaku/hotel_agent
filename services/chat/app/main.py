"""HotelBook Chat Service -- AI-powered chatbot for guest and staff interactions."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.chat import router as chat_router
from app.api.v1.conversations import router as conversations_router
from app.core.database import engine


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: initialize DB engine on startup, dispose on shutdown."""
    yield
    await engine.dispose()


app = FastAPI(
    title="HotelBook Chat Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(conversations_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "chat"}
