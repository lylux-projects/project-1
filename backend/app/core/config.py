from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Database settings
    supabase_url: str = "https://ijhthgduecrvuwnukzcg.supabase.co"
    supabase_key: str = "your-supabase-key-here"
    
    # API settings
    api_title: str = "Lylux Product Configurator API"
    api_version: str = "1.0.0"
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    model_config = {
        "env_file": ".env",
        "extra": "allow"  # This allows extra fields from .env
    }

settings = Settings()