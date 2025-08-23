from pathlib import Path
from typing import List
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


    # Database
    database_url: str

    # WhatsApp API (Twilio)
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str

    # Restaurant / Business settings
    restaurant_name: str
    delivery_radius_km: float

    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"


settings = Settings()
