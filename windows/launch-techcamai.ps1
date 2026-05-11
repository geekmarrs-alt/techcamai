param(
    [string]$AppDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[TECHCAMAI] $Message" -ForegroundColor Cyan
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Warning "Docker Desktop is required before TECHCAMAI can start."
    Start-Process "https://www.docker.com/products/docker-desktop/"
    exit 1
}

Write-Step "Starting local command center"
Push-Location $AppDir
try {
    docker compose up -d
} finally {
    Pop-Location
}

Start-Process "http://localhost:8000/"
Write-Step "TECHCAMAI is opening at http://localhost:8000/"
