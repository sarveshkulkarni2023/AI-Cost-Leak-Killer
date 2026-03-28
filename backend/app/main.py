"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import upload, anomalies, dashboard, actions, logs
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Cost Leak Killer",
    description="Detect, analyze, and correct enterprise cost leakages with AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
        logger.info("App will continue with potential database issues")

# Include routers
app.include_router(upload.router)
app.include_router(anomalies.router)
app.include_router(dashboard.router)
app.include_router(actions.router)
app.include_router(logs.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Cost Leak Killer API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/upload",
            "detect": "POST /api/detect-anomalies",
            "anomalies": "GET /api/anomalies",
            "summary": "GET /api/summary",
            "actions": "GET /api/actions",
            "logs": "GET /api/logs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
