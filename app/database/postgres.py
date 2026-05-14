from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.database.base import Base

_engine = None
_SessionLocal = None

def init_postgres():
    """Initialize PostgreSQL connection - call this on startup"""
    global _engine, _SessionLocal
    
    DATABASE_URL = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    
    _engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

def close_postgres():
    """Close PostgreSQL connection - call this on shutdown"""
    global _engine
    if _engine:
        _engine.dispose()

def get_db() -> Generator[Session, None, None]:
    """Get database session - use as FastAPI dependency"""
    if _SessionLocal is None:
        init_postgres()
    
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    if _engine is None:
        init_postgres()
    Base.metadata.create_all(bind=_engine)