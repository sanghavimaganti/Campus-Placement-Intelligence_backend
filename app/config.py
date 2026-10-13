import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "Campus Placement Eligibility Dashboard"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    # Defaults to local SQLite, or uses DATABASE_URL (MySQL/PostgreSQL) if provided
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campus_placement.db")
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://localhost:5173",
        "*"
    ]

settings = Settings()
