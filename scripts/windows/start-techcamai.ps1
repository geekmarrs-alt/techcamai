param(
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

function Assert-Tool($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required tool '$Name' not found. Install it and try again."
    }
}

Assert-Tool "docker"

$projectRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $projectRoot

if (-not (Test-Path ".env")) {
    if (-not (Test-Path ".env.example")) {
        throw ".env.example not found in project root."
    }
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Created .env from .env.example"
}

if ($NoBuild) {
    docker compose up -d
}
else {
    docker compose up --build -d
}

Write-Host ""
Write-Host "TECHCAMAI is starting."
Write-Host "Dashboard: http://localhost:8000/"
Write-Host "API docs : http://localhost:8000/docs"
