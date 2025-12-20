# Split Terminal Startup Script - Opens Two Separate Terminal Windows
# This is easier to use and allows you to see each server's output clearly

Write-Host "🚀 Starting Multi-Modal Image Analysis Platform..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Warning: backend\.env file not found!" -ForegroundColor Yellow
    Write-Host "   Please create backend\.env with your API keys" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "📦 Starting Backend Server (Port 8000)..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '🔧 Backend Server Starting...' -ForegroundColor Green; uv run uvicorn app.main:app --reload --port 8000"

Write-Host "📦 Starting Frontend Server (Port 3000)..." -ForegroundColor Green
Start-Sleep -Seconds 2
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '🎨 Frontend Server Starting...' -ForegroundColor Cyan; npm run dev"

Write-Host ""
Write-Host "✅ Both servers are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access the application at:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 To stop the servers, close the terminal windows or press Ctrl+C in each" -ForegroundColor Yellow
Write-Host ""
