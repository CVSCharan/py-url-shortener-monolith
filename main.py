from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import string
import random

# Import our custom modules
import models
from database import engine, get_db

# Create all database tables (Normally done with Alembic, but this works for basic apps)
models.Base.metadata.create_all(bind=engine)

import os
app = FastAPI(title="Python URL Shortener")

# Setup Jinja2 templates for Server-Side Rendering
# Vercel needs an absolute path to the templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """Render the main page with a list of all URLs."""
    urls = db.query(models.URL).order_by(models.URL.id.desc()).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"urls": urls})


@app.post("/shorten", response_class=HTMLResponse)
def shorten_url(request: Request, target_url: str = Form(...), db: Session = Depends(get_db)):
    """Handle the form submission, create a short URL, and return the updated HTML list."""
    # Ensure the URL has http/https
    if not target_url.startswith("http"):
        target_url = "https://" + target_url

    short_code = generate_short_code()
    
    # Check for collisions (very rare, but good practice)
    while db.query(models.URL).filter(models.URL.short_code == short_code).first():
        short_code = generate_short_code()

    # Create the DB record (like `new URL({ targetUrl, shortCode })` in Mongoose)
    db_url = models.URL(target_url=target_url, short_code=short_code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Re-fetch all URLs to render the updated list
    urls = db.query(models.URL).order_by(models.URL.id.desc()).all()
    
    # We return ONLY the partial HTML that HTMX requested to replace
    return templates.TemplateResponse(request=request, name="partials/url_list.html", context={"urls": urls})


@app.get("/{short_code}")
def redirect_to_target(short_code: str, db: Session = Depends(get_db)):
    """When a user visits the short URL, redirect them to the original destination."""
    db_url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Increment clicks for analytics
    db_url.clicks += 1
    db.commit()

    # Redirect (HTTP 307)
    return RedirectResponse(url=db_url.target_url)
