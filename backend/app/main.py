"""
Resume Coach - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.routes import resume, analysis, chat
from app.models.schemas import HealthResponse
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered resume coaching and job matching application",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix=settings.API_V1_PREFIX, tags=["resume"])
app.include_router(analysis.router, prefix=settings.API_V1_PREFIX, tags=["analysis"])
app.include_router(chat.router, prefix=settings.API_V1_PREFIX, tags=["chat"])


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
