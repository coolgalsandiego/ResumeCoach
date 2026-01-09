#!/bin/bash

# Frontend Startup Script for Resume Coach (macOS/Linux)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Resume Coach Frontend...${NC}"

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies (this may take a few minutes)...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Check if .env file exists
if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}WARNING: frontend/.env file not found!${NC}"
    echo -e "${CYAN}Creating frontend/.env file with default values...${NC}"
    echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > frontend/.env
fi

# Start the development server
echo ""
echo -e "${GREEN}Starting React development server...${NC}"
echo -e "${CYAN}Frontend will be available at: http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

cd frontend
npm start

