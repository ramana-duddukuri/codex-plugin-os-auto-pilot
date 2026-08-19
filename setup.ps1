# PowerShell setup script for Windows users
$ErrorActionPreference = "Stop"

# Change directory to plugin root
Set-Location -Path $PSScriptRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Running Oniesoft Auto-Pilot Setup for Windows..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (Get-Command python -ErrorAction SilentlyContinue) {
    python scripts\setup.py @args
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    python3 scripts\setup.py @args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 scripts\setup.py @args
} else {
    Write-Error "Python 3.10+ is required but 'python', 'python3', or 'py' was not found on PATH."
    exit 1
}
