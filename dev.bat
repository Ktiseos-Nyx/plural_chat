@echo off
REM Plural Chat Development Startup Script (Windows)
REM This script starts both the backend and frontend servers

echo.
echo Starting Plural Chat Development Environment...
echo.

REM Check if we're in the right directory
if not exist "web\backend" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

if not exist "web\frontend" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

REM Check if backend dependencies are installed
if not exist "web\backend\venv" (
    echo Installing backend dependencies...
    cd web\backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..\..
)

REM Check if frontend dependencies are installed
if not exist "web\frontend\node_modules" (
    echo Installing frontend dependencies...
    cd web\frontend
    call npm install
    cd ..\..
)

REM Start backend server
echo Starting Backend (FastAPI) on http://localhost:8000...
cd web\backend
start "Plural Chat Backend" cmd /k "venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
cd ..\..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo Starting Frontend (Next.js) on http://localhost:3000...
cd web\frontend
start "Plural Chat Frontend" cmd /k "npm run dev"
cd ..\..

echo.
echo Development servers started!
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the servers
echo.
pause
