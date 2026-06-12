# Containerises the FastAPI backend.
# Inside Docker we default to SQLite because the host's SQL Server is not
# visible from the container; pass DATABASE_URL / MSSQL_SERVER env vars to
# point it at a real SQL Server instance.

FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

WORKDIR /app/backend

# Train the ML model at build time so the container starts instantly
RUN python -m app.ml.train_model

ENV DATABASE_URL=sqlite:///./health_app.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
