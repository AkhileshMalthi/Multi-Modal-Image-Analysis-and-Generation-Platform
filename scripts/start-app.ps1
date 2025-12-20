# Multi-Modal Image Analysis and Generation Platform - Startup Script
# This script starts both backend and frontend servers concurrently

Write-Host "🚀 Starting Multi-Modal Image Analysis Platform..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "   Current directory: $PWD" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Warning: backend\.env file not found!" -ForegroundColor Yellow
    Write-Host "   Please create backend\.env with your API keys before running the app" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

Write-Host "📦 Starting Backend (FastAPI - Port 8000)..." -ForegroundColor Green
Write-Host "📦 Starting Frontend (Next.js - Port 3000)..." -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to cleanup processes on exit
$cleanup = {
    Write-Host "`n`n🛑 Shutting down servers..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "✅ Servers stopped" -ForegroundColor Green
}

# Register cleanup on exit
Register-EngineEvent PowerShell.Exiting -Action $cleanup | Out-Null

try {
    # Start backend in background job
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location backend
        uv run uvicorn app.main:app --reload --port 8000
    }

    # Start frontend in background job
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location frontend
        npm run dev
    }

    # Wait a moment for servers to start
    Start-Sleep -Seconds 3

    Write-Host "✅ Backend started: http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "✅ Frontend started: http://localhost:3000" -ForegroundColor Green
    Write-Host "✅ API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Monitoring logs (Ctrl+C to stop)..." -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan

    # Monitor both jobs and display output
    while ($true) {
        # Check if jobs are still running
        if ($backendJob.State -eq "Failed" -or $frontendJob.State -eq "Failed") {
            Write-Host "`n❌ One or more servers failed to start" -ForegroundColor Red
            
            if ($backendJob.State -eq "Failed") {
                Write-Host "`nBackend Error:" -ForegroundColor Red
                Receive-Job $backendJob
            }
            
            if ($frontendJob.State -eq "Failed") {
                Write-Host "`nFrontend Error:" -ForegroundColor Red
                Receive-Job $frontendJob
            }
            
            break
        }

        # Display output from both jobs
        $backendOutput = Receive-Job $backendJob
        $frontendOutput = Receive-Job $frontendJob

        if ($backendOutput) {
            Write-Host "[Backend] " -ForegroundColor Blue -NoNewline
            Write-Host $backendOutput
        }

        if ($frontendOutput) {
            Write-Host "[Frontend] " -ForegroundColor Magenta -NoNewline
            Write-Host $frontendOutput
        }

        Start-Sleep -Milliseconds 500
    }
}
catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
}
finally {
    # Cleanup
    & $cleanup
}
