"""SQLAlchemy ORM models - these classes map directly to database tables."""

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    """One row = one patient record with blood test results and the AI remark."""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)

    # Blood test values
    glucose: Mapped[float] = mapped_column(Float, nullable=False)        # mg/dL (fasting)
    haemoglobin: Mapped[float] = mapped_column(Float, nullable=False)    # g/dL
    cholesterol: Mapped[float] = mapped_column(Float, nullable=False)    # mg/dL (total)

    # Filled automatically by the ML model - never typed by the user.
    remarks: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    history: Mapped[list["PatientHistory"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="PatientHistory.recorded_at",
    )


class PatientHistory(Base):
    """One snapshot per create/update — tracks how blood values and risk change over time."""

    __tablename__ = "patient_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    glucose: Mapped[float] = mapped_column(Float, nullable=False)
    haemoglobin: Mapped[float] = mapped_column(Float, nullable=False)
    cholesterol: Mapped[float] = mapped_column(Float, nullable=False)
    remarks: Mapped[str] = mapped_column(String(500), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # Low / Moderate / High
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # create / update
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    patient: Mapped["Patient"] = relationship(back_populates="history")
