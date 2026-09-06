from pydantic import BaseModel, HttpUrl

# Pydantic Schemas handle input validation and output serialization (Like Zod)

# When a user submits a form, they send a target_url.
class URLCreate(BaseModel):
    target_url: HttpUrl # Automatically validates that it is a valid URL!

# When we return data to the user, this is what it looks like.
class URLInfo(URLCreate):
    id: int
    short_code: str
    clicks: int

    # Config allows Pydantic to read data directly from a SQLAlchemy model
    class Config:
        from_attributes = True
