import os
import logging
from dotenv import load_dotenv
# from pydantic import BaseSettings # Old import
from pydantic_settings import BaseSettings # New import

# Load .env file BEFORE Settings class definition
load_dotenv(dotenv_path=".env")

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "true").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "false").lower() == "true"

settings = Settings()

# Runtime validation and debug logging
if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment or .env")

logging.warning(f"🚨 DEBUG: DATABASE_URL at runtime = {settings.DATABASE_URL}")
logging.warning(f"🚨 DEBUG: EMAIL_USERNAME = {settings.EMAIL_USERNAME}")
