@echo off
REM Quick Start Script for Windows (Command Prompt)
REM Run this from E:\phyai-humanoid-textbook\backend\rag-chatbot

echo ========================================
echo   RAG Chatbot Backend - Quick Start
echo ========================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   X Python not found! Please install Python 3.11+
    pause
    exit /b 1
)
echo   √ Python found

REM Step 2: Activate virtual environment (if exists)
echo.
echo [2/5] Checking virtual environment...
if exist ".\venv\Scripts\activate.bat" (
    echo   √ Activating virtual environment...
    call .\venv\Scripts\activate.bat
) else (
    echo   ! No virtual environment found (optional)
)

REM Step 3: Install dependencies
echo.
echo [3/5] Installing dependencies...
echo   This may take 2-5 minutes on first run...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo   X Failed to install dependencies
    pause
    exit /b 1
)
echo   √ All dependencies installed

REM Step 4: Verify key packages
echo.
echo [4/5] Verifying installation...
python -c "import openai; import litellm; from agents import Agent; print('  √ OpenAI, LiteLLM, and Agents SDK ready')"
if %errorlevel% neq 0 (
    echo   X Package verification failed
    pause
    exit /b 1
)

REM Step 5: Kill old processes
echo.
echo [5/5] Cleaning up old processes...
taskkill /F /IM python.exe /T >nul 2>&1
echo   √ Ready to start server

REM Start server
echo.
echo ========================================
echo   Starting Backend Server...
echo ========================================
echo.
echo Server will start on: http://localhost:8000
echo Wait for 'Application startup complete' message (~10-15 seconds)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
