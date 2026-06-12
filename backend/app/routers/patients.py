"""Patient REST endpoints - the full CRUD surface of the application."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("", response_model=list[schemas.PatientOut])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """READ (all): return patients, newest first, with pagination."""
    return crud.get_patients(db, skip=skip, limit=limit)


@router.get("/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """READ (one): return a single patient or 404."""
    patient = crud.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("", response_model=schemas.PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    """CREATE: validate, run the ML prediction, store, and return the record."""
    if crud.get_patient_by_email(db, payload.email):
        raise HTTPException(
            status_code=409, detail="A patient with this email already exists"
        )
    return crud.create_patient(db, payload)


@router.put("/{patient_id}", response_model=schemas.PatientOut)
def update_patient(
    patient_id: int, payload: schemas.PatientUpdate, db: Session = Depends(get_db)
):
    """UPDATE: replace the record and regenerate the AI remarks."""
    patient = crud.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing = crud.get_patient_by_email(db, payload.email)
    if existing and existing.id != patient_id:
        raise HTTPException(
            status_code=409, detail="A patient with this email already exists"
        )
    return crud.update_patient(db, patient, payload)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """DELETE: remove the record; 204 means success with no response body."""
    patient = crud.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    crud.delete_patient(db, patient)
