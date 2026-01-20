from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.apis.v1 import auth, chat, health, ingest
from app.core.config import settings
from app.core.custom_exceptions import http_exception_handler
from app.core.logging import setup_logging

# Base.metadata.create_all(bind=async_engine)
# TODO read from config
app = FastAPI(
    title=settings.APP_NAME or "RAG ChatBot",
    description=settings.APP_DESCRIPTION,
)
setup_logging(log_level="INFO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(auth.router)
app.add_exception_handler(HTTPException, http_exception_handler)
