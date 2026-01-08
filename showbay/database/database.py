from sqlmodel import create_engine, Session
from sqlalchemy import event
from sqlalchemy.pool import Pool
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/showbay_db")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection.
    
    Yields:
        Session: A database session that will be automatically closed.
    """
    with Session(engine) as session:
        yield session


# Optional: Add event listener to log connection events (useful for debugging)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database-specific pragmas when connecting."""
    pass  # PostgreSQL doesn't need special pragmas like SQLite