# 🎯 START HERE - Resume Coach Setup

## ✅ What's Already Done

1. ✅ Virtual environment created in `backend/venv`
2. ✅ Backend dependencies installation started (may still be running)
3. ✅ Frontend dependencies installation started (may still be running)
4. ✅ Run scripts created (`run_backend.ps1` and `run_frontend.ps1`)
5. ✅ Setup guides created

## ⚠️ What You Need to Do

### Step 1: Create Backend `.env` File

Create a file named `.env` in the `backend/` directory with this content:

```env
DEBUG=true
ENVIRONMENT=development
OPENAI_API_KEY=your-openai-api-key-here
USE_OPENAI_FALLBACK=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Get your OpenAI API key from:** https://platform.openai.com/api-keys

### Step 2: Create Frontend `.env` File

Create a file named `.env` in the `frontend/` directory with this content:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Step 3: Wait for Installation to Complete

The backend and frontend dependencies are installing in the background. Wait a few minutes for:
- Backend: Python packages (especially torch, transformers, etc.)
- Frontend: npm packages

### Step 4: Download spaCy Model

After backend installation completes, run:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m spacy download en_core_web_sm
```

### Step 5: Run the Application

**Option A: Use the run scripts (Easiest)**

Open **TWO** PowerShell terminals:

**Terminal 1:**
```powershell
.\run_backend.ps1
```

**Terminal 2:**
```powershell
.\run_frontend.ps1
```

**Option B: Manual commands**

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

## 🌐 Access the Application

Once both servers are running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📚 More Help

- See `QUICK_RUN.md` for quick reference
- See `SETUP_GUIDE.md` for detailed setup instructions
- See `README.md` for full project documentation

## 🐛 Common Issues

1. **"Module not found"** → Make sure virtual environment is activated
2. **"OpenAI API error"** → Check your API key in `backend/.env`
3. **"Port already in use"** → Stop other applications using ports 3000 or 8000
4. **"CORS error"** → Verify CORS_ORIGINS in `backend/.env` includes `http://localhost:3000`

## ✨ You're Ready!

Once you've created the `.env` files and installations complete, you can start the application!
