"""CRUD layer - the only place that talks to the database.

Routers call these functions instead of writing queries themselves,
which keeps database logic in one testable place.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models, schemas
from app.ml.predictor import generate_remarks


def _age_from_dob(dob) -> int:
    from datetime import date

    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _risk_from_remarks(remarks: str) -> str:
    if "High Risk" in remarks:
        return "High"
    if "Moderate Risk" in remarks:
        return "Moderate"
    return "Low"


def _log_history(
    db: Session,
    patient: models.Patient,
    source: str,
    recorded_at: datetime | None = None,
) -> None:
    """Save a snapshot after create or update (same patient ID, new history row)."""
    db.add(
        models.PatientHistory(
            patient_id=patient.id,
            glucose=patient.glucose,
            haemoglobin=patient.haemoglobin,
            cholesterol=patient.cholesterol,
            remarks=patient.remarks,
            risk_level=_risk_from_remarks(patient.remarks),
            source=source,
            recorded_at=recorded_at or datetime.now(timezone.utc),
        )
    )


def backfill_patient_history(db: Session) -> None:
    """One-time snapshot for existing patients that have no history yet."""
    for patient in db.query(models.Patient).all():
        has_history = (
            db.query(models.PatientHistory)
            .filter(models.PatientHistory.patient_id == patient.id)
            .first()
        )
        if not has_history:
            _log_history(db, patient, "create", patient.created_at)
    db.commit()


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


def get_patient_history(db: Session, patient_id: int) -> list[models.PatientHistory]:
    return (
        db.query(models.PatientHistory)
        .filter(models.PatientHistory.patient_id == patient_id)
        .order_by(models.PatientHistory.recorded_at.asc())
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
    db.refresh(patient)
    _log_history(db, patient, "create", patient.created_at)
    db.commit()
    db.refresh(patient)
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
    _log_history(db, patient, "update", patient.updated_at)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: models.Patient) -> None:
    db.delete(patient)
    db.commit()
