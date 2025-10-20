#!/bin/bash

# Capacity Planner Backend Setup & Start Script

set -e

echo "🚀 Capacity Planner Backend Setup"
echo "================================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the capacity-be directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Install dependencies
echo "📦 Installing dependencies..."
.venv/bin/pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your database settings"
fi

echo ""
echo "✅ Setup completed!"
echo ""
echo "🚀 Starting development server..."
echo "   API will be available at: http://localhost:8000"
echo "   Health check: http://localhost:8000/health"
echo "   API docs: http://localhost:8000/docs"
echo ""

# Start the server
PYTHONPATH="$(pwd)" .venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
