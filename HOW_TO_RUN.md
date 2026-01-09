# 🚀 How to Run Backend and Frontend

## Quick Start (Easiest Method)

### Step 1: Create Environment Files (If Not Already Created)

**Backend `.env` file** (`backend/.env`):
```env
DEBUG=true
ENVIRONMENT=development
OPENAI_API_KEY=your-openai-api-key-here
USE_OPENAI_FALLBACK=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Frontend `.env` file** (`frontend/.env`):
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

> **Note:** Get your OpenAI API key from https://platform.openai.com/api-keys

### Step 2: Run Both Servers

Open **TWO separate PowerShell terminals** in the project root (`C:\ik\ResumeCoach`):

#### Terminal 1 - Backend:
```powershell
.\run_backend.ps1
```

#### Terminal 2 - Frontend:
```powershell
.\run_frontend.ps1
```

That's it! The servers will start automatically.

---

## Manual Method (Alternative)

If you prefer to run commands manually:

### Terminal 1 - Backend:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend:
```powershell
cd frontend
npm start
```

---

## What You'll See

### Backend Terminal:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Terminal:
```
Compiled successfully!

You can now view resume-coach-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

---

## Access the Application

Once both servers are running:

- **Frontend (Main App)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## Troubleshooting

### Backend Issues:

1. **"Module not found"**
   - Make sure virtual environment is activated: `.\venv\Scripts\Activate.ps1`
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **"OpenAI API error"**
   - Check your API key in `backend/.env`
   - Make sure the key starts with `sk-`

3. **"Port 8000 already in use"**
   - Stop other applications using port 8000
   - Or change port: `uvicorn app.main:app --reload --port 8001`

4. **"spacy model not found"**
   - Run: `python -m spacy download en_core_web_sm`

### Frontend Issues:

1. **"npm start fails"**
   - Make sure you're in `frontend/` directory
   - Run `npm install` first

2. **"Cannot connect to API"**
   - Make sure backend is running first
   - Check `frontend/.env` has correct API URL
   - Verify backend is on port 8000

3. **"Port 3000 already in use"**
   - Stop other React apps
   - Or set different port: `set PORT=3001 && npm start`

### CORS Errors:

- Make sure `backend/.env` includes: `CORS_ORIGINS=http://localhost:3000,http://localhost:8000`
- Restart backend after changing `.env` file

---

## Stopping the Servers

Press `Ctrl+C` in each terminal to stop the servers.

---

## Next Steps

1. Open http://localhost:3000 in your browser
2. Upload a resume (PDF, DOCX, or TXT)
3. Enter a job description
4. Get AI-powered analysis!
