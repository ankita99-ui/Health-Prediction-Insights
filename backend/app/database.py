"""Database setup: connects SQLAlchemy to Microsoft SQL Server.

Default connection (no configuration needed on this machine):
    server   : localhost\\MSSQL  (your local SQL Server 2022 instance)
    database : HealthDB
    auth     : Windows Authentication (trusted connection - no password)
    driver   : ODBC Driver 17 for SQL Server

Everything can be overridden with environment variables, and setting
DATABASE_URL replaces the whole thing (the test suite uses this to run
against a throwaway SQLite file).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load settings from a .env file (project root), so users can configure the
# database without touching code. Real environment variables still win.
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Explicit override (e.g. tests use sqlite:///./test_health_app.db)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    )
else:
    # Build the SQL Server connection URL piece by piece.
    # URL.create handles special characters (like the \ in localhost\MSSQL) safely.
    url = URL.create(
        "mssql+pyodbc",
        host=os.getenv("MSSQL_SERVER", r"localhost\MSSQL"),
        database=os.getenv("MSSQL_DATABASE", "HealthDB"),
        query={
            "driver": os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server"),
            "trusted_connection": "yes",  # Windows Authentication
        },
    )
    engine = create_engine(url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class that all ORM models inherit from."""


def get_db():
    """FastAPI dependency: opens a DB session per request and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
