# FedHeal - Start ML / Federated Learning (Windows PowerShell)
param (
    [string]$Mode = "server"
)
Write-Host "Starting FedHeal ML ($Mode)..." -ForegroundColor Magenta
python ml/run_federated.py $Mode
