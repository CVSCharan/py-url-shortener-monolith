# Learning Curve & Concepts

## SQLAlchemy vs Mongoose/Prisma
- **Mongoose (Node):** You define Schemas and Models. It's NoSQL, so the database doesn't care much about strict schemas.
- **Prisma (Node):** You define a `schema.prisma` file and push the schema to the database.
- **SQLAlchemy (Python):** We define Python classes in `models.py` that inherit from a `Base`. We can use `Base.metadata.create_all()` to push these tables into Postgres (similar to `prisma db push`).

## Pydantic vs Zod
In the Node.js world, you might use Zod to validate `req.body`.
In FastAPI, you define a Pydantic class in `schemas.py`. You put that class in your function signature, and FastAPI *automatically* validates the incoming request against it. If it fails, FastAPI automatically returns a 422 Unprocessable Entity error.

## The Paradigm Shift
Moving from React/SPA (Single Page Application) to HTMX/SSR (Server-Side Rendering) requires a mindset shift. Instead of returning JSON and writing Javascript to update the DOM, the server just returns raw HTML and HTMX handles updating the DOM automatically.
