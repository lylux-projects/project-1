from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Database settings
    database_url: str = ""
    supabase_url: str = "https://ijhthgduecrvuwnukzcg.supabase.co"
    supabase_anon_key: str = ""  # This matches SUPABASE_ANON_KEY in .env
    supabase_service_role_key: str = ""  # This matches SUPABASE_SERVICE_ROLE_KEY in .env
    
    # FastAPI Configuration
    secret_key: str = "lyluxproject007"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    
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