from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timedelta
from passlib.context import CryptContext
import string
import random
import qrcode
import io
import os
from typing import Optional
import models
from database import engine, get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Import our custom modules


# Create all database tables (Normally done with Alembic, but this works for basic apps)
models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Python URL Shortener")

# Rate Limiting Setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Setup Jinja2 templates for Server-Side Rendering
# Vercel needs an absolute path to the templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


# --- ROUTES ---


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """Render the homepage with the list of recently shortened URLs."""
    urls = db.query(models.URL).order_by(models.URL.id.desc()).limit(5).all()
    default_expiration = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"urls": urls, "default_expiration": default_expiration},
    )


@app.get("/dashboard", response_class=HTMLResponse)
def view_dashboard(request: Request, page: int = 1, db: Session = Depends(get_db)):
    """Render the dashboard with pagination."""
    per_page = 10
    total_urls = db.query(models.URL).count()
    total_pages = (total_urls + per_page - 1) // per_page

    urls = (
        db.query(models.URL)
        .order_by(models.URL.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "urls": urls,
            "current_page": page,
            "total_pages": total_pages,
            "total_urls": total_urls,
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    """Render the about page."""
    return templates.TemplateResponse(request=request, name="about.html")


@app.post("/shorten", response_class=HTMLResponse)
@limiter.limit("5/minute")
def shorten_url(
    request: Request,
    target_url: str = Form(...),
    custom_alias: Optional[str] = Form(None),
    expires_at: Optional[datetime] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Handle the form submission, create a short URL, and return the updated HTML list."""
    # Ensure the URL has http/https
    if not target_url.startswith("http"):
        target_url = "https://" + target_url

    # Check if custom alias is already taken
    if custom_alias:
        if (
            db.query(models.URL).filter(models.URL.custom_alias == custom_alias).first()
            or db.query(models.URL)
            .filter(models.URL.short_code == custom_alias)
            .first()
        ):
            return HTMLResponse(
                "<div class='text-red-500 text-sm mt-2 font-bold'>Error: Alias already taken.</div>",
                status_code=400,
            )

    short_code = generate_short_code()

    # Check for collisions (very rare, but good practice)
    while db.query(models.URL).filter(models.URL.short_code == short_code).first():
        short_code = generate_short_code()

    hashed_password = pwd_context.hash(password) if password else None

    # Create the DB record (like `new URL({ targetUrl, shortCode })` in Mongoose)
    db_url = models.URL(
        target_url=target_url,
        short_code=short_code,
        custom_alias=custom_alias,
        expires_at=expires_at,
        hashed_password=hashed_password,
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Re-fetch all URLs to render the updated list (We will update this to limit 5 later)
    urls = db.query(models.URL).order_by(models.URL.id.desc()).limit(5).all()

    # We return the modal partial. It contains the modal HTML and an OOB swap for the table.
    return templates.TemplateResponse(
        request=request,
        name="partials/shorten_response.html",
        context={"urls": urls, "new_url": db_url},
    )


@app.get("/qr_modal/{short_code}", response_class=HTMLResponse)
def qr_modal(short_code: str, request: Request, db: Session = Depends(get_db)):
    """Return a modal containing the QR code."""
    db_url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    return templates.TemplateResponse(
        request=request, name="partials/qr_modal.html", context={"url": db_url}
    )


@app.get("/qr/{short_code}")
def generate_qr_code(short_code: str, request: Request, db: Session = Depends(get_db)):
    """Generate and return a QR code for a shortened URL."""
    db_url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    full_url = str(request.base_url) + db_url.short_code

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(full_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")  # type: ignore
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@app.get("/{short_code}")
def redirect_to_target(
    short_code: str, request: Request, db: Session = Depends(get_db)
):
    """When a user visits the short URL, redirect them to the original destination."""
    db_url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

    # Custom aliases can also be queried this way, but they are in a different column.
    # Let's check both short_code and custom_alias
    if not db_url:
        db_url = (
            db.query(models.URL).filter(models.URL.custom_alias == short_code).first()
        )

    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Check Premium features
    if not db_url.is_active:
        return HTMLResponse(
            "<h1 style='text-align:center;font-family:sans-serif;margin-top:50px;'>This link has been disabled.</h1>",
            status_code=410,
        )

    if db_url.expires_at and db_url.expires_at < datetime.now():
        return HTMLResponse(
            "<h1 style='text-align:center;font-family:sans-serif;margin-top:50px;'>This link has expired.</h1>",
            status_code=410,
        )

    if db_url.hashed_password:
        return templates.TemplateResponse(
            request=request,
            name="password_prompt.html",
            context={"short_code": short_code},
        )

    # Increment clicks for analytics
    db_url.clicks += 1
    db.commit()

    # Redirect (HTTP 307)
    return RedirectResponse(url=db_url.target_url)


@app.post("/{short_code}")
def verify_password_and_redirect(
    short_code: str,
    request: Request,
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Verify password and redirect to the target URL."""
    db_url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not db_url:
        db_url = (
            db.query(models.URL).filter(models.URL.custom_alias == short_code).first()
        )

    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    if not pwd_context.verify(password, db_url.hashed_password):
        return templates.TemplateResponse(
            request=request,
            name="password_prompt.html",
            context={"short_code": short_code, "error": "Incorrect password"},
        )

    db_url.clicks += 1
    db.commit()

    # HTTP 303 See Other is correct when redirecting after a POST
    return RedirectResponse(url=db_url.target_url, status_code=303)
