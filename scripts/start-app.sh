#!/bin/bash
# Multi-Modal Image Analysis and Generation Platform - Startup Script
# This script starts both backend and frontend servers concurrently

echo "🚀 Starting Multi-Modal Image Analysis Platform..."
echo ""

# Check if we're in the correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file not found!"
    echo "   Please create backend/.env with your API keys before running the app"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Starting Backend (FastAPI - Port 8000)..."
echo "📦 Starting Frontend (Next.js - Port 3000)..."
echo ""
echo "Press Ctrl+C to stop both servers"
echo "============================================"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Register cleanup on exit
trap cleanup SIGINT SIGTERM EXIT

# Start backend
cd backend
uv run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment
sleep 2

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait another moment for servers to start
sleep 3

echo "✅ Backend started: http://127.0.0.1:8000"
echo "✅ Frontend started: http://localhost:3000"
echo "✅ API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "📊 Servers running (Ctrl+C to stop)..."
echo "============================================"

# Wait for both processes
wait
