# Debug Script - Find and Fix Route Issues
# Run this to verify routes are correctly registered

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Route Debugging Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill all Python processes
Write-Host "[1/6] Killing all Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "  ✓ All Python processes terminated" -ForegroundColor Green
Write-Host ""

# Step 2: Verify code changes
Write-Host "[2/6] Verifying code changes..." -ForegroundColor Yellow
$chatRouter = Get-Content "app\api\v1\chat.py" | Select-String "router = APIRouter"
if ($chatRouter -match 'tags=\["chat"\]') {
    Write-Host "  ✓ chat.py: Router has NO prefix (correct)" -ForegroundColor Green
} else {
    Write-Host "  ✗ chat.py: Router still has prefix!" -ForegroundColor Red
    Write-Host "  Line: $chatRouter" -ForegroundColor Gray
}

$mainRouter = Get-Content "app\main.py" | Select-String "include_router\(chat.router"
if ($mainRouter -match 'prefix="/api/v1/chat"') {
    Write-Host "  ✓ main.py: Router included with /api/v1/chat prefix (correct)" -ForegroundColor Green
} else {
    Write-Host "  ✗ main.py: Router prefix missing or wrong!" -ForegroundColor Red
    Write-Host "  Line: $mainRouter" -ForegroundColor Gray
}
Write-Host ""

# Step 3: Check if port 8000 is free
Write-Host "[3/6] Checking if port 8000 is available..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr ":8000"
if ($portCheck) {
    Write-Host "  ⚠ Warning: Port 8000 is still in use" -ForegroundColor Yellow
    Write-Host "  $portCheck" -ForegroundColor Gray
} else {
    Write-Host "  ✓ Port 8000 is available" -ForegroundColor Green
}
Write-Host ""

# Step 4: Start server in background
Write-Host "[4/6] Starting backend server..." -ForegroundColor Yellow
Write-Host "  This will take 10-15 seconds..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 15
Write-Host "  ✓ Server should be running" -ForegroundColor Green
Write-Host ""

# Step 5: Test health endpoint
Write-Host "[5/6] Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "  ✓ Main health endpoint: OK" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Main health endpoint: FAILED" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# Step 6: Test chat endpoints
Write-Host "[6/6] Testing chat endpoints..." -ForegroundColor Yellow

# Test chat health
try {
    $chatHealth = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/chat/health" -Method Get -TimeoutSec 5
    Write-Host "  ✓ /api/v1/chat/health: 200 OK" -ForegroundColor Green
    Write-Host "    Endpoints: $($chatHealth.endpoints | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ /api/v1/chat/health: FAILED" -ForegroundColor Red
    Write-Host "    Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Gray
}

# Test stream endpoint
Write-Host ""
Write-Host "  Testing /api/v1/chat/stream..." -ForegroundColor Cyan
try {
    $body = @{
        session_id = "debug-test"
        question = "test"
    } | ConvertTo-Json

    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/chat/stream" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 15

    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ /api/v1/chat/stream: 200 OK (WORKING!)" -ForegroundColor Green
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  ✗ /api/v1/chat/stream: $statusCode" -ForegroundColor Red

    if ($statusCode -eq 404) {
        Write-Host "    ERROR: Endpoint not found (404)" -ForegroundColor Red
        Write-Host "    This means the route is NOT registered correctly" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Debugging Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Check the new PowerShell window that opened (minimized)" -ForegroundColor Gray
Write-Host "2. Look for the route registration logs:" -ForegroundColor Gray
Write-Host "   [Backend] POST /api/v1/chat/stream" -ForegroundColor Gray
Write-Host "3. If routes look wrong, manually check main.py and chat.py" -ForegroundColor Gray
Write-Host ""
