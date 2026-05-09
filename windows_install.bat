@echo off
setlocal enabledelayedexpansion

echo TECHCAMAI - Windows Desktop Installer (v2)
echo ------------------------------------------

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.12 or newer from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b
)

:: 2. Check for FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] FFmpeg was not found in your PATH.
    echo Detection and clip recording require FFmpeg.
    echo.
    echo To install it automatically, open a new Terminal (as Admin) and run:
    echo   winget install ffmpeg
    echo.
    echo Alternatively, download it from https://ffmpeg.org/download.html
    pause
    exit /b
)

:: 3. Install Dependencies
echo [1/3] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r api/requirements.txt
python -m pip install -r worker/requirements.txt
python -m pip install pywebview uvicorn

:: 4. Create Desktop Shortcut (Ghost Mode)
echo [2/3] Creating Quick Launch Desktop Shortcut...

set "TARGET_PATH=%CD%\desktop_app.py"
set "ICON_PATH=%CD%\api\app\static\techcamai-icon.jpg"
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"

:: We use pythonw.exe to launch without a console window
for /f "delims=" %%i in ('where pythonw.exe') do set "PYTHONW_PATH=%%i"

if not defined PYTHONW_PATH (
    set "PYTHONW_PATH=pythonw.exe"
)

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%USERPROFILE%\Desktop\TechCamAI.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%PYTHONW_PATH%" >> "%VBS_SCRIPT%"
echo oLink.Arguments = "!TARGET_PATH!" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%CD%" >> "%VBS_SCRIPT%"
echo oLink.Description = "TECHCAMAI AI CCTV Console" >> "%VBS_SCRIPT%"
echo oLink.IconLocation = "%ICON_PATH%" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo [3/3] Initializing database...
:: Quick run to ensure DB exists
python -c "import os; os.environ['DB_PATH']='techcamai.db'; from api.app.main import engine; from sqlmodel import SQLModel; SQLModel.metadata.create_all(engine)"

echo ------------------------------------------
echo SUCCESS: TECHCAMAI is ready.
echo.
echo Use the 'TechCamAI' shortcut on your Desktop to launch.
echo The app will run in 'Ghost' mode (no terminal windows).
echo.
pause
