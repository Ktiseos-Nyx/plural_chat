@echo off
REM Quick start script for Plural Chat Web Edition (Windows)

echo 🚀 Starting Plural Chat Web Edition...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Ask for environment
echo Select environment:
echo 1^) Development (with hot reload^)
echo 2^) Production
set /p env_choice="Enter choice (1 or 2): "

if "%env_choice%"=="1" (
    echo Starting development environment...
    docker-compose -f docker-compose.dev.yml up --build
) else if "%env_choice%"=="2" (
    echo Starting production environment...

    REM Check if .env exists
    if not exist backend\.env (
        echo ⚠️  Backend .env file not found. Creating from example...
        copy backend\.env.example backend\.env
        echo 📝 Please edit backend\.env with your configuration
        pause
        exit /b 1
    )

    docker-compose up --build -d
    echo ✅ Services started!
    echo Frontend: http://localhost:3000
    echo Backend: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
    pause
) else (
    echo Invalid choice
    pause
    exit /b 1
)
