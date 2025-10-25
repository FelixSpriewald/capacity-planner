from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import json
from enum import Enum
import logging

from app.api.routes import router as api_router
from app.core.config import settings
from app.db.init_db import ensure_database_ready

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App erstellen
app = FastAPI(
    title="Capacity Planner API",
    description="REST API für Team-Capacity-Planning mit Sprint-Management",
    version="1.0.0",
    timezone=settings.TIMEZONE
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger.info("Starting Capacity Planner API...")
    try:
        ensure_database_ready()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database during startup: {e}")
        # In production, you might want to exit here
        # For development, we'll continue and let the user handle it manually

# CORS Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifische Origins setzen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router einbinden
app.include_router(api_router, prefix="/api/v1")

# Health Check Route
@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {"status": "ok"}

# Root Route
@app.get("/")
async def root():
    """Root Endpoint"""
    return {
        "message": "Capacity Planner API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
