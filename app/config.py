from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings


# Get the absolute path to the current file
current_file = Path(__file__).resolve()

# Move up three levels to reach project root
# project_dir = current_file.parents[1]

# Paths
env_path = current_file.parent / ".env"


class Settings(BaseSettings):
    # General project settings
    debug: bool
    project_name: str
    base_url: str
    environment: str  # development / staging / production
    allowed_origins: List[str]

    secret_key: str
    restaurant_name: str
    delivery_radius_km: float
    
    # Database
    database_url: str

    # WhatsApp API (Twilio)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"


settings = Settings()
