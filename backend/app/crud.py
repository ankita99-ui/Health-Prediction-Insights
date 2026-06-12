"""CRUD layer - the only place that talks to the database.

Routers call these functions instead of writing queries themselves,
which keeps database logic in one testable place.
"""

from sqlalchemy.orm import Session

from app import models, schemas
from app.ml.predictor import generate_remarks


def _age_from_dob(dob) -> int:
    from datetime import date

    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def get_patient(db: Session, patient_id: int) -> models.Patient | None:
    return db.get(models.Patient, patient_id)


def get_patient_by_email(db: Session, email: str) -> models.Patient | None:
    return db.query(models.Patient).filter(models.Patient.email == email).first()


def get_patients(db: Session, skip: int = 0, limit: int = 100) -> list[models.Patient]:
    return (
        db.query(models.Patient)
        .order_by(models.Patient.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_patient(db: Session, data: schemas.PatientCreate) -> models.Patient:
    remarks = generate_remarks(
        age=_age_from_dob(data.date_of_birth),
        glucose=data.glucose,
        haemoglobin=data.haemoglobin,
        cholesterol=data.cholesterol,
    )
    patient = models.Patient(**data.model_dump(), remarks=remarks)
    db.add(patient)
    db.commit()
    db.refresh(patient)  # reload so auto-generated fields (id, timestamps) are populated
    return patient


def update_patient(
    db: Session, patient: models.Patient, data: schemas.PatientUpdate
) -> models.Patient:
    for field, value in data.model_dump().items():
        setattr(patient, field, value)

    # Blood values may have changed, so the AI prediction must be refreshed too.
    patient.remarks = generate_remarks(
        age=_age_from_dob(data.date_of_birth),
        glucose=data.glucose,
        haemoglobin=data.haemoglobin,
        cholesterol=data.cholesterol,
    )
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: models.Patient) -> None:
    db.delete(patient)
    db.commit()
