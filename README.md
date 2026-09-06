# URL Shortener (Monolith)

This project demonstrates a 100% Python Monolithic web application using Server-Side Rendering (SSR). 
Because we use Jinja2 to render HTML from the server and HTMX for interactivity, there is no separate frontend client repository. The FastAPI server handles both the backend logic and the frontend presentation.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Frontend Template Engine:** Jinja2
- **Frontend Interactivity:** HTMX

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
