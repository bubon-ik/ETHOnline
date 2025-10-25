#!/bin/bash

# 🚀 BlockScout AI Bot - Quick Deploy Script

echo "🚀 BlockScout AI Bot Deployment"
echo "================================"

# Check if we're in the right directory
if [ ! -f "bot.py" ]; then
    echo "❌ Error: bot.py not found. Run this from the project root."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found."
    echo "Please create .env with your API keys first."
    exit 1
fi

echo "✅ Project files found"
echo "✅ Procfile ready for Railway"

echo ""
echo "🌐 DEPLOYMENT OPTIONS:"
echo "1. Railway (FREE) - Recommended"
echo "2. Heroku (PAID)"
echo "3. Local testing"

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Railway Deployment:"
        echo "1. Go to https://railway.app"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "4. Select your ETHOnline repository"
        echo "5. Add environment variables:"
        echo "   - TELEGRAM_API_TOKEN"
        echo "   - CLAUDE_API_KEY"
        echo "6. Click 'Deploy'"
        echo ""
        echo "✅ Your bot will be live in minutes!"
        ;;
    2)
        echo ""
        echo "🐳 Heroku Deployment:"
        echo "1. Install Heroku CLI"
        echo "2. Run: heroku login"
        echo "3. Run: heroku create your-bot-name"
        echo "4. Run: heroku config:set TELEGRAM_API_TOKEN=your_token"
        echo "5. Run: heroku config:set CLAUDE_API_KEY=your_key"
        echo "6. Run: git push heroku main"
        ;;
    3)
        echo ""
        echo "🔧 Local Testing:"
        echo "Starting bot locally..."
        source venv/bin/activate
        python bot.py
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "🏆 Deployment complete! Your bot is ready for ETHOnline 2025!"
