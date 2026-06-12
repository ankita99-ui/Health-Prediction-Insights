# MIRA — Health Prediction Application

A health prediction app that manages patient blood test records (CRUD) and
uses a trained Machine Learning model to predict a health risk level, which is
saved in the **Remarks** field of every record.

Built for the *Junior AI/ML Developer — Task 1* assessment.

## Features

| Feature | Description |
| --- | --- |
| 🗂️ **Patient Management** | Full CRUD — create, view, update and delete patient records, with validation at every step (email format, no future date of birth, numeric blood values — checked in the UI **and** again on the server with Pydantic) |
| 🤖 **AI Prediction Engine** | A trained RandomForest classifier (scikit-learn) predicts Low / Moderate / High health risk from age, glucose, haemoglobin and cholesterol, with a confidence score — written automatically into the Remarks field |
| 📈 **Real-Time Dashboard** | Live KPI cards, search, risk-level filters and Plotly charts that refresh automatically after every change |
| ⬇️ **CSV Export** | Download the complete patient dataset as a CSV file for reports and offline analysis |
| 🧪 **Risk Analysis** | Per-metric explanations show exactly *which* blood values are outside normal clinical ranges, so the prediction is never a black box |
| 🔐 **Secure Database** | Records stored in Microsoft SQL Server (works with SSMS) via SQLAlchemy ORM, using Windows Authentication — no passwords or secrets in the code |

Plus: a **REST API** (FastAPI) with auto-generated Swagger docs at `/docs`,
and a Streamlit frontend with a landing page, dashboard and guided
add/update/delete flows.

## Architecture

```
┌──────────────┐   HTTP (JSON)   ┌──────────────┐   SQLAlchemy   ┌────────────┐
│  Streamlit   │ ──────────────► │   FastAPI    │ ─────────────► │ SQL Server │
│  frontend    │ ◄────────────── │   backend    │ ◄───────────── │ (HealthDB) │
└──────────────┘                 └──────┬───────┘                └────────────┘
                                        │
                                        ▼
                                 ┌──────────────┐
                                 │ RandomForest │  predicts risk level →
                                 │   ML model   │  fills the Remarks field
                                 └──────────────┘
```

## Tech Stack

| Layer      | Technology                  | Why                                          |
| ---------- | --------------------------- | -------------------------------------------- |
| Frontend   | Streamlit                   | Pure-Python UI, no HTML/CSS/JS needed        |
| Backend    | FastAPI + Uvicorn           | Fast, modern, automatic validation and docs  |
| Database   | SQL Server (via SQLAlchemy) | Robust relational storage, manageable in SSMS|
| ML         | scikit-learn RandomForest   | Reliable classifier, easy to train and ship  |
| Validation | Pydantic v2                 | Declarative request/response validation      |

## Project Structure

```
task1/
├── backend/                  # Everything server-side
│   ├── app/                  # FastAPI package
│   │   ├── main.py           # App entry point, startup logic
│   │   ├── database.py       # SQL Server connection (SQLAlchemy engine/session)
│   │   ├── models.py         # ORM model = database table definition
│   │   ├── schemas.py        # Pydantic schemas = request/response validation
│   │   ├── crud.py           # All database operations in one place
│   │   ├── routers/
│   │   │   └── patients.py   # REST endpoints (CRUD)
│   │   └── ml/
│   │       ├── train_model.py # ML training pipeline (data → train → save)
│   │       └── predictor.py   # Loads the model, generates the Remarks text
│   ├── models/               # Trained model + metrics (health_model.joblib)
│   ├── database/
│   │   └── create_database.sql # Schema script for SSMS (documentation)
│   └── tests/
│       └── test_api.py       # API tests (pytest)
├── frontend/                 # Everything client-side
│   ├── streamlit_app.py      # Streamlit app (talks only to the API)
│   ├── ui/
│   │   ├── home.py           # Home page + dashboard components
│   │   └── styles.py         # All custom CSS in one place
│   └── .streamlit/
│       └── config.toml       # Streamlit theme
├── seed_data.py              # Optional: fill the DB with 20 sample patients
├── requirements.txt
├── .env.example              # Configuration template (no secrets committed)
├── Dockerfile
└── README.md
```

## Quick Start (Windows)

After the one-time setup below, just **double-click `start_app.bat`** in the
project root - it opens the backend and frontend in two windows and the
website appears at http://localhost:8501.

## One-Time Setup (Windows)

Prerequisites: Python 3.11+, SQL Server with ODBC Driver 17 (both already
present if you use SSMS locally).

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database (SQL Server users - one time only).
#    Either run backend/database/create_database.sql in SSMS,
#    or run this one-liner (adjust the instance name to yours):
sqlcmd -S "localhost\MSSQL" -E -Q "IF DB_ID('HealthDB') IS NULL CREATE DATABASE HealthDB"

# 4. Train the ML model (also happens automatically on first start)
cd backend
python -m app.ml.train_model
```

### Database configuration

The app reads its settings from a `.env` file in the project root.
Copy `.env.example` to `.env` and adjust:

- **Have SQL Server?** Set `MSSQL_SERVER` to *your* instance name - the same
  "Server name" you type into SSMS (common values: `localhost\SQLEXPRESS`,
  `localhost\MSSQL`, or just `localhost`). Windows Authentication is used,
  so no password is needed.
- **No SQL Server?** Uncomment `DATABASE_URL=sqlite:///./health_app.db` in
  `.env` and the app runs with a zero-installation SQLite file instead -
  skip step 3 entirely.

## Running the App (every time)

Easiest way: double-click **`start_app.bat`** in the project root.

Manual way - the app has two parts, so you need **two terminals**:

```powershell
# Terminal 1 - backend API (keep this window open)
cd e:\task1\backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
# wait until you see "Application startup complete"
# API docs: http://127.0.0.1:8000/docs
```

```powershell
# Terminal 2 - frontend website (keep this window open)
cd e:\task1\frontend
..\.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
# Website: http://localhost:8501
```

> **Notes**
> - Run each command from the folder shown above. Running
>   `streamlit run streamlit_app.py` from the project root fails with
>   *"No such file or directory"* because the file lives in `frontend/`.
> - Only one copy can run at a time. A *"port already in use"* error means
>   the app is already running - just open http://localhost:8501.
> - (Optional) `python seed_data.py` from the project root fills the
>   database with 20 sample patients for a demo.

By default the app connects to `localhost\MSSQL`, database `HealthDB`, using
Windows Authentication. Override via environment variables (see
`.env.example`): `MSSQL_SERVER`, `MSSQL_DATABASE`, `MSSQL_DRIVER`, or a full
`DATABASE_URL`.

## API Endpoints

| Method | Endpoint             | Description                              |
| ------ | -------------------- | ---------------------------------------- |
| GET    | `/api/patients`      | List all patients                        |
| GET    | `/api/patients/{id}` | Get one patient                          |
| POST   | `/api/patients`      | Create patient (AI fills `remarks`)      |
| PUT    | `/api/patients/{id}` | Update patient (AI re-fills `remarks`)   |
| DELETE | `/api/patients/{id}` | Delete patient                           |

Example request — `POST /api/patients`:

```json
{
  "full_name": "Asha Patel",
  "date_of_birth": "1990-05-14",
  "email": "asha@example.com",
  "glucose": 132,
  "haemoglobin": 10.5,
  "cholesterol": 245
}
```

Example response (`201 Created`):

```json
{
  "full_name": "Asha Patel",
  "date_of_birth": "1990-05-14",
  "email": "asha@example.com",
  "glucose": 132.0,
  "haemoglobin": 10.5,
  "cholesterol": 245.0,
  "id": 1,
  "remarks": "AI Prediction: High Risk (97% confidence) - Possible diabetes (glucose 132 mg/dL); possible anaemia (haemoglobin 10.5 g/dL); high cholesterol (cholesterol 245 mg/dL).",
  "created_at": "2026-06-12T09:00:00",
  "updated_at": "2026-06-12T09:00:00"
}
```

## How the ML Prediction Works

1. `app/ml/train_model.py` generates a synthetic dataset of 6,000 patients
   based on **real medical reference ranges** (fasting glucose, haemoglobin,
   total cholesterol), labels each one Low/Moderate/High risk, and trains a
   **RandomForest classifier** (~97% accuracy on the held-out test set).
2. The model is saved to `models/health_model.joblib`.
3. On every Create/Update, `app/ml/predictor.py` predicts the risk level with
   a confidence score, and rule-based checks add an explanation of which
   values are out of range. The combined text is stored in `remarks`.

> Disclaimer: this is a coding-assessment demo, **not** medical advice.

## Testing

```powershell
cd backend
pytest -v
```

Tests cover: creation with AI remarks, abnormal-value flagging, invalid email,
future date of birth, non-numeric values, duplicate email, and the full
read → update → delete flow. They run against a temporary SQLite database, so
your SQL Server data is never touched.

## Security Notes

- No passwords or API keys are stored in the repository
- Database credentials come from environment variables (`.env` is gitignored)
- Windows Authentication is used locally, so no secret is needed at all
