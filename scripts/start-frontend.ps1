# Start Frontend Server Only
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "frontend\.env.local")) {
    Write-Host "⚠️  Info: .env.local not found (optional)" -ForegroundColor Yellow
    Write-Host "   Default backend URL: http://127.0.0.1:8000" -ForegroundColor Yellow
    Write-Host ""
}

Set-Location frontend
Write-Host "📍 Starting Next.js server on http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
npm run dev
