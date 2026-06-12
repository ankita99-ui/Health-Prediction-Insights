# MIRA Health Prediction — Interview Preparation & Learning Guide

**Project:** Health Prediction Application (Task 1 — Junior AI/ML Developer)  
**Stack:** Streamlit (frontend) + FastAPI (backend) + SQL Server + scikit-learn  
**Audience:** Freshers — explanations are simple enough for non-technical readers too.

---

## Table of Contents

1. [Project at a Glance](#1-project-at-a-glance)
2. [How the App Works (Big Picture)](#2-how-the-app-works-big-picture)
3. [Phases of Building This Project](#3-phases-of-building-this-project)
4. [Learning Section — Every Concept Explained](#4-learning-section--every-concept-explained)
5. [Interview Questions & Answers](#5-interview-questions--answers)
6. [Common Beginner Mistakes & How to Avoid Them](#6-common-beginner-mistakes--how-to-avoid-them)
7. [Demo Video Talking Points](#7-demo-video-talking-points)
8. [Quick Cheat Sheet](#8-quick-cheat-sheet)

---

## 1. Project at a Glance

### What does this app do?

A **health prediction web app** that:

1. Stores **patient records** (name, date of birth, email, blood test values).
2. Lets users **Create, Read, Update, Delete (CRUD)** those records.
3. Uses a **Machine Learning model** to predict a **health risk level** (Low / Moderate / High).
4. Saves the prediction automatically in the **Remarks** field (user does not type it).

### What did the company ask for?

| Requirement | What we built |
|-------------|---------------|
| CRUD | Add, view, edit, delete patients |
| User interface | Streamlit website with Home + Dashboard + forms |
| Validation | Email, date of birth, numeric blood values |
| Persistent storage | SQL Server database (`HealthDB`) |
| AI/ML integration | RandomForest model + health remarks |

### Folder structure (simple view)

```
task1/
├── frontend/          ← Website (what you see in the browser)
│   ├── streamlit_app.py
│   └── ui/            ← Home page design, styles
├── backend/           ← API + database + ML (runs in the background)
│   ├── app/           ← FastAPI code
│   ├── models/        ← Trained ML file (.joblib)
│   └── database/      ← SQL script for SSMS
├── start_app.bat      ← One-click start (Windows)
├── seed_data.py       ← Optional: add 20 sample patients
└── README.md
```

---

## 2. How the App Works (Big Picture)

### Text diagram — three layers

```
┌─────────────────────────────────────────────────────────────────┐
│  YOU (browser)                                                  │
│  Open: http://localhost:8501                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND  (Streamlit)                                          │
│  • Shows forms, tables, charts                                  │
│  • Does NOT touch the database directly                         │
│  • Sends HTTP requests (like asking a waiter to bring food)     │
└────────────────────────────┬────────────────────────────────────┘
                             │  JSON over HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND  (FastAPI)                                             │
│  • Validates input (Pydantic)                                   │
│  • Calls ML model for prediction                                │
│  • Saves/reads data via SQLAlchemy                              │
└────────────────────────────┬────────────────────────────────────┘
                             │  SQL
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  DATABASE  (SQL Server — HealthDB)                              │
│  Table: patients (one row = one patient)                      │
└─────────────────────────────────────────────────────────────────┘
```

### What happens when you click "Save Patient"?

```
Step 1: You fill the form (name, email, glucose, etc.)
           │
Step 2: Streamlit sends POST /api/patients with JSON body
           │
Step 3: FastAPI checks data (valid email? future DOB? numbers?)
           │  ❌ Bad data → error 422, nothing saved
           │  ✅ Good data → continue
           │
Step 4: ML model reads age + glucose + haemoglobin + cholesterol
           │
Step 5: Model outputs: "High Risk (96% confidence)" + explanations
           │
Step 6: Row inserted into SQL Server (including remarks)
           │
Step 7: JSON response back to Streamlit → success message + risk card
```

---

## 3. Phases of Building This Project

If you built this from scratch, follow this order. Each phase depends on the previous one.

### Phase 1 — Environment & structure

**Goal:** Python works, folders exist, libraries installed.

- Install Python 3.11+
- Create `backend/` and `frontend/` folders
- `python -m venv .venv`
- `pip install -r requirements.txt`

**Mistake to avoid:** Running commands from the wrong folder (e.g. `streamlit run` from project root instead of `frontend/`).

---

### Phase 2 — Database

**Goal:** Data survives after closing the app.

- Design table: `patients` (id, full_name, date_of_birth, email, glucose, haemoglobin, cholesterol, remarks, timestamps)
- Connect with SQLAlchemy + pyodbc to SQL Server
- Create `HealthDB` in SSMS (database must exist; app creates the *table* on startup)

**Mistake to avoid:** Assuming the app creates the database automatically — it usually only creates the *table* inside an existing database.

---

### Phase 3 — Machine Learning

**Goal:** Turn blood values into a risk label + readable remark.

- Generate synthetic training data using real medical reference ranges
- Label: Low / Moderate / High risk
- Train RandomForest classifier
- Save model: `backend/models/health_model.joblib`
- `predictor.py`: load model once, predict on every create/update

**Mistake to avoid:** Training inside every request (slow). Load the model once and reuse it.

---

### Phase 4 — Backend API (FastAPI)

**Goal:** REST endpoints for CRUD + validation.

| Endpoint | Action |
|----------|--------|
| GET `/api/patients` | List all |
| GET `/api/patients/{id}` | Get one |
| POST `/api/patients` | Create + AI remarks |
| PUT `/api/patients/{id}` | Update + regenerate remarks |
| DELETE `/api/patients/{id}` | Delete |

- Pydantic schemas validate every request
- `crud.py` = all database logic in one place
- Test at `http://127.0.0.1:8000/docs` before building the UI

**Mistake to avoid:** Putting SQL queries inside route functions — hard to test and maintain.

---

### Phase 5 — Frontend (Streamlit)

**Goal:** User-friendly UI that calls the API only.

- Home page: hero + buttons (no sidebar)
- Dashboard: KPI cards, table, Plotly charts, CSV export
- Add / Update / Delete pages with forms
- Sidebar navigation on inner pages only

**Mistake to avoid:** Streamlit talking to the database directly — breaks the "API integration" story for interviews.

---

### Phase 6 — Testing & documentation

**Goal:** Prove it works; others can run it.

- `pytest` in `backend/tests/` (uses temporary SQLite, not your real data)
- README with setup steps
- `.gitignore` — no `.env`, no `.db`, no passwords
- Optional: `seed_data.py` for demo patients

---

## 4. Learning Section — Every Concept Explained

### 4.1 General software terms

#### Application / App
Software you use to do a job. Here: manage patients and see AI health risk.

**Example:** Like a clinic register book, but on a computer.

#### Frontend vs Backend

| Part | Role | Analogy |
|------|------|---------|
| **Frontend** | What you see and click | Restaurant dining area + menu |
| **Backend** | Logic, database, AI | Kitchen — you don't go there, but food comes from there |

#### Client vs Server

- **Client** asks (browser, Streamlit app).
- **Server** answers (FastAPI on port 8000).

#### Port (8000, 8501)

A "door number" on your computer.  
- `8501` = Streamlit website  
- `8000` = API  

**Example:** One building (your PC), many rooms (ports).

#### localhost

Means "this same computer." `http://localhost:8501` only works on the machine where the server is running.

---

### 4.2 Web & API concepts

#### HTTP

The language browsers and APIs use to talk. Common "verbs":

| Method | Meaning | In our app |
|--------|---------|------------|
| GET | Read / fetch | List patients |
| POST | Create new | Add patient |
| PUT | Replace / update | Edit patient |
| DELETE | Remove | Delete patient |

#### REST API

A standard way to expose data over URLs. Each URL + method = one action.

**Example:** `POST /api/patients` = "create a new patient."

#### JSON

Text format for data exchange. Looks like:

```json
{
  "full_name": "Asha Patel",
  "glucose": 95,
  "email": "asha@example.com"
}
```

**Why:** Frontend and backend can use different languages but agree on JSON.

#### Status codes

| Code | Meaning |
|------|---------|
| 200 | OK — success (read/update) |
| 201 | Created — new record saved |
| 204 | Success, no body (delete) |
| 404 | Not found — wrong ID |
| 409 | Conflict — duplicate email |
| 422 | Validation failed — bad input |

#### Request body vs Response body

- **Request:** what the client sends (form data as JSON).
- **Response:** what the server returns (saved patient + AI remarks).

---

### 4.3 Python frameworks we used

#### Streamlit

Python library to build web UIs quickly — forms, tables, charts without HTML/CSS.

**When to say in interview:** "I chose Streamlit because the role is Python-focused and I could build a clean UI fast while spending more time on API and ML."

#### FastAPI

Modern Python framework for building APIs. Auto-generates Swagger docs at `/docs`.

**Benefits:** Speed, automatic validation with Pydantic, industry standard.

#### Uvicorn

The program that *runs* FastAPI (like an engine for the API).

---

### 4.4 Database concepts

#### Database vs Table

- **Database** = folder (`HealthDB`)
- **Table** = spreadsheet (`patients` — rows = patients, columns = fields)

#### SQL Server

Microsoft's relational database. You manage it with **SSMS** (SQL Server Management Studio).

#### SQL

Language to query databases: `SELECT * FROM patients`

#### ORM (SQLAlchemy)

Write Python instead of raw SQL:

```python
db.add(patient)
db.commit()
```

SQLAlchemy generates the SQL for SQL Server.

**Benefit:** Same code can target SQL Server or SQLite by changing config.

#### Primary Key (id)

Unique number for each row. Auto-increments (1, 2, 3…).

#### UNIQUE (email)

No two patients can share the same email.

#### Windows Authentication

Login to SQL Server using your Windows user — no password in code. Good for security.

#### Persistent storage

Data stays after closing the app (unlike variables in memory).

---

### 4.5 Validation (Pydantic)

**Validation** = checking input before saving.

Rules in our app:

- Email must look like an email
- Date of birth cannot be in the future
- Glucose, haemoglobin, cholesterol must be numbers in range

**Pydantic** = define rules in a Python class; FastAPI applies them automatically.

**Why validate twice?** UI checks for fast feedback; server checks because clients can bypass the UI (Postman, hackers).

---

### 4.6 Machine Learning concepts

#### Machine Learning (ML)

Computer learns patterns from data instead of only following fixed if-rules.

**Our task:** predict risk from blood test numbers.

#### Features (inputs)

What the model reads:

- Age (from date of birth)
- Glucose
- Haemoglobin
- Cholesterol

#### Labels (outputs)

What we predict: **Low / Moderate / High** risk (3 classes).

#### Classification vs Regression

- **Classification** → category (Low/Moderate/High)
- **Regression** → number (e.g. predict exact glucose)

We use **classification**.

#### Training vs Prediction

| Phase | What happens |
|-------|----------------|
| **Training** | Model learns from many examples (`train_model.py`) |
| **Prediction** | Model guesses for one new patient (`predictor.py`) |

#### Train / Test split

Hide 20% of data during training, then test accuracy on that hidden part — honest measure of performance.

#### RandomForest

Many decision trees vote; majority wins. Good for tabular data, handles non-linear patterns.

**Simple analogy:** 150 doctors each vote on risk; final answer = majority vote.

#### Overfitting

Model memorizes training data but fails on new patients. We reduce it with train/test split and label noise in synthetic data.

#### Confidence score

Model says how sure it is (e.g. 96% confidence for High Risk).

#### joblib

Saves trained model to a file so we don't retrain every time.

#### Synthetic data

We generated fake patients using real medical ranges because no public dataset matched our exact columns. **Interview honesty:** "In production I'd retrain on real anonymized lab data."

#### Clinical rules + ML (hybrid)

- ML gives overall risk level
- Rule-based text explains which value is abnormal (e.g. "possible diabetes — glucose 132 mg/dL")

**Why both:** ML generalizes; rules make output explainable.

---

### 4.7 Other tools

#### Git / GitHub

Version control + online code hosting for submission.

#### .env file

Stores settings (database server name, API URL) outside code. Never commit real `.env`.

#### python-dotenv

Loads `.env` into environment variables when backend starts.

#### pytest

Automated tests — run `pytest` to check API without manual clicking.

#### Plotly

Interactive charts (donut, bar) on Dashboard.

#### Docker (mentioned in README)

Tool to package app in a container. We kept local setup without Docker per your choice.

#### ODBC / pyodbc

Bridge between Python and SQL Server on Windows.

---

## 5. Interview Questions & Answers

### Project overview

**Q1: Walk me through your project in 2 minutes.**

**Answer:**  
"I built MIRA, a health prediction application for the assessment. The frontend is Streamlit — users manage patient records and see a dashboard with charts. The backend is FastAPI REST API. When a patient is created or updated, the app sends blood test values to a trained RandomForest model, which predicts Low, Moderate, or High health risk with a confidence score. That result is stored automatically in the Remarks field. Data is persisted in SQL Server using SQLAlchemy. I separated frontend and backend so the API can be tested independently in Swagger and demonstrates proper API integration."

---

**Q2: Why did you use Streamlit instead of React or HTML?**

**Answer:**  
"The role is Python-focused. Streamlit let me build forms, tables, and Plotly charts in pure Python without HTML/CSS, so I focused on validation, API design, and ML quality — which the task weighted heavily. For a larger product team, React might be better; for this scope Streamlit was the right trade-off."

---

**Q3: Why FastAPI instead of Flask?**

**Answer:**  
"FastAPI gives automatic request validation with Pydantic, async support, and interactive API docs at `/docs` without extra setup. That helped me test CRUD before the UI and shows clean API design to reviewers."

---

**Q4: Why two folders — frontend and backend?**

**Answer:**  
"Separation of concerns. The UI only talks HTTP JSON to the API; it never touches the database. That mirrors real systems, makes testing easier, and proves API integration — which was an explicit evaluation point."

---

### Database

**Q5: Which database did you use and why?**

**Answer:**  
"SQL Server on my machine, database HealthDB, table patients. I use Windows Authentication so no passwords are in code. SQLAlchemy ORM maps Python classes to tables. Tests use temporary SQLite so they don't touch real patient data."

---

**Q6: What is an ORM?**

**Answer:**  
"Object-Relational Mapping. I define a `Patient` class in Python; SQLAlchemy translates that to SQL INSERT/SELECT on SQL Server. It reduces SQL injection risk and lets me switch databases by changing connection settings."

---

**Q7: How do you prevent duplicate patients?**

**Answer:**  
"Email is UNIQUE in the database, and the API returns 409 Conflict if someone tries to create a duplicate. Validation happens at both DB and API layers."

---

### API & validation

**Q8: Explain your API endpoints.**

**Answer:**  
"Five REST endpoints under `/api/patients`: GET list, GET by id, POST create, PUT update, DELETE remove. POST and PUT trigger ML prediction and refresh Remarks. DELETE returns 204 with no body."

---

**Q9: What is Pydantic and where did you use it?**

**Answer:**  
"Pydantic defines schemas — Python classes with types and rules. `PatientCreate` requires valid email, DOB not in future, positive numeric blood values. FastAPI returns 422 with field-level errors if validation fails."

---

**Q10: What is the difference between 404, 409, and 422?**

**Answer:**  
"404 — patient ID doesn't exist. 409 — business rule conflict, like duplicate email. 422 — request body failed validation, like invalid email format or future date of birth."

---

### Machine Learning

**Q11: Which ML algorithm did you use and why?**

**Answer:**  
"RandomForest classifier from scikit-learn. It handles non-linear relationships — for example glucose is risky when too high or too low. It doesn't require heavy feature scaling, gives probability scores for confidence, and trains quickly on tabular data."

---

**Q12: What features does your model use?**

**Answer:**  
"Age derived from date of birth, fasting glucose, haemoglobin, and total cholesterol. Four numeric features fed as one row to the model."

---

**Q13: Where did your training data come from?**

**Answer:**  
"I generated synthetic data using published clinical reference ranges for glucose, haemoglobin, and cholesterol. Labels came from rule-based scoring plus small random noise so the model learns patterns rather than memorizing rules. On a test holdout I got about 97.7% accuracy. In production I'd retrain on real anonymized lab data with clinician review."

---

**Q14: How is the Remarks field generated?**

**Answer:**  
"On create/update, `predictor.py` loads the saved model, predicts class and confidence, then rule-based checks add human-readable explanations for each abnormal metric. Example: 'AI Prediction: High Risk (96% confidence) - Possible diabetes (glucose 132 mg/dL).'"

---

**Q15: What is overfitting and how did you reduce it?**

**Answer:**  
"Overfitting is when the model memorizes training data and fails on new patients. I used train/test split with stratification, held out 20% for evaluation, and added label noise in synthetic data. I report per-class precision/recall, not just one accuracy number."

---

**Q16: Why not use an external health API?**

**Answer:**  
"The task allowed custom ML models. A custom model gives full control, no API keys to manage, works offline for demo, and shows I understand training and deployment — not only calling a third-party service."

---

### Architecture & behavior

**Q17: Why doesn't Streamlit connect directly to the database?**

**Answer:**  
"By design. The frontend is a client of the REST API. That enforces a clear contract, enables Swagger/Postman testing, and matches how production apps separate UI and business logic."

---

**Q18: What happens on update when blood values change?**

**Answer:**  
"PUT replaces the record and calls `generate_remarks` again with new values, so Remarks always matches current blood tests."

---

**Q19: How do you handle configuration and secrets?**

**Answer:**  
"Settings via environment variables and `.env` loaded with python-dotenv. `.env` is gitignored. SQL Server uses Windows Authentication locally. README documents SQLite fallback for users without SQL Server."

---

**Q20: How did you test the project?**

**Answer:**  
"Seven pytest tests with FastAPI TestClient: create with remarks, abnormal values flagged, invalid email, future DOB, non-numeric input, duplicate email, full CRUD flow. Tests use a temporary SQLite database. I also manually tested via Swagger and the Streamlit UI."

---

### Behavioral / process

**Q21: What was the hardest part?**

**Answer (example — pick what's true for you):**  
"Keeping frontend and backend in sync after folder restructure, and ensuring Streamlit always fetched fresh data after CRUD. I solved it with sidebar navigation that reruns the script and by not relying on tabs that don't refresh."

---

**Q22: What would you improve next?**

**Answer:**  
"User authentication (JWT), pagination for large lists, sex-specific haemoglobin ranges, retrain on real data, CI pipeline running pytest on every push, and optional cloud deployment with one public URL."

---

**Q23: Is this medical advice?**

**Answer:**  
"No. It's a coding assessment demo using simplified rules and synthetic training data. Not for clinical diagnosis."

---

## 6. Common Beginner Mistakes & How to Avoid Them

| Mistake | Why it's bad | How to avoid |
|---------|--------------|--------------|
| Running `streamlit` from wrong folder | File not found error | Always `cd frontend` first, or use `start_app.bat` |
| Starting only frontend | "Cannot reach backend API" | Start backend (port 8000) before frontend |
| Multiple servers on same port | Random errors, old code | Kill old processes; one backend + one frontend |
| Committing `.env` or passwords | Security risk, task says remove secrets | Use `.gitignore`; only commit `.env.example` |
| Validation only in UI | Bad data can still hit API via Postman | Always validate on server with Pydantic |
| SQL inside route functions | Messy, untestable | Use `crud.py` layer |
| Retraining model on every request | Very slow | Load model once with joblib; cache in memory |
| Assuming app creates SQL database | Connection fails | Create `HealthDB` in SSMS first |
| Wrong SQL Server instance name | Login / connection errors | Match SSMS server name in `.env` |
| Copy-paste AI code without understanding | Task warns disqualification | Read each file; explain in demo video |
| Forgetting to regenerate Remarks on update | Stale AI text after edit | Call predictor in `update_patient` too |
| Using only training accuracy | Misleading metric | Report test set accuracy and per-class metrics |

---

## 7. Demo Video Talking Points

Suggested flow (5–8 minutes):

1. **Intro (30 sec)** — "MIRA Health Prediction: CRUD + ML + SQL Server + REST API."
2. **Architecture (1 min)** — Show diagram: Streamlit → FastAPI → SQL Server.
3. **Home page** — Hero, Get Started, View Dashboard.
4. **Add patient** — Normal values → Low risk remark. Abnormal values → High risk remark.
5. **Dashboard** — KPI cards, search, filter, Plotly charts, CSV export.
6. **Update** — Change glucose, show Remarks change.
7. **Delete** — Remove record, count updates.
8. **SSMS (optional, strong)** — Show same row in `HealthDB.dbo.patients`.
9. **Swagger** — Open `/docs`, show one POST request.
10. **Challenges** — e.g. folder structure, Streamlit refresh, SQL Server connection.
11. **Why this stack** — Python end-to-end, API for integration, SQL Server for persistence.

---

## 8. Quick Cheat Sheet

### Start the app

```powershell
# Easiest
Double-click start_app.bat

# Manual
cd backend → uvicorn app.main:app --reload
cd frontend → streamlit run streamlit_app.py
```

### URLs

| URL | What |
|-----|------|
| http://localhost:8501 | Website |
| http://127.0.0.1:8000/docs | API documentation |
| http://127.0.0.1:8000/api/patients | Patient list (JSON) |

### Key files to know for interview

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI entry, startup |
| `backend/app/schemas.py` | Validation rules |
| `backend/app/crud.py` | Database + calls ML |
| `backend/app/ml/predictor.py` | AI remarks |
| `backend/app/database.py` | SQL Server connection |
| `frontend/streamlit_app.py` | UI + navigation |
| `frontend/ui/home.py` | Home & dashboard components |

### One-line definitions

- **CRUD** — Create, Read, Update, Delete  
- **REST** — Standard URL + HTTP method API style  
- **ORM** — Python classes ↔ database tables  
- **Pydantic** — Data validation library  
- **RandomForest** — Ensemble ML classifier  
- **JSON** — Text format for API data exchange  

---

## Final note for freshers

You don't need to memorize every line of code. For the interview, focus on:

1. **What** the app does (CRUD + AI remarks + database)  
2. **Why** you split frontend and backend  
3. **How** data flows from form → API → ML → database → UI  
4. **One honest limitation** (synthetic data, not real medical advice)  
5. **One improvement** you'd make next  

If you can explain those five things clearly, you will sound prepared — not just someone who submitted copied code.

---

*Document version: 1.0 — aligned with MIRA project structure (frontend/ + backend/).*
