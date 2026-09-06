import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the connection string. If it's missing, throw an error.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Please add it to your .env file.")

# SQLAlchemy 1.4+ strictly requires postgresql:// instead of postgres://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# The engine is responsible for communicating with the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

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
