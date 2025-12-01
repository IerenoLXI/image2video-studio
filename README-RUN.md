# 🚀 How to Run the Project

## Quick Start (Easiest Method)

### Option 1: Double-Click Method (Windows)
1. **Double-click `start-project.bat`**
   - This will open two PowerShell windows
   - One for backend, one for frontend
   - Both servers will start automatically

### Option 2: PowerShell Script
1. **Right-click `start-project.ps1`** → **Run with PowerShell**
   - Or open PowerShell and run: `.\start-project.ps1`

## Manual Start (Step by Step)

### Backend Setup
1. Open PowerShell in the project root
2. Navigate to backend:
   ```powershell
   cd backend
   ```
3. Activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Start server:
   ```powershell
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup (New Terminal)
1. Open a new PowerShell window
2. Navigate to frontend:
   ```powershell
   cd frontend
   ```
3. Install dependencies (first time only):
   ```powershell
   npm install
   ```
4. Start dev server:
   ```powershell
   npm run dev
   ```

## Individual Server Scripts

### Start Backend Only
- Double-click: `start-backend.ps1`
- Or run: `powershell -File start-backend.ps1`

### Start Frontend Only
- Double-click: `start-frontend.ps1`
- Or run: `powershell -File start-frontend.ps1`

## Access Points

Once running:
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Troubleshooting

### PowerShell Execution Policy Error
If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
- Backend (8000): Change port in `start-backend.ps1` or use: `uvicorn main:app --reload --port 8001`
- Frontend (3000): Change in `vite.config.js` or use: `npm run dev -- --port 3001`

### Virtual Environment Not Found
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Node Modules Not Found
```powershell
cd frontend
npm install
```

## Project Structure

```
a2e-image2video/
├── start-project.bat      ← Double-click to start everything
├── start-project.ps1      ← PowerShell script (all-in-one)
├── start-backend.ps1      ← Backend only
├── start-frontend.ps1    ← Frontend only
├── backend/               ← FastAPI backend
└── frontend/              ← React frontend
```

## Notes

- The scripts will automatically check for dependencies
- Backend requires Python virtual environment
- Frontend requires Node.js and npm
- Make sure to update `.env` file with your API keys before using providers

