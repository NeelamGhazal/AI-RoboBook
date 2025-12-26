# Backend Testing Script
# Run this AFTER the server is started (in a separate PowerShell window)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"
$testsPassed = 0
$testsFailed = 0

# Test 1: Health Check
Write-Host "[Test 1/4] Health Check Endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -TimeoutSec 5
    if ($response.status -eq "healthy") {
        Write-Host "  ✓ PASS: Server is healthy" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ FAIL: Unexpected response" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ FAIL: Cannot connect to server. Is it running?" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}

Write-Host ""

# Test 2: Simple Query - What is ROS 2?
Write-Host "[Test 2/4] RAG Query - 'What is ROS 2?'" -ForegroundColor Yellow
try {
    $body = @{
        session_id = "test-ps-1"
        question = "What is ROS 2?"
    } | ConvertTo-Json

    $response = Invoke-WebRequest `
        -Uri "$baseUrl/api/v1/chat/api/v1/chat/stream" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 15

    $content = $response.Content

    # Check if response contains expected elements
    if ($content -like "*token*" -and $content -like "*citations*" -and $content -like "*metadata*") {
        # Extract token content
        if ($content -match '"type": "token", "content": "([^"]+)"') {
            $tokenContent = $matches[1]
            Write-Host "  ✓ PASS: Received response" -ForegroundColor Green
            Write-Host "  Preview: $($tokenContent.Substring(0, [Math]::Min(80, $tokenContent.Length)))..." -ForegroundColor Gray
            $testsPassed++
        } else {
            Write-Host "  ✗ FAIL: No token content found" -ForegroundColor Red
            $testsFailed++
        }
    } else {
        Write-Host "  ✗ FAIL: Response missing expected fields" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ FAIL: Query failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}

Write-Host ""

# Test 3: Physics Simulation Query
Write-Host "[Test 3/4] RAG Query - 'Explain physics simulation'" -ForegroundColor Yellow
try {
    $body = @{
        session_id = "test-ps-2"
        question = "Explain physics simulation"
    } | ConvertTo-Json

    $response = Invoke-WebRequest `
        -Uri "$baseUrl/api/v1/chat/api/v1/chat/stream" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 15

    $content = $response.Content

    if ($content -like "*token*" -and $content -like "*citations*") {
        if ($content -match '"token_count": (\d+)') {
            $tokenCount = $matches[1]
            if ([int]$tokenCount -gt 0) {
                Write-Host "  ✓ PASS: Received response with $tokenCount tokens" -ForegroundColor Green
                $testsPassed++
            } else {
                Write-Host "  ✗ FAIL: Empty response (token_count: 0)" -ForegroundColor Red
                $testsFailed++
            }
        } else {
            Write-Host "  ✗ FAIL: No token count in metadata" -ForegroundColor Red
            $testsFailed++
        }
    } else {
        Write-Host "  ✗ FAIL: Response missing expected fields" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ FAIL: Query failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}

Write-Host ""

# Test 4: Response Time Check
Write-Host "[Test 4/4] Performance - Response Time" -ForegroundColor Yellow
try {
    $body = @{
        session_id = "test-ps-3"
        question = "What are ROS 2 nodes?"
    } | ConvertTo-Json

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    $response = Invoke-WebRequest `
        -Uri "$baseUrl/api/v1/chat/api/v1/chat/stream" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 20

    $stopwatch.Stop()
    $elapsed = $stopwatch.ElapsedMilliseconds

    if ($elapsed -lt 10000) {
        Write-Host "  ✓ PASS: Response time: $elapsed ms (< 10s)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ⚠ WARN: Response time: $elapsed ms (slow)" -ForegroundColor Yellow
        $testsPassed++
    }
} catch {
    Write-Host "  ✗ FAIL: Query timed out or failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Results" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Passed: $testsPassed / 4" -ForegroundColor $(if ($testsPassed -eq 4) { "Green" } else { "Yellow" })
Write-Host "  Failed: $testsFailed / 4" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "🎉 All tests passed! Backend is ready for demo." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check server logs for details." -ForegroundColor Yellow
}

Write-Host ""
