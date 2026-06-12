"""Prediction pipeline: turns blood test values into a human-readable remark.

Two layers work together:
1. The trained RandomForest model predicts the OVERALL risk level.
2. Clinical reference-range rules explain WHICH values are abnormal.

The final remark combines both, e.g.:
"AI Prediction: Moderate Risk - Possible prediabetes (glucose 110 mg/dL);
 borderline high cholesterol (215 mg/dL). Haemoglobin normal."
"""

import threading

import joblib
import numpy as np

from app.ml.train_model import MODEL_PATH, RISK_LABELS, train_and_save

_model = None
_lock = threading.Lock()


def _load_model():
    """Load the model once and cache it; train it first if the file is missing."""
    global _model
    if _model is None:
        with _lock:
            if _model is None:  # double-check inside the lock
                if not MODEL_PATH.exists():
                    train_and_save(verbose=False)
                _model = joblib.load(MODEL_PATH)
    return _model


def _findings(glucose: float, haemoglobin: float, cholesterol: float) -> list[str]:
    """Explainable per-metric notes based on standard lab reference ranges."""
    notes: list[str] = []

    if glucose >= 126:
        notes.append(f"possible diabetes (glucose {glucose:g} mg/dL)")
    elif glucose >= 100:
        notes.append(f"possible prediabetes (glucose {glucose:g} mg/dL)")
    elif glucose < 70:
        notes.append(f"low blood sugar / hypoglycemia (glucose {glucose:g} mg/dL)")

    if haemoglobin < 12:
        notes.append(f"possible anaemia (haemoglobin {haemoglobin:g} g/dL)")
    elif haemoglobin > 17.5:
        notes.append(f"elevated haemoglobin (haemoglobin {haemoglobin:g} g/dL)")

    if cholesterol >= 240:
        notes.append(f"high cholesterol (cholesterol {cholesterol:g} mg/dL)")
    elif cholesterol >= 200:
        notes.append(f"borderline high cholesterol (cholesterol {cholesterol:g} mg/dL)")

    return notes


def generate_remarks(age: int, glucose: float, haemoglobin: float, cholesterol: float) -> str:
    model = _load_model()

    features = np.array([[age, glucose, haemoglobin, cholesterol]])
    risk_class = int(model.predict(features)[0])
    confidence = float(model.predict_proba(features)[0][risk_class])

    risk_text = RISK_LABELS[risk_class]
    notes = _findings(glucose, haemoglobin, cholesterol)

    if notes:
        detail = "; ".join(notes).capitalize()
    else:
        detail = "All blood test values are within normal ranges"

    return f"AI Prediction: {risk_text} ({confidence:.0%} confidence) - {detail}."
