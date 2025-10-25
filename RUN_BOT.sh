#!/bin/bash

# BlockScout AI Bot - Quick Start Script
# ETHOnline 2025 - Blockscout MCP Prize

echo "🚀 Starting BlockScout AI Bot..."
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import telegram" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt --quiet
    echo "✅ Dependencies installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your API keys:"
    echo "  TELEGRAM_API_TOKEN=your_telegram_token"
    echo "  CLAUDE_API_KEY=your_claude_key"
    exit 1
fi

echo "✅ Environment ready"
echo ""
echo "🤖 Starting bot..."
echo "================================"
echo ""

# Run the bot
python bot.py

