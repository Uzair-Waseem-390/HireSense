#  this file contains configuration settings for the ORM system
#  it handles environment variables, database connection details, and other settings
#  required for the ORM to function correctly within the application.

from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    gemini_api_key: str
    base_url: str

    class Config:
        env_file = BASE_DIR / ".env"

settings = Settings()
