# MIRA — Health Prediction Application

**MIRA (Medical Intelligence Robotic Automation)** is a full-stack health prediction web app that manages patient blood test records and uses a trained Machine Learning model to automatically predict a patient's health risk level — saved directly into the Remarks field of every record.

Built for the *Junior AI/ML Developer*

## Features

| Feature | Description |
| --- | --- |
| 🗂️ **Patient Management** | Full CRUD — create, view, update and delete patient records, with validation at every step (email format, no future date of birth, numeric blood values — checked in the UI **and** again on the server with Pydantic) |
| 🤖 **AI Prediction Engine** | A trained RandomForest classifier (scikit-learn) predicts Low / Moderate / High health risk from age, glucose, haemoglobin and cholesterol, with a confidence score — written automatically into the Remarks field |
| 📈 **Update History & Trends** | When you **update** an existing patient (same ID), each save adds a snapshot to `patient_history`. The **Update History** page shows Plotly line charts for glucose, haemoglobin and cholesterol, plus risk-level changes (e.g. High → Moderate) over time |
| 📈 **Real-Time Dashboard** | Live KPI cards, search, risk-level filters and Plotly charts that refresh automatically after every change |
| ⬇️ **CSV Export** | Download the complete patient dataset as a CSV file for reports and offline analysis |
| 🧪 **Risk Analysis** | Per-metric explanations show exactly *which* blood values are outside normal clinical ranges, so the prediction is never a black box |
| 🔐 **Secure Database** | Records stored in Microsoft SQL Server (works with SSMS) via SQLAlchemy ORM, using Windows Authentication — no passwords or secrets in the code |

Plus: a **REST API** (FastAPI) with auto-generated Swagger docs at `/docs`,
and a Streamlit frontend with a landing page, dashboard and guided
add/update/delete flows.

## Demo

![MIRA App Preview](https://raw.githubusercontent.com/ankita99-ui/Health-Prediction-Insights/main/mira_preview_small.gif)

## Architecture

![MIRA Architecture](https://github.com/user-attachments/assets/4b5004da-af0d-4f43-905e-3d7bd6b9738f)

## Tech Stack

| Layer | Technology | Why |
|--------|------------|------|
| Frontend | Streamlit | Pure-Python UI, no HTML/CSS/JS needed |
| Backend | FastAPI + Uvicorn | Fast, modern, automatic validation and docs |
| Database | SQL Server (via SQLAlchemy) | Robust relational storage, manageable in SSMS |
| ML | scikit-learn RandomForest | Reliable classifier, easy to train and ship |
| Validation | Pydantic v2 | Declarative request/response validation |

## Project Structure

```text
task1/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── routers/
│   │   │   └── patients.py
│   │   └── ml/
│   │       ├── train_model.py
│   │       └── predictor.py
│   ├── models/
│   ├── database/
│   │   └── create_database.sql
│   └── tests/
│       └── test_api.py
├── frontend/
│   ├── streamlit_app.py
│   ├── ui/
│   │   ├── home.py
│   │   ├── history.py
│   │   └── styles.py
│   └── .streamlit/
│       └── config.toml
├── seed_data.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## Quick Start (Windows)

After the one-time setup below, just **double-click `start_app.bat`** in the project root. It opens the backend and frontend in two windows and launches the application at:

```text
http://localhost:8501
```

## Future Improvements

- User Authentication & Authorization
- Role-Based Access Control
- Model Retraining Dashboard
- PDF Report Generation
- Cloud Deployment
- Advanced Health Analytics
- Real Healthcare Dataset Integration

## Conclusion

MIRA successfully integrates Machine Learning into a full-stack healthcare application. The system provides patient management, automated health risk prediction, and secure SQL Server data storage through a modern FastAPI and Streamlit architecture.

The project demonstrates practical experience in:

- Python Development
- Machine Learning
- FastAPI APIs
- SQL Server Integration
- Streamlit UI Development
- Software Engineering Best Practices

> **Note:** The prediction model is trained on sample healthcare data and is intended for educational and demonstration purposes only. It should not be used for real clinical decision-making.

## References

[1] Géron, A., *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*, 3rd Edition, O'Reilly Media, 2022.

[2] Raschka, S., Liu, Y., and Mirjalili, V., *Machine Learning with PyTorch and Scikit-Learn*, Packt Publishing, 2022.

[3] VanderPlas, J., *Python Data Science Handbook*, O'Reilly Media, 2016.

[4] McKinney, W., *Python for Data Analysis*, 3rd Edition, O'Reilly Media, 2022.

[5] Beaulieu, A., *Learning SQL: Generate, Manipulate, and Retrieve Data*, 3rd Edition, O'Reilly Media, 2020.

[6] Delaney, K., *SQL Server Internals*, Microsoft Press, 2019.

[7] Microsoft Corporation, *SQL Server Documentation*, Microsoft Learn.

[8] The Scikit-Learn Development Team, *Scikit-Learn User Guide and Documentation*.

[9] Streamlit Inc., *Streamlit Documentation and Developer Guide*.

[10] UCI Machine Learning Repository, *Pima Indians Diabetes Dataset*.