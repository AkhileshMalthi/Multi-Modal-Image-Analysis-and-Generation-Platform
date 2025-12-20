#!/bin/bash
# Split Terminal Startup Script - Opens Two Separate Terminal Windows (Linux/Mac)

echo "🚀 Starting Multi-Modal Image Analysis Platform..."
echo ""

# Check if we're in the correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file not found!"
    echo "   Please create backend/.env with your API keys"
    echo ""
fi

PROJECT_ROOT=$(pwd)

echo "📦 Starting Backend Server (Port 8000)..."

# Detect the terminal emulator and OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e "tell app \"Terminal\" to do script \"cd '$PROJECT_ROOT/backend' && echo '🔧 Backend Server Starting...' && uv run uvicorn app.main:app --reload --port 8000\""
    sleep 2
    echo "📦 Starting Frontend Server (Port 3000)..."
    osascript -e "tell app \"Terminal\" to do script \"cd '$PROJECT_ROOT/frontend' && echo '🎨 Frontend Server Starting...' && npm run dev\""
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - try common terminal emulators
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT/backend' && echo '🔧 Backend Server Starting...' && uv run uvicorn app.main:app --reload --port 8000; exec bash"
        sleep 2
        gnome-terminal -- bash -c "cd '$PROJECT_ROOT/frontend' && echo '🎨 Frontend Server Starting...' && npm run dev; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$PROJECT_ROOT/backend' && echo '🔧 Backend Server Starting...' && uv run uvicorn app.main:app --reload --port 8000; bash" &
        sleep 2
        xterm -e "cd '$PROJECT_ROOT/frontend' && echo '🎨 Frontend Server Starting...' && npm run dev; bash" &
    elif command -v konsole &> /dev/null; then
        konsole -e "bash -c \"cd '$PROJECT_ROOT/backend' && echo '🔧 Backend Server Starting...' && uv run uvicorn app.main:app --reload --port 8000; bash\"" &
        sleep 2
        konsole -e "bash -c \"cd '$PROJECT_ROOT/frontend' && echo '🎨 Frontend Server Starting...' && npm run dev; bash\"" &
    else
        echo "⚠️  Could not detect terminal emulator. Using single terminal mode..."
        bash "$PROJECT_ROOT/scripts/start-app.sh"
        exit 0
    fi
else
    echo "⚠️  Unsupported OS. Using single terminal mode..."
    bash "$PROJECT_ROOT/scripts/start-app.sh"
    exit 0
fi

echo ""
echo "✅ Both servers are starting in separate windows!"
echo ""
echo "📍 Access the application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://127.0.0.1:8000"
echo "   API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "💡 To stop the servers, close the terminal windows or press Ctrl+C in each"
echo ""
