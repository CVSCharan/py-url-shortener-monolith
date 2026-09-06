# URL Shortener (Monolith)

This project demonstrates a 100% Python Monolithic web application using Server-Side Rendering (SSR).
Because we use Jinja2 to render HTML from the server and HTMX for interactivity, there is no separate frontend client repository. The FastAPI server handles both the backend logic and the frontend presentation.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (with Alembic for migrations)
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Frontend Template Engine:** Jinja2
- **Frontend Interactivity:** HTMX
- **Styling:** Tailwind CSS
- **Code Quality:** Ruff (Linting/Formatting), Pyright (Strict Type Checking) & pre-commit

## Premium Features Added
- **Custom Aliases:** Users can define their own URL endings (e.g., `/my-promo`).
- **Password Protection:** Secure destination links with a hashed password (bcrypt).
- **Expiration Dates:** Links automatically expire after a set time, returning a 410 Gone status.
- **Inline QR Modals:** Each link gets a dynamically generated QR code available via an HTMX modal.
- **Rate Limiting:** IP-based rate limiting (5 requests/minute) using `slowapi` to prevent abuse.
- **Dashboard & Pagination:** A dedicated dashboard at `/dashboard` to view all generated links.
- **Jinja2 Components & DRY Layouts:** Reusable UI macros (mimicking React components) and a master `base.html` template for 100% consistent UI across the app.
- **Shadcn UI Aesthetics:** Premium high-contrast Zinc monochrome theme with Inter typography.

## How to Run

1. **Set up your Database:**
   Create a PostgreSQL database (e.g., on Neon.tech) and paste the connection string into the `.env` file.
   ```
   DATABASE_URL=postgresql://user:password@host/db
   ```

2. **Activate the environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt # (or just install the packages we used)
   ```

4. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```
