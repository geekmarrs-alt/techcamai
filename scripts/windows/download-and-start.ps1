param(
    [string]$RepoZipUrl = "https://github.com/geekmarrs-alt/techcamai/archive/refs/heads/master.zip",
    [string]$DestinationRoot = "$env:USERPROFILE\Downloads\techcamai",
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

function Assert-Tool($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required tool '$Name' not found. Install it and try again."
    }
}

Assert-Tool "docker"

New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null

$zipPath = Join-Path $DestinationRoot "techcamai-master.zip"
$extractPath = Join-Path $DestinationRoot "techcamai-master"

Write-Host "[1/4] Downloading source ZIP..."
Invoke-WebRequest -Uri $RepoZipUrl -OutFile $zipPath

Write-Host "[2/4] Extracting archive..."
if (Test-Path $extractPath) {
    Remove-Item -Recurse -Force $extractPath
}
Expand-Archive -Path $zipPath -DestinationPath $DestinationRoot -Force

$projectRoot = Get-ChildItem -Path $DestinationRoot -Directory | Where-Object { $_.Name -like "techcamai-*" } | Select-Object -First 1
if (-not $projectRoot) {
    throw "Could not locate extracted project folder in $DestinationRoot."
}

Set-Location $projectRoot.FullName

Write-Host "[3/4] Preparing environment..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

Write-Host "[4/4] Starting Docker stack..."
if ($NoBuild) {
    docker compose up -d
}
else {
    docker compose up --build -d
}

Write-Host ""
Write-Host "TECHCAMAI is starting from: $($projectRoot.FullName)"
Write-Host "Dashboard: http://localhost:8000/"
Write-Host "API docs : http://localhost:8000/docs"
