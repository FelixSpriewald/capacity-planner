from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings mit Pydantic Settings"""

    # Database Configuration
    MYSQL_URL: str = "mysql+pymysql://capacity_user:capacity_password@localhost:3306/capacity_planner"

    # Application Settings
    TIMEZONE: str = "Europe/Berlin"
    DEBUG: bool = False

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Capacity Planner"

    # Database Pool Settings
    SQLALCHEMY_POOL_SIZE: int = 5
    SQLALCHEMY_MAX_OVERFLOW: int = 10
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global Settings Instance
settings = Settings()
