@echo off
setlocal
title YouTube Metadata Studio
cd /d "%~dp0"

echo ===================================================
echo   YouTube Metadata and HD Thumbnail Studio
echo ===================================================

echo [*] Checking for previous running instances...
powershell -NoProfile -Command "$p = (Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue).OwningProcess; if ($p) { Write-Host '[*] Stopping previous instance (PID:' $p ')...'; Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 600 }"

if not exist ".venv\Scripts\python.exe" (
    echo [*] Virtual environment not found. Creating .venv...
    python -m venv .venv
    echo [*] Installing dependencies...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo [*] Starting YouTube Metadata Studio on http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
.venv\Scripts\python.exe app.py

pause
