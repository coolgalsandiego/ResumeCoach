#!/bin/bash

# Backend Startup Script for Resume Coach (macOS/Linux)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Use Python 3.12 for better library compatibility (spaCy doesn't support 3.14 yet)
PYTHON_CMD="python3.12"
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD="python3.11"
    if ! command -v $PYTHON_CMD &> /dev/null; then
        PYTHON_CMD="python3"
    fi
fi

echo -e "${GREEN}Starting Resume Coach Backend...${NC}"
echo -e "${CYAN}Using Python: $PYTHON_CMD${NC}"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv backend/venv
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source backend/venv/bin/activate

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}WARNING: backend/.env file not found!${NC}"
    echo -e "${YELLOW}Please create backend/.env file with your OpenAI API key.${NC}"
    echo -e "${YELLOW}See SETUP_GUIDE.md for details.${NC}"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Check if dependencies are installed
echo -e "${CYAN}Checking dependencies...${NC}"
if ! pip list 2>/dev/null | grep -q "fastapi"; then
    echo -e "${YELLOW}Installing dependencies (this may take a few minutes)...${NC}"
    pip install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies. Please check the error above.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Downloading spaCy model...${NC}"
    python -m spacy download en_core_web_sm
fi

# Start the server
echo ""
echo -e "${GREEN}Starting FastAPI server...${NC}"
echo -e "${CYAN}Backend will be available at: http://localhost:8000${NC}"
echo -e "${CYAN}API docs will be available at: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

