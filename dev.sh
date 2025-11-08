#!/bin/bash

# Plural Chat Development Startup Script
# This script starts both the backend and frontend servers

set -e

echo "🚀 Starting Plural Chat Development Environment..."
echo ""

# Check if we're in the right directory
if [ ! -d "web/backend" ] || [ ! -d "web/frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."

    # Kill backend process and its children
    if [ ! -z "$BACKEND_PID" ]; then
        pkill -P $BACKEND_PID 2>/dev/null || true
        kill $BACKEND_PID 2>/dev/null || true
    fi

    # Kill frontend process and its children
    if [ ! -z "$FRONTEND_PID" ]; then
        pkill -P $FRONTEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    # Kill any remaining uvicorn/node processes on these ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true

    echo "✅ All servers stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if backend dependencies are installed
if [ ! -d "web/backend/venv" ] && [ ! -f "web/backend/.venv/bin/activate" ]; then
    echo "📦 Installing backend dependencies..."
    cd web/backend
    python3 -m venv venv || python -m venv venv
    source venv/bin/activate || . venv/Scripts/activate
    pip install -r requirements.txt
    cd ../..
fi

# Check if frontend dependencies are installed
if [ ! -d "web/frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd web/frontend
    npm install
    cd ../..
fi

# Start backend server
echo "🔧 Starting Backend (FastAPI) on http://localhost:8000..."
cd web/backend
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    . venv/Scripts/activate
fi
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../..

# Wait a moment for backend to start
sleep 2

# Start frontend server
echo "⚛️  Starting Frontend (Next.js) on http://localhost:3000..."
cd web/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo "✅ Development servers started!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for background processes
wait
