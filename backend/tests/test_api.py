"""API tests using FastAPI's TestClient (no server needed - runs in-process).

Run with:  pytest -v
A temporary SQLite database is used so tests never touch real data.
"""

import os
import sys
from pathlib import Path

# Make the project root importable and point the app at a test database
# BEFORE the app modules are imported.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["DATABASE_URL"] = "sqlite:///./test_health_app.db"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

VALID_PATIENT = {
    "full_name": "Test Patient",
    "date_of_birth": "1990-05-14",
    "email": "test@example.com",
    "glucose": 95,
    "haemoglobin": 14,
    "cholesterol": 180,
}


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


def test_create_patient_generates_remarks(client):
    res = client.post("/api/patients", json=VALID_PATIENT)
    assert res.status_code == 201
    body = res.json()
    assert body["id"] == 1
    assert body["remarks"].startswith("AI Prediction:")
    assert "Low Risk" in body["remarks"]


def test_abnormal_values_flagged(client):
    payload = {**VALID_PATIENT, "glucose": 180, "cholesterol": 260}
    res = client.post("/api/patients", json=payload)
    assert res.status_code == 201
    remarks = res.json()["remarks"]
    assert "diabetes" in remarks.lower()
    assert "cholesterol" in remarks.lower()


def test_invalid_email_rejected(client):
    res = client.post("/api/patients", json={**VALID_PATIENT, "email": "not-an-email"})
    assert res.status_code == 422


def test_future_dob_rejected(client):
    res = client.post("/api/patients", json={**VALID_PATIENT, "date_of_birth": "2099-01-01"})
    assert res.status_code == 422


def test_non_numeric_blood_value_rejected(client):
    res = client.post("/api/patients", json={**VALID_PATIENT, "glucose": "abc"})
    assert res.status_code == 422


def test_duplicate_email_rejected(client):
    assert client.post("/api/patients", json=VALID_PATIENT).status_code == 201
    res = client.post("/api/patients", json=VALID_PATIENT)
    assert res.status_code == 409


def test_read_update_delete_flow(client):
    created = client.post("/api/patients", json=VALID_PATIENT).json()
    pid = created["id"]

    # READ
    assert client.get(f"/api/patients/{pid}").status_code == 200
    assert len(client.get("/api/patients").json()) == 1

    # UPDATE - remarks must be regenerated for the new values
    updated = client.put(
        f"/api/patients/{pid}", json={**VALID_PATIENT, "glucose": 150}
    )
    assert updated.status_code == 200
    assert "Low Risk" not in updated.json()["remarks"]

    # DELETE
    assert client.delete(f"/api/patients/{pid}").status_code == 204
    assert client.get(f"/api/patients/{pid}").status_code == 404
