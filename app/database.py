"""
Database connection and session management
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)
print(settings.DATABASE_URL,'database url')

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def check_connection():
    """Check database connection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except OperationalError as e:
        logger.error(f"Database connection failed: {e.orig}")
        return False
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
