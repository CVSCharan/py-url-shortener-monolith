from sqlalchemy import Column, Integer, String
from database import Base

# This defines the shape of our table in PostgreSQL (Like a Mongoose Schema)
class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, index=True)     # The long URL (e.g. https://google.com)
    short_code = Column(String, unique=True, index=True) # The short code (e.g. xyz123)
    clicks = Column(Integer, default=0)         # Analytics tracking
