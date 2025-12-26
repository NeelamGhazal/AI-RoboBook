# Quick Start Script for Windows
# Run this from E:\phyai-humanoid-textbook\backend\rag-chatbot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RAG Chatbot Backend - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Step 2: Activate virtual environment (if exists)
Write-Host ""
Write-Host "[2/5] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "  ✓ Activating virtual environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "  ! No virtual environment found (optional)" -ForegroundColor Yellow
}

# Step 3: Install dependencies
Write-Host ""
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take 2-5 minutes on first run..." -ForegroundColor Gray
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ All dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Verify key packages
Write-Host ""
Write-Host "[4/5] Verifying installation..." -ForegroundColor Yellow
python -c "import openai; import litellm; from agents import Agent; print('  ✓ OpenAI, LiteLLM, and Agents SDK ready')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Package verification failed" -ForegroundColor Red
    exit 1
}

# Step 5: Kill old processes
Write-Host ""
Write-Host "[5/5] Cleaning up old processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Ready to start server" -ForegroundColor Green

# Start server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Backend Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will start on: http://localhost:8000" -ForegroundColor Green
Write-Host "Wait for 'Application startup complete' message (~10-15 seconds)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
