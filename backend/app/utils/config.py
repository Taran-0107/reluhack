import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY")
    DISCORD_WEBHOOK_URL: str | None = None
    OPENROUTER_MODEL: str = "openrouter/free"
    
    # Provider toggle: "cohere" or "openrouter"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "cohere")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
