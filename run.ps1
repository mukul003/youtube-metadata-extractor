# Launch YouTube Metadata & HD Thumbnail Studio (Stop & Start)
Set-Location -Path $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Red
Write-Host "  YouTube Metadata & HD Thumbnail Studio" -ForegroundColor White
Write-Host "===================================================" -ForegroundColor Red

Write-Host "[*] Checking for previous running instances..." -ForegroundColor Yellow

# Find and stop any process listening on port 5000
$conn = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    foreach ($c in $conn) {
        $pidToKill = $c.OwningProcess
        Write-Host "[*] Stopping previous instance on port 5000 (PID: $pidToKill)..." -ForegroundColor Yellow
        Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Milliseconds 800
}

# Verify virtual environment
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[*] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
    & .venv\Scripts\python.exe -m pip install -r requirements.txt
}

Write-Host "[*] Starting server on http://localhost:5000 ..." -ForegroundColor Green
Start-Process "http://localhost:5000"
& .venv\Scripts\python.exe app.py
