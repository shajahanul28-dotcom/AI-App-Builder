$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "Installing NOVAIX AI App Builder..." -ForegroundColor Cyan
python -m pip install --upgrade --force-reinstall .
Write-Host "NOVAIX installation completed." -ForegroundColor Green
Write-Host "Double-click START_NOVAIX.bat for laptop use."
Write-Host "Double-click START_NOVAIX_PHONE.bat for phone access on the same Wi-Fi."
