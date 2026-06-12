"""Pydantic schemas - they validate every request and shape every response.

Why separate from models.py?
- models.py  = how data is STORED (database layer)
- schemas.py = how data is EXCHANGED over the API (validation layer)
Keeping them separate means the API contract can evolve independently
from the database.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Asha Patel"])
    date_of_birth: date = Field(..., examples=["1990-05-14"])
    email: EmailStr = Field(..., examples=["asha@example.com"])
    glucose: float = Field(..., gt=0, le=1000, description="Fasting glucose in mg/dL")
    haemoglobin: float = Field(..., gt=0, le=30, description="Haemoglobin in g/dL")
    cholesterol: float = Field(..., gt=0, le=1000, description="Total cholesterol in mg/dL")

    @field_validator("date_of_birth")
    @classmethod
    def dob_cannot_be_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value

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
