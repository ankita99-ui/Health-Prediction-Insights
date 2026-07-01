"""CRUD layer - the only place that talks to the database.

Routers call these functions instead of writing queries themselves,
which keeps database logic in one testable place.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import engine
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


def migrate_soft_delete_columns(db: Session) -> None:
    """Add is_deleted / deleted_at to patients on existing databases."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "patients" not in inspector.get_table_names():
        return

    existing = {c["name"] for c in inspector.get_columns("patients")}
    dialect = engine.dialect.name

    with engine.begin() as conn:
        if "is_deleted" not in existing:
            bool_type = "BIT" if dialect == "mssql" else "BOOLEAN"
            default = "0" if dialect == "mssql" else "FALSE"
            conn.execute(
                text(
                    f"ALTER TABLE patients ADD is_deleted {bool_type} NOT NULL DEFAULT {default}"
                )
            )
        if "deleted_at" not in existing:
            conn.execute(text("ALTER TABLE patients ADD deleted_at DATETIME"))


def _active_patients(db: Session):
    return db.query(models.Patient).filter(models.Patient.is_deleted == False)  # noqa: E712


def get_patient(db: Session, patient_id: int) -> models.Patient | None:
    return _active_patients(db).filter(models.Patient.id == patient_id).first()


def get_patient_by_email(db: Session, email: str) -> models.Patient | None:
    return _active_patients(db).filter(models.Patient.email == email).first()


def get_patients(db: Session, skip: int = 0, limit: int = 100) -> list[models.Patient]:
    return (
        _active_patients(db)
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
) -> tuple[models.Patient, str]:
    blood_changed = (
        patient.glucose != data.glucose
        or patient.haemoglobin != data.haemoglobin
        or patient.cholesterol != data.cholesterol
    )
    email_changed = patient.email != data.email
    dob_changed = patient.date_of_birth != data.date_of_birth

    for field, value in data.model_dump().items():
        setattr(patient, field, value)

    if blood_changed or dob_changed:
        patient.remarks = generate_remarks(
            age=_age_from_dob(data.date_of_birth),
            glucose=data.glucose,
            haemoglobin=data.haemoglobin,
            cholesterol=data.cholesterol,
        )

    db.commit()
    db.refresh(patient)

    if blood_changed:
        _log_history(db, patient, "update", patient.updated_at)
        db.commit()
        db.refresh(patient)
        update_type = "blood_values"
    elif email_changed and not blood_changed and not dob_changed:
        update_type = "email_only"
    else:
        update_type = "profile"

    return patient, update_type


def delete_patient(db: Session, patient: models.Patient) -> None:
    """Soft delete: hide from the app but keep the row (and history) in SQL."""
    deleted_at = datetime.now(timezone.utc)
    _log_history(db, patient, "delete", deleted_at)
    patient.is_deleted = True
    patient.deleted_at = deleted_at
    # Free the email so the same address can be used for a new patient later.
    if not patient.email.endswith(f".deleted.{patient.id}"):
        patient.email = f"{patient.email}.deleted.{patient.id}"
    db.commit()
