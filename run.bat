@echo off
setlocal

echo ============================================
echo   TECHCAMAI - Edge Camera Monitoring MVP
echo ============================================
echo.

:: Check Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ from https://www.python.org/downloads/
    echo         Make sure to tick "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Show Python version
python --version

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate venv and install dependencies
echo.
echo [2/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Create data directory
echo.
echo [3/4] Setting up data directory...
if not exist "data" mkdir data
if not exist "data\clips" mkdir data\clips

:: Start the server
echo.
echo [4/4] Starting TECHCAMAI...
echo.
echo   Dashboard:  http://localhost:8000/
echo   API docs:   http://localhost:8000/docs
echo   Health:     http://localhost:8000/health
echo.
echo   Press Ctrl+C to stop the server.
echo ============================================
echo.

:: Set env vars and launch
set DB_PATH=%~dp0data\techcamai.db
set CLIPS_DIR=%~dp0data\clips

:: Open browser after a short delay
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000/"

:: Run uvicorn from the api directory
cd api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
