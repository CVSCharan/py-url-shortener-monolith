# How the URL Shortener Works

1. **User Visits Root (`/`)**
   - The user opens `http://127.0.0.1:8000`.
   - FastAPI's `read_root` function is triggered.
   - It queries the database for all existing URLs.
   - It passes that data to `index.html` (Jinja2), which generates the final webpage.

2. **User Submits Form**
   - The user pastes a long URL and clicks submit.
   - HTMX catches the submit event and sends a POST request to `/shorten`.
   - FastAPI's `shorten_url` function validates the input, generates a random 6-character code, and saves both to PostgreSQL.
   - The server responds with *just* the HTML for the updated table (using `partials/url_list.html`).
   - HTMX swaps out the old table for the new one on the screen.

3. **User Clicks a Short URL**
   - The user navigates to `http://127.0.0.1:8000/aB3x9Z`.
   - FastAPI's `redirect_to_target` function looks up `aB3x9Z` in PostgreSQL.
   - If found, it increments the click count, and returns an HTTP 307 Redirect to the original long URL.
