# Startup Scripts

This folder contains scripts to easily start the Multi-Modal Image Analysis Platform.

## 📁 Available Scripts

### PowerShell (Windows)
- `start-app-split.ps1` - Opens backend and frontend in separate windows ⭐ **RECOMMENDED**
- `start-app.ps1` - Runs both servers in a single terminal with combined logs
- `start-backend.ps1` - Start backend only
- `start-frontend.ps1` - Start frontend only

### Bash (Linux/Mac)
- `start-app-split.sh` - Opens backend and frontend in separate terminals ⭐ **RECOMMENDED**
- `start-app.sh` - Runs both servers in a single terminal
- `start-backend.sh` - Start backend only
- `start-frontend.sh` - Start frontend only

## 🚀 Quick Start

### Windows (PowerShell)
```powershell
# From project root
.\scripts\start-app-split.ps1
```

### Linux/Mac (Bash)
```bash
# From project root
# Make scripts executable first
chmod +x scripts/*.sh

# Then run
./scripts/start-app-split.sh
```

## 📋 Prerequisites

### Backend Requirements
- Python 3.11+
- `uv` package manager installed
- `.env` file in `backend/` with API keys:
  - `GOOGLE_API_KEY`
  - `HUGGINGFACE_TOKEN`
  - AWS credentials

### Frontend Requirements
- Node.js 18+
- Dependencies installed (`npm install`)
- Optional: `.env.local` in `frontend/`

## 🛠️ Script Details

### Split Terminal Scripts (Recommended)
Opens servers in separate terminal windows for easy monitoring and debugging.

**Windows:**
```powershell
.\scripts\start-app-split.ps1
```

**Linux/Mac:**
```bash
./scripts/start-app-split.sh
```

**Features:**
- ✅ Separate windows for each server
- ✅ Easy to see individual logs
- ✅ Can stop/restart servers independently
- ✅ Better for development and debugging

### Combined Scripts
Runs both servers in a single terminal with combined output.

**Windows:**
```powershell
.\scripts\start-app.ps1
```

**Linux/Mac:**
```bash
./scripts/start-app.sh
```

**Features:**
- ✅ Single terminal window
- ✅ Color-coded logs
- ✅ Automatic cleanup on exit
- ✅ Cleaner workspace

### Individual Server Scripts

**Backend only:**
```powershell
# Windows
.\scripts\start-backend.ps1

# Linux/Mac
./scripts/start-backend.sh
```

**Frontend only:**
```powershell
# Windows
.\scripts\start-frontend.ps1

# Linux/Mac
./scripts/start-frontend.sh
```

## 🎯 Access Points

Once the servers are running:

- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000
- **API Documentation:** http://127.0.0.1:8000/docs

## 🐛 Troubleshooting

### Windows PowerShell Execution Policy
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/Mac Permissions
Make scripts executable:
```bash
chmod +x scripts/*.sh
```

### Backend Won't Start
- Check `.env` file exists in `backend/`
- Verify all API keys are present
- Ensure virtual environment exists
- Try: `cd backend && uv sync`

### Frontend Won't Start
- Install dependencies: `cd frontend && npm install`
- Check Node.js version: `node --version` (should be 18+)
- Clear cache: `rm -rf .next node_modules && npm install`

### Port Already in Use
If ports 8000 or 3000 are already in use:
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac - Find and kill process
lsof -ti:8000 | xargs kill -9
```

## 💡 Tips

1. **First time setup:** Use `start-app-simple` scripts to see logs clearly
2. **Regular development:** Choose whichever script style you prefer
3. **Debugging:** Individual scripts let you restart one server at a time
4. **Production:** Don't use these scripts - use proper deployment methods

## 📝 Customization

To modify script behavior:
1. Edit the script files in this directory
2. Adjust ports, commands, or terminal preferences
3. Add custom environment checks or validations

## 🔗 Related Documentation

- [Main README](../README.md) - Full project documentation
- [S3 CORS Setup](../S3_CORS_SETUP.md) - Image download configuration
- [Backend README](../backend/README.md) - Backend-specific docs
- [Frontend README](../frontend/README.md) - Frontend-specific docs
