"""
TruthLens — Fake News Detector
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import os

from app.database.connection import connect_db, disconnect_db
from app.routes import predict, auth, analytics, sources, graphs, metrics, history
from app.middleware.rate_limiter import RateLimitMiddleware
from app.utils.model_loader import ModelLoader


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("Starting TruthLens backend…")
    await connect_db()
    # Pre-load all ML models into memory
    loader = ModelLoader()
    await loader.load_all()
    app.state.model_loader = loader
    logger.info("All models loaded. Server ready.")
    yield
    logger.info("Shutting down…")
    await disconnect_db()


app = FastAPI(
    title="TruthLens — Fake News Detector API",
    description=(
        "Production-grade misinformation detection platform. "
        "Combines semantic analysis, linguistic features, emotion detection, "
        "source credibility, AI-generated text detection, and explainable AI."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/auth",      tags=["Authentication"])
app.include_router(predict.router,   prefix="/api/predict",   tags=["Prediction"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(sources.router,   prefix="/api/sources",   tags=["Source Credibility"])
app.include_router(graphs.router,    prefix="/api/graphs",    tags=["Graph Analysis"])
app.include_router(metrics.router,   prefix="/api/metrics",   tags=["Model Metrics"])
app.include_router(history.router,   prefix="/api/history",   tags=["History"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "TruthLens Backend", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to TruthLens API",
        "docs": "/docs",
        "health": "/health",
    }
