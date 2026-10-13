# FedHeal - Start Frontend React App (Windows PowerShell)
$ErrorActionPreference = "Stop"
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies with npm install..." -ForegroundColor Yellow
    npm install
}
Write-Host "Starting Vite development server..." -ForegroundColor Green
npm run dev
