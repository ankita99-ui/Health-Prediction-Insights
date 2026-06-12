@echo off
REM Starts the whole MIRA app: backend API + frontend website.
REM Just double-click this file (or run: start_app.bat)

REM Window 1: FastAPI backend (port 8000)
start "MIRA Backend - do not close" cmd /k "cd /d %~dp0backend && %~dp0.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

REM Give the backend a moment to start before the frontend connects to it
timeout /t 5 /nobreak >nul

REM Window 2: Streamlit frontend (port 8501) - opens the browser automatically
start "MIRA Frontend - do not close" cmd /k "cd /d %~dp0frontend && %~dp0.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8501"

echo Both servers are starting in separate windows.
echo Website:  http://localhost:8501
echo API docs: http://127.0.0.1:8000/docs
