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

set "REPO_ZIP_URL=https://github.com/geekmarrs-alt/techcamai/archive/refs/heads/master.zip"
set "TMP_ROOT=%TEMP%\techcamai_quick_install"
set "ZIP_PATH=%TMP_ROOT%\techcamai-master.zip"
set "EXTRACT_ROOT=%TMP_ROOT%\extract"

echo [1/5] Preparing temporary workspace...
if exist "%TMP_ROOT%" rmdir /s /q "%TMP_ROOT%"
mkdir "%TMP_ROOT%" >nul 2>&1
mkdir "%EXTRACT_ROOT%" >nul 2>&1

echo [2/5] Downloading latest TECHCAMAI...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing -Uri '%REPO_ZIP_URL%' -OutFile '%ZIP_PATH%'" || (
  echo [ERROR] Failed to download %REPO_ZIP_URL%
  pause
  exit /b 1
)

echo [3/5] Extracting package...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%ZIP_PATH%' -DestinationPath '%EXTRACT_ROOT%' -Force" || (
  echo [ERROR] Failed to extract package.
  pause
  exit /b 1
)

set "APP_DIR="
for /d %%D in ("%EXTRACT_ROOT%\techcamai-*") do (
  set "APP_DIR=%%~fD"
)

if not defined APP_DIR (
  echo [ERROR] Could not find extracted TECHCAMAI folder.
  pause
  exit /b 1
)

if not exist "%APP_DIR%\windows_install.bat" (
  echo [ERROR] windows_install.bat not found in extracted package.
  pause
  exit /b 1
)

echo [4/5] Running installer...
pushd "%APP_DIR%"
call windows_install.bat
set "INSTALL_EXIT=%ERRORLEVEL%"
popd

if not "%INSTALL_EXIT%"=="0" (
  echo [ERROR] Installer returned exit code %INSTALL_EXIT%.
  pause
  exit /b %INSTALL_EXIT%
)

echo [5/5] Complete.
echo TECHCAMAI installed successfully.
echo Desktop shortcut: TechCamAI
echo.
pause
