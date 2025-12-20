#!/bin/bash
# Start Backend Server Only

echo "🔧 Starting Backend Server..."
echo ""

if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Create backend/.env with your API keys:"
    echo "   - GOOGLE_API_KEY"
    echo "   - HUGGINGFACE_TOKEN"
    echo "   - AWS credentials"
    echo ""
fi

cd backend || exit 1
echo "📍 Starting FastAPI server on http://127.0.0.1:8000"
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo ""
uv run uvicorn app.main:app --reload --port 8000
