param(
    [string]$InstallDir = "$env:USERPROFILE\TechCamAI",
    [string]$RepoZipUrl = "",
    [switch]$SkipLaunch
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[TECHCAMAI] $Message" -ForegroundColor Cyan
}

$desktop = [Environment]::GetFolderPath("Desktop")
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("techcamai-" + [Guid]::NewGuid().ToString("N"))
$zipPath = Join-Path $tempRoot "techcamai.zip"
$extractDir = Join-Path $tempRoot "extract"

if ([string]::IsNullOrWhiteSpace($RepoZipUrl)) {
    throw "RepoZipUrl is required. Use an approved private source archive URL or signed release package; do not use public download links for proprietary builds."
}

Write-Step "Preparing Windows install at $InstallDir"
New-Item -ItemType Directory -Force -Path $tempRoot, $InstallDir | Out-Null

Write-Step "Downloading TECHCAMAI Windows package from approved source"
Invoke-WebRequest -Uri $RepoZipUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

$sourceRoot = Get-ChildItem -Path $extractDir -Directory | Select-Object -First 1
if (-not $sourceRoot) {
    throw "Downloaded package did not contain a source directory."
}

Write-Step "Copying application files"
Copy-Item -Path (Join-Path $sourceRoot.FullName "*") -Destination $InstallDir -Recurse -Force

$launchScript = Join-Path $InstallDir "windows\launch-techcamai.ps1"
if (-not (Test-Path $launchScript)) {
    throw "Launch script was not found at $launchScript"
}

Write-Step "Creating desktop quick launch shortcut"
$shortcutPath = Join-Path $desktop "TECHCAMAI Command Center.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$launchScript`""
$shortcut.WorkingDirectory = $InstallDir
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,220"
$shortcut.Save()

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Warning "Docker Desktop was not found. Install it from https://www.docker.com/products/docker-desktop/ and then use the desktop shortcut."
    Start-Process "https://www.docker.com/products/docker-desktop/"
} elseif (-not $SkipLaunch) {
    Write-Step "Starting TECHCAMAI with Docker Compose"
    Push-Location $InstallDir
    try {
        docker compose up -d --build
    } finally {
        Pop-Location
    }
    Start-Process "http://localhost:8000/"
}

Write-Step "Done. Use the TECHCAMAI Command Center shortcut on your desktop to launch the app."
