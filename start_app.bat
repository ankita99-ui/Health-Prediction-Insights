@echo off
REM Starts the whole MIRA app: backend API + frontend website.
REM Just double-click this file (or run: start_app.bat)

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo ERROR: Virtual environment not found at %ROOT%.venv
    echo Run once:  python -m venv .venv
    echo            .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%ROOT%.env" (
    copy "%ROOT%.env.example" "%ROOT%.env" >nul
    echo Created .env from .env.example
)

REM Stop leftover servers from a previous run (frees ports 8000 and 8501)
powershell -NoProfile -Command "foreach ($p in 8000,8501) { Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } }"

echo Starting backend... (first start can take 15-30 seconds)
start "MIRA Backend - do not close" cmd /k "cd /d %ROOT%backend && %PYTHON% -m uvicorn app.main:app --port 8000"

echo Waiting for backend to be ready...
powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 90;$i++){ try { $r=Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -TimeoutSec 3 -UseBasicParsing; if($r.StatusCode -eq 200){$ok=$true; break} } catch {}; Start-Sleep -Seconds 1 }; if($ok){ Write-Host 'Backend is ready.' } else { Write-Host 'WARNING: Backend did not respond in 90s. Check the Backend window for errors.' }"

echo Starting frontend...
start "MIRA Frontend - do not close" cmd /k "cd /d %ROOT%frontend && %PYTHON% -m streamlit run streamlit_app.py --server.port 8501"

echo.
echo Both servers are starting in separate windows.
echo Website:  http://localhost:8501
echo API docs: http://127.0.0.1:8000/docs
echo.
echo Keep both windows open while using the app.
