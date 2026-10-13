# FedHeal - Start Backend Services (Windows PowerShell)
$ErrorActionPreference = "Stop"
Write-Host "Starting FedHeal Backend Services..." -ForegroundColor Cyan
python backend/run_all.py
