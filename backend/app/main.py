import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import research, pdf, discord
from app.utils.logger import logger
from app.utils.config import settings
import uvicorn

app = FastAPI(
    title="AI Company Research API",
    description="Backend for researching companies using AI, Serper, and web crawling.",
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(research.router)
app.include_router(pdf.router)
app.include_router(discord.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AI Company Research API...")
    if not settings.OPENROUTER_API_KEY or not settings.SERPER_API_KEY:
        logger.warning("Missing essential API keys (OpenRouter/Serper) in environment variables!")

@app.get("/")
async def root():
    return {"message": "AI Company Research API is running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
