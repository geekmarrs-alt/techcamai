@echo off
echo TECHCAMAI - Windows Desktop Installer Path
echo ------------------------------------------

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.12+ from python.org
    pause
    goto :eof
)

echo [1/3] Installing dependencies...
pip install -r api/requirements.txt
pip install -r worker/requirements.txt
pip install pywebview pyinstaller uvicorn

echo [2/3] Building executable...
:: pyinstaller --onefile --windowed --name TechCamAI --add-data "api;api" --add-data "worker;worker" desktop_app.py
echo (In a real Windows environment, this would run PyInstaller to bundle the app)

echo [3/3] Creating Desktop Shortcut...
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\TechCamAI.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%CD%\desktop_app.py" >> %SCRIPT%
echo oLink.WorkingDirectory = "%CD%" >> %SCRIPT%
echo oLink.Description = "Launch TECHCAMAI Operator Console" >> %SCRIPT%
echo oLink.IconLocation = "%CD%\api\app\static\techcamai-icon.jpg" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo ------------------------------------------
echo Done! A shortcut 'TechCamAI' has been created on your desktop.
echo Double-click it to launch the console without using the terminal.
pause
