from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from typing import Generator

from .models import Base
from ..utils import get_logger
from config import get_config

logger = get_logger(__name__)

# Global variables for database connection
engine = None
SessionLocal = None


def get_database_url() -> str:
    """
    Build database URL from configuration
    """
    config = get_config()
    db_config = config["database"]
    
    # Check for full database URL first
    if "url" in db_config and db_config["url"]:
        return db_config["url"]
    
    # Build URL from components for PostgreSQL
    if db_config["password"]:
        url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    else:
        url = f"postgresql://{db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    return url


def get_engine():
    """
    Get or create database engine
    """
    global engine
    
    if engine is None:
        database_url = get_database_url()
        
        # Configure engine based on database type
        if database_url.startswith("sqlite"):
            engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=False
            )
        else:
            engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        
        logger.info(f"Database engine created for: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    
    return engine


def get_session_maker():
    """
    Get or create session maker
    """
    global SessionLocal
    
    if SessionLocal is None:
        engine = get_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal


def get_session() -> Session:
    """
    Get a new database session
    """
    session_maker = get_session_maker()
    return session_maker()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def init_db(drop_all: bool = False) -> None:
    """
    Initialize database tables
    
    Args:
        drop_all: If True, drop all existing tables first
    """
    engine = get_engine()
    
    try:
        if drop_all:
            logger.warning("Dropping all database tables")
            Base.metadata.drop_all(bind=engine)
        
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def test_connection() -> bool:
    """
    Test database connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text
        with get_db() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_db_info() -> dict:
    """
    Get database information
    
    Returns:
        Dictionary with database info
    """
    try:
        from sqlalchemy import text
        engine = get_engine()
        with get_db() as db:
            # Different version queries for different databases
            if "sqlite" in str(engine.url):
                result = db.execute(text("SELECT sqlite_version()"))
                version = f"SQLite {result.fetchone()[0]}" if result else "SQLite Unknown"
            else:
                result = db.execute(text("SELECT version()"))
                version = result.fetchone()[0] if result else "Unknown"
            
            # Pool info (only for non-SQLite databases)
            pool_info = {}
            if not "sqlite" in str(engine.url):
                pool_info = {
                    "pool_size": engine.pool.size(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow(),
                    "checked_in": engine.pool.checkedin()
                }
            
            return {
                "url": str(engine.url).replace(str(engine.url.password) if engine.url.password else "", "***"),
                "version": version,
                **pool_info
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}