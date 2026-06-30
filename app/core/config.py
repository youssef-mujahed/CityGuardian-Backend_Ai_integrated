import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Traffic Management System"
    DEBUG: bool = True
    SECRET_KEY: str 
    
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "traffic_management"
    
    # JWT Settings
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    
    #maps
    OPENROUTESERVICE_API_KEY: str = ""
    SMS_SENDER_EMAIL: str = os.getenv("SMS_SENDER_EMAIL", "")
    SMS_SENDER_PASSWORD: str = os.getenv("SMS_SENDER_PASSWORD", "")
    
    
    #firebase credintials
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()