# Architecture: Monolithic Server-Side Rendering

## Why Monolithic?
In Project 1 (To-Do app), we strictly decoupled the frontend (Streamlit) from the backend (FastAPI). 
For this project, we are demonstrating a **Monolithic** architecture. The FastAPI server acts as BOTH the backend API and the frontend web server.

## HTMX + Jinja2 (The "New" Old Way)
Instead of the backend sending raw JSON data for a React frontend to process and render, the backend renders the HTML itself using **Jinja2**. 

When a user submits the "Shorten URL" form, **HTMX** intercepts the submission, sends the data to FastAPI, and FastAPI responds with the updated HTML table. HTMX then seamlessly injects that new HTML into the page without a full browser refresh.

## Database Integration
We introduced a traditional relational database (PostgreSQL) using **SQLAlchemy** (an ORM).
- `database.py` manages the connection pool.
- `models.py` defines the actual structure of the Postgres tables.
- `schemas.py` uses Pydantic to validate the incoming data from the user before we attempt to save it to the database.
