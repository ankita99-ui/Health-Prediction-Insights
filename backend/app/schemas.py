"""Pydantic schemas - they validate every request and shape every response.

Why separate from models.py?
- models.py  = how data is STORED (database layer)
- schemas.py = how data is EXCHANGED over the API (validation layer)
Keeping them separate means the API contract can evolve independently
from the database.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _parse_dob(value) -> date:
    """Validate YYYY-MM-DD (or date object) using strict calendar parsing."""
    if isinstance(value, date):
        d = value
    elif isinstance(value, str):
        normalized = value.strip().replace("/", "-")
        try:
            d = datetime.strptime(normalized, "%Y-%m-%d").date()
        except ValueError as exc:
            error_msg = str(exc)
            if "day is out of range" in error_msg:
                raise ValueError("Error: Invalid day for the specified month/year.") from exc
            if "unconverted data remains" in error_msg:
                raise ValueError("Error: Text does not match the YYYY-MM-DD format.") from exc
            raise ValueError("Error: Invalid date, year, or month.") from exc
    else:
        raise ValueError("Please enter a valid date of birth")

    if d > date.today():
        raise ValueError("Error: DOB cannot be a future date.")
    if d < date(1900, 1, 1):
        raise ValueError("Date of birth must be on or after 1900-01-01")
    return d


class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Asha Patel"])
    date_of_birth: date = Field(..., examples=["1990-05-14"])
    email: EmailStr = Field(..., examples=["asha@example.com"])
    glucose: float = Field(..., gt=0, le=1000, description="Fasting glucose in mg/dL")
    haemoglobin: float = Field(..., gt=0, le=30, description="Haemoglobin in g/dL")
    cholesterol: float = Field(..., gt=0, le=1000, description="Total cholesterol in mg/dL")

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, value) -> date:
        return _parse_dob(value)

    @field_validator("full_name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Full name cannot be blank")
        return cleaned


class PatientCreate(PatientBase):
    """Body for POST /api/patients - remarks are generated, not accepted."""


class PatientUpdate(PatientBase):
    """Body for PUT /api/patients/{id} - full replacement of the record."""


class PatientOut(PatientBase):
    """Response shape - includes server-generated fields."""

    id: int
    remarks: str
    created_at: datetime
    updated_at: datetime

    # Lets Pydantic read attributes straight from the SQLAlchemy object.
    model_config = ConfigDict(from_attributes=True)


class PatientUpdateOut(PatientOut):
    """PUT response — includes what kind of change was saved."""

    update_type: str  # blood_values | email_only | profile


class HistoryOut(BaseModel):
    """One blood-test snapshot for a patient (create or update)."""

    id: int
    patient_id: int
    glucose: float
    haemoglobin: float
    cholesterol: float
    remarks: str
    risk_level: str
    source: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
