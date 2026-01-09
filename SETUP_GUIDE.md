# Setup Guide - Resume Coach

## Quick Setup Instructions

### Step 1: Backend Setup

1. **Create virtual environment** (if not already created):
   ```powershell
   cd backend
   python -m venv venv
   ```

2. **Activate virtual environment**:
   ```powershell
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Create `.env` file in `backend/` directory**:
   ```env
   # Application Settings
   APP_NAME=Resume Coach
   APP_VERSION=1.0.0
   DEBUG=true
   ENVIRONMENT=development

   # API Configuration
   API_V1_PREFIX=/api/v1

   # AWS Configuration (optional for local development)
   AWS_REGION=us-east-1

   # SageMaker (optional - leave empty for OpenAI fallback)
   SAGEMAKER_ENDPOINT_NAME=
   USE_SAGEMAKER=false

   # OpenAI API Key (REQUIRED for local development)
   # Get your key from: https://platform.openai.com/api-keys
   OPENAI_API_KEY=your-openai-api-key-here
   USE_OPENAI_FALLBACK=true

   # CORS
   CORS_ORIGINS=http://localhost:3000,http://localhost:8000

   # File Upload
   MAX_UPLOAD_SIZE=10485760
   ALLOWED_EXTENSIONS=pdf,docx,txt

   # JWT (for production, use a secure random key)
   JWT_SECRET_KEY=dev-secret-key-change-in-production
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

   **Important**: Replace `your-openai-api-key-here` with your actual OpenAI API key!

### Step 2: Frontend Setup

1. **Navigate to frontend directory**:
   ```powershell
   cd frontend
   ```

2. **Install dependencies**:
   ```powershell
   npm install
   ```

3. **Create `.env` file in `frontend/` directory**:
   ```env
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

### Step 3: Run the Application

**Terminal 1 - Backend:**
```powershell
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

### Backend Issues

1. **Module not found errors**: Make sure virtual environment is activated
2. **OpenAI API errors**: Check your API key in `.env` file
3. **Port already in use**: Change port with `--port 8001` flag

### Frontend Issues

1. **npm install fails**: Try `npm install --legacy-peer-deps`
2. **API connection errors**: Check that backend is running on port 8000
3. **CORS errors**: Verify CORS_ORIGINS in backend `.env` includes `http://localhost:3000`

## Next Steps

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Add it to `backend/.env` file
3. Start both servers
4. Upload a resume and test the analysis!
