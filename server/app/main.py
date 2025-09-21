from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .api.v1 import api_router
from .tasks.scheduler import setup_scheduler, start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Job Tracker API")
    setup_scheduler()
    start_scheduler()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Job Tracker API")
    stop_scheduler()


app = FastAPI(
    title="Job Tracker API",
    description="A comprehensive job application tracking system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Job Tracker API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Job Tracker API is running"}
