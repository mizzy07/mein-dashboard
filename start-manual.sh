#!/bin/bash

# Manual Startup Script (without Docker)

echo "🚀 Starting AI Crypto Trading Dashboard (Manual Mode)"
echo ""

# Check environment files
if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env from backend/.env.example..."
    cp backend/.env.example backend/.env
    echo "✅ Please edit backend/.env and add your ANTHROPIC_API_KEY"
    read -p "Press Enter to continue after editing .env..."
fi

# Start Backend
echo "Starting Backend..."
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Start backend in background
echo "Starting FastAPI server..."
python main.py &
BACKEND_PID=$!

# Return to root
cd ..

# Start Frontend
echo ""
echo "Starting Frontend..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Access points:"
echo "  - Frontend:  http://localhost:5173"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo ""
echo "🛑 Stop services: Press Ctrl+C"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
