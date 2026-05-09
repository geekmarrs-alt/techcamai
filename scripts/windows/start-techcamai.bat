@echo off
setlocal

set SCRIPT_DIR=%~dp0
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-techcamai.ps1" %*

if errorlevel 1 (
  echo Failed to start TECHCAMAI.
  exit /b 1
)

echo TECHCAMAI start command completed.
