# ===============================================================
# DUKAANDOST AI - ONE-CLICK APPLICATION LAUNCHER
# Autonomous AI Growth Manager for Small Retail Businesses
# Store: Sharma General Store, Ranchi, Jharkhand
# ===============================================================

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "   DUKAANDOST AI - AUTONOMOUS KIRANA GROWTH MANAGER" -ForegroundColor Cyan
Write-Host "   'Your AI Business Partner That Doesn't Just Advise. It Takes Action.'" -ForegroundColor White
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

$env:PYTHONPATH = "backend"
$env:PYTHONIOENCODING = "utf-8"

# 1. Start Backend in a background process
Write-Host "[1/3] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendJob = Start-Process python -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory "backend" -PassThru

Start-Sleep -Seconds 3

# 2. Start Frontend
Write-Host "[2/3] Starting React + Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
Write-Host ""
Write-Host ">>> DukaanDost AI is live! Press Ctrl+C in this terminal to stop. <<<" -ForegroundColor Green
Write-Host ""

# Open default browser
Start-Process "http://localhost:5173"

# Run Vite dev server in foreground
Set-Location frontend
npm.cmd run dev -- --host
