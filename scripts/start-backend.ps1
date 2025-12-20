# Start Backend Server Only
Write-Host "🔧 Starting Backend Server..." -ForegroundColor Green
Write-Host ""

if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "   Create backend\.env with your API keys:" -ForegroundColor Yellow
    Write-Host "   - GOOGLE_API_KEY" -ForegroundColor Yellow
    Write-Host "   - HUGGINGFACE_TOKEN" -ForegroundColor Yellow
    Write-Host "   - AWS credentials" -ForegroundColor Yellow
    Write-Host ""
}

Set-Location backend
Write-Host "📍 Starting FastAPI server on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
uv run uvicorn app.main:app --reload --port 8000
