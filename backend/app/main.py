from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import analyze

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered misinformation detection system using Gemini"
)

# Configure CORS - Allow all origins in debug mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to TruthBot API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health():
    """Health check endpoint at root level"""
    return {"status": "healthy", "version": settings.APP_VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )