@echo off
setlocal enabledelayedexpansion

title TECHCAMAI Quick Install
echo TECHCAMAI Quick Install
echo =======================
echo.

where powershell >nul 2>&1
if %errorlevel% neq 0 (
  echo [ERROR] PowerShell is required but was not found.
  pause
  exit /b 1
)

set "EXE_URL=https://github.com/geekmarrs-alt/techcamai/releases/latest/download/TECHCAMAI.exe"
set "INSTALL_DIR=%USERPROFILE%\TechCamAI"
set "EXE_PATH=%INSTALL_DIR%\TECHCAMAI.exe"
set "TMP_ROOT=%TEMP%\techcamai_quick_install"

echo [1/4] Preparing Windows app folder...
if exist "%TMP_ROOT%" rmdir /s /q "%TMP_ROOT%"
mkdir "%TMP_ROOT%" >nul 2>&1
mkdir "%INSTALL_DIR%" >nul 2>&1

echo [2/4] Downloading latest TECHCAMAI.exe...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing -Uri '%EXE_URL%' -OutFile '%EXE_PATH%'" || (
  echo [ERROR] Failed to download %EXE_URL%
  pause
  exit /b 1
)

echo [3/4] Creating desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\TechCamAI.lnk'); $s.TargetPath='%EXE_PATH%'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.IconLocation='%EXE_PATH%'; $s.Save()" || (
  echo [ERROR] Failed to create desktop shortcut.
  pause
  exit /b 1
)

echo [4/4] Launching TECHCAMAI...
start "" "%EXE_PATH%"
echo.
echo TECHCAMAI installed successfully:
echo %EXE_PATH%
echo Desktop shortcut: TechCamAI
echo.
pause
