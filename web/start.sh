#!/bin/bash
# Quick start script for Plural Chat Web Edition

echo "🚀 Starting Plural Chat Web Edition..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Ask for environment
echo "Select environment:"
echo "1) Development (with hot reload)"
echo "2) Production"
read -p "Enter choice (1 or 2): " env_choice

case $env_choice in
    1)
        echo "Starting development environment..."
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    2)
        echo "Starting production environment..."
        # Check if .env exists
        if [ ! -f backend/.env ]; then
            echo "⚠️  Backend .env file not found. Creating from example..."
            cp backend/.env.example backend/.env
            echo "📝 Please edit backend/.env with your configuration"
            exit 1
        fi
        docker-compose up --build -d
        echo "✅ Services started!"
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
