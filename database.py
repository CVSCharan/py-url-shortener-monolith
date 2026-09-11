import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the connection string. If it's missing, fall back to SQLite for local development.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    # On Vercel, the file system is read-only except for /tmp
    db_path = "/tmp/shortener.db" if os.getenv("VERCEL") else "./shortener.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# SQLAlchemy 1.4+ strictly requires postgresql:// instead of postgres://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

# The connect_args={"check_same_thread": False} is only needed for SQLite in FastAPI
connect_args = (
    {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

# The engine is responsible for communicating with the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# A SessionLocal class will be a factory for new database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models to inherit from.
Base = declarative_base()


# Dependency to get a database session for each request (similar to context in GraphQL)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
