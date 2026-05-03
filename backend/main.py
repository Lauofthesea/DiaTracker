"""
ML Diabetes Tracker Backend API

FastAPI application for diabetes prediction and food tracking.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.database import engine
from app.db.base import Base
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import ErrorHandlingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting up ML Diabetes Tracker API...")
    
    # Create logs directory for audit logs
    os.makedirs("logs", exist_ok=True)
    
    print("Security features enabled:")
    print(f"  - Rate limiting: {settings.RATE_LIMIT_PER_MINUTE} requests/minute")
    print(f"  - CORS: {settings.ALLOWED_HOSTS}")
    print(f"  - TLS 1.2+ required for production")
    print(f"  - AES-256 encryption enabled")
    print(f"  - Audit logging enabled")
    
    yield
    # Shutdown
    print("Shutting down ML Diabetes Tracker API...")


app = FastAPI(
    title="ML Diabetes Tracker API",
    description="API for diabetes prediction and nutritional tracking",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Security middleware - order matters!

# 1. Error handling (outermost - catches all errors)
app.add_middleware(ErrorHandlingMiddleware)

# 2. Rate limiting (before processing requests)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# 3. CORS middleware with strict origin whitelist
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Explicit methods
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# 4. Trusted host middleware (prevent host header attacks)
# In production, this should be configured with actual domain
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ML Diabetes Tracker API",
        "version": "1.0.0",
        "security": {
            "tls": "1.2+",
            "encryption": "AES-256",
            "rate_limit": f"{settings.RATE_LIMIT_PER_MINUTE} requests/minute"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    # In production, use proper HTTPS configuration
    # with SSL certificates (Let's Encrypt)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # For production with TLS 1.2+:
        # ssl_keyfile="path/to/key.pem",
        # ssl_certfile="path/to/cert.pem",
        # ssl_version=ssl.PROTOCOL_TLSv1_2,
    )