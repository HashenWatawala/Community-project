import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGO_DETAILS: str = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "tms_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

settings = Settings()
