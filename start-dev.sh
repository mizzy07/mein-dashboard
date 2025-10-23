#!/bin/bash

# Development Startup Script

echo "🚀 Starting AI Crypto Trading Dashboard (Development Mode)"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
fi

# Check if backend/.env exists
if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env from backend/.env.example..."
    cp backend/.env.example backend/.env
    echo "✅ Please edit backend/.env and add your ANTHROPIC_API_KEY"
    echo ""
fi

# Start services
echo "Starting services with docker-compose..."
docker-compose up -d

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Access points:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - Redis:     localhost:6379"
echo ""
echo "📝 View logs:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose down"
echo ""
