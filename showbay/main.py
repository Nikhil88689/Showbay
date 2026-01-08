from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from showbay.api import router as api_router
from showbay.database.database import engine
from showbay.models.task import Task
from showbay.utils.exception_handlers import (
    external_api_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from showbay.utils.exceptions import ExternalAPIException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Initializing application...")
    
    # Create database tables
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(bind=engine)
    
    logger.info("Application initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="ShowBay Task Management API",
    description="A robust REST API service that acts as a bridge between a local database and an external API",
    version="1.0.0",
    lifespan=lifespan
)

# Register exception handlers
app.add_exception_handler(ExternalAPIException, external_api_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["tasks"])


@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "ShowBay Task Management API is running!"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "ShowBay Task Management API"}