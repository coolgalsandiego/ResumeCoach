# Quick Run Guide - Resume Coach

## 🚀 Fastest Way to Run

### Option 1: Use the Run Scripts (Recommended)

**Terminal 1 - Backend:**
```powershell
.\run_backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\run_frontend.ps1
```

### Option 2: Manual Steps

#### Backend Setup

1. **Create `.env` file in `backend/` directory:**
   ```env
   DEBUG=true
   ENVIRONMENT=development
   OPENAI_API_KEY=your-openai-api-key-here
   USE_OPENAI_FALLBACK=true
   CORS_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

2. **Activate virtual environment and start:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Create `.env` file in `frontend/` directory:**
   ```env
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

2. **Install and start:**
   ```powershell
   cd frontend
   npm install
   npm start
   ```

## ⚠️ Important: Get Your OpenAI API Key

Before running, you need an OpenAI API key:

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy it and paste into `backend/.env` file as `OPENAI_API_KEY=your-key-here`

## 📍 Access Points

Once both servers are running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🐛 Troubleshooting

### Backend won't start
- Check that `.env` file exists in `backend/` directory
- Verify OpenAI API key is set correctly
- Make sure virtual environment is activated
- Check if port 8000 is already in use

### Frontend won't start
- Run `npm install` in `frontend/` directory
- Check that `.env` file exists in `frontend/` directory
- Verify backend is running on port 8000
- Check if port 3000 is already in use

### API Connection Errors
- Make sure backend is running first
- Check CORS settings in `backend/.env`
- Verify `REACT_APP_API_URL` in `frontend/.env` matches backend URL

## ✅ Verification

1. Backend is running if you see: `Uvicorn running on http://0.0.0.0:8000`
2. Frontend is running if browser opens to http://localhost:3000
3. Test backend by visiting http://localhost:8000/docs
