"""FastAPI application entry point."""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine
from app.db.models import Base
from app.api import chat, appointments, metrics
from app.utils.logger import logger, request_id_var


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create DB tables on startup."""
    logger.info("Starting AI Healthcare Assistant...")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully.")
    yield

    # Cleanup
    await engine.dispose()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="AI Healthcare Assistant",
    description=(
        "An AI-powered healthcare assistant that collects symptoms, "
        "recommends departments, and books appointments."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add a unique request ID for tracing."""
    req_id = str(uuid.uuid4())[:8]
    request_id_var.set(req_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


# Include routers
app.include_router(chat.router)
app.include_router(appointments.router)
app.include_router(metrics.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-healthcare-assistant"}
