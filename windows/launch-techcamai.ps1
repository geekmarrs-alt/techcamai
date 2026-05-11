param(
    [string]$AppDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[TECHCAMAI] $Message" -ForegroundColor Cyan
}

$exePath = Join-Path $AppDir "TECHCAMAI.exe"
if (-not (Test-Path $exePath)) {
    throw "TECHCAMAI.exe was not found at $exePath. Run windows\install.ps1 first."
}

Write-Step "Launching TECHCAMAI"
Start-Process $exePath
