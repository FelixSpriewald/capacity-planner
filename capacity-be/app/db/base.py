from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLAlchemy Engine erstellen
engine = create_engine(
    settings.MYSQL_URL,
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
    pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
    pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
    echo=settings.DEBUG,  # SQL Queries loggen wenn DEBUG=True
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base für Models
Base = declarative_base()


# Dependency für FastAPI
def get_db():
    """Database Session Dependency für FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
