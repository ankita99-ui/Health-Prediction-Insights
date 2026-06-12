"""ML training pipeline.

Since no public labelled dataset matches exactly (age, glucose, haemoglobin,
cholesterol -> risk level), we generate a synthetic dataset using real
medical reference ranges, label it with clinical rules + a little noise,
and train a RandomForest classifier on it.

Risk classes:
    0 = Low risk      (all values within normal range)
    1 = Moderate risk (one borderline/abnormal value)
    2 = High risk     (severely abnormal or multiple abnormal values)

Run directly to (re)train:  python -m app.ml.train_model
"""

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "health_model.joblib"

RISK_LABELS = {0: "Low Risk", 1: "Moderate Risk", 2: "High Risk"}


def _severity_score(glucose: float, haemoglobin: float, cholesterol: float) -> int:
    """Clinical-rule scoring used to label the synthetic data.

    Reference ranges (standard lab values):
      Fasting glucose  : normal 70-99, prediabetes 100-125, diabetes >=126 mg/dL
      Haemoglobin      : normal 12-17.5 g/dL (combined adult range)
      Total cholesterol: desirable <200, borderline 200-239, high >=240 mg/dL
    """
    score = 0
    if glucose >= 126 or glucose < 60:
        score += 2
    elif glucose >= 100 or glucose < 70:
        score += 1

    if haemoglobin < 8 or haemoglobin > 20:
        score += 2
    elif haemoglobin < 12 or haemoglobin > 17.5:
        score += 1

    if cholesterol >= 240:
        score += 2
    elif cholesterol >= 200:
        score += 1
    return score


def generate_dataset(n_samples: int = 6000, seed: int = 42):
    """Create synthetic patients spanning normal and abnormal value ranges."""
    rng = np.random.default_rng(seed)

    age = rng.integers(18, 90, n_samples)
    glucose = np.clip(rng.normal(105, 35, n_samples), 40, 400)
    haemoglobin = np.clip(rng.normal(13.5, 2.5, n_samples), 4, 22)
    cholesterol = np.clip(rng.normal(195, 45, n_samples), 80, 400)

    X = np.column_stack([age, glucose, haemoglobin, cholesterol])

    y = np.empty(n_samples, dtype=int)
    for i in range(n_samples):
        score = _severity_score(glucose[i], haemoglobin[i], cholesterol[i])
        y[i] = 0 if score == 0 else (1 if score == 1 else 2)

    # Flip 3% of labels so the model sees realistic, imperfect data
    # instead of memorising the exact rules.
    noise_idx = rng.choice(n_samples, size=int(0.03 * n_samples), replace=False)
    y[noise_idx] = rng.integers(0, 3, len(noise_idx))

    return X, y


def train_and_save(verbose: bool = True) -> Path:
    """Full pipeline: generate data -> split -> train -> evaluate -> save."""
    X, y = generate_dataset()

    # stratify keeps the same class balance in train and test sets.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    if verbose:
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
        print(classification_report(y_test, y_pred, target_names=list(RISK_LABELS.values())))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # Save metrics alongside the model so the UI can display real numbers.
    metrics_path = MODEL_PATH.parent / "metrics.json"
    metrics_path.write_text(
        json.dumps({"accuracy": round(float(accuracy_score(y_test, y_pred)), 4)})
    )

    if verbose:
        print(f"Model saved to {MODEL_PATH}")
    return MODEL_PATH


if __name__ == "__main__":
    train_and_save()
