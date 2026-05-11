param(
    [string]$InstallDir = "$env:USERPROFILE\TechCamAI",
    [string]$ExeUrl = "https://github.com/geekmarrs-alt/techcamai/releases/latest/download/TECHCAMAI.exe",
    [switch]$SkipLaunch
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[TECHCAMAI] $Message" -ForegroundColor Cyan
}

$desktop = [Environment]::GetFolderPath("Desktop")
$exePath = Join-Path $InstallDir "TECHCAMAI.exe"

Write-Step "Preparing Windows install at $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

Write-Step "Downloading TECHCAMAI.exe"
Invoke-WebRequest -UseBasicParsing -Uri $ExeUrl -OutFile $exePath

Write-Step "Creating desktop quick launch shortcut"
$shortcutPath = Join-Path $desktop "TechCamAI.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = $InstallDir
$shortcut.IconLocation = $exePath
$shortcut.Save()

if (-not $SkipLaunch) {
    Write-Step "Launching TECHCAMAI"
    Start-Process $exePath
}

Write-Step "Done. Use the TechCamAI shortcut on your desktop to launch the app."
