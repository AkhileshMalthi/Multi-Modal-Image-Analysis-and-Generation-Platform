#!/bin/bash
# Start Frontend Server Only

echo "🎨 Starting Frontend Server..."
echo ""

if [ ! -f "frontend/.env.local" ]; then
    echo "⚠️  Info: .env.local not found (optional)"
    echo "   Default backend URL: http://127.0.0.1:8000"
    echo ""
fi

cd frontend || exit 1
echo "📍 Starting Next.js server on http://localhost:3000"
echo ""
npm run dev
