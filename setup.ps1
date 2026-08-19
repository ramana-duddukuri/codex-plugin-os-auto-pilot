# PowerShell setup script for Windows users
$ErrorActionPreference = "Stop"

# Change directory to plugin root
Set-Location -Path $PSScriptRoot

if (Get-Command python -ErrorAction SilentlyContinue) {
    python scripts\setup.py @args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 scripts\setup.py @args
} else {
    Write-Error "Python 3.10+ is required but neither 'python' nor 'py' was found on PATH."
}
