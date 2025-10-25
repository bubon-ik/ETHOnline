#!/bin/bash

# 🔍 BlockScout AI Bot - Deployment Readiness Check

echo "🔍 BlockScout AI Bot - Deployment Readiness Check"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "bot.py" ]; then
    echo "❌ Error: bot.py not found. Run this from the project root."
    exit 1
fi

echo "✅ Project files found"

# Check Procfile
if [ -f "Procfile" ]; then
    echo "✅ Procfile found"
    echo "   Content: $(cat Procfile)"
else
    echo "❌ Procfile missing"
    exit 1
fi

# Check requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
    echo "   Dependencies: $(wc -l < requirements.txt) packages"
else
    echo "❌ requirements.txt missing"
    exit 1
fi

# Check .env
if [ -f ".env" ]; then
    echo "✅ .env file found"
    if grep -q "TELEGRAM_API_TOKEN" .env && grep -q "CLAUDE_API_KEY" .env; then
        echo "✅ API keys configured"
    else
        echo "⚠️  API keys may be missing from .env"
    fi
else
    echo "⚠️  .env file not found (will need to set environment variables manually)"
fi

# Check if bot runs locally
echo ""
echo "🧪 Testing local bot startup..."
timeout 5s python -c "
import sys
import os
sys.path.append('.')
try:
    # Test basic imports
    import anthropic
    import telegram
    import requests
    print('✅ All dependencies imported successfully')
    
    # Test environment variables
    telegram_token = os.getenv('TELEGRAM_API_TOKEN')
    claude_key = os.getenv('CLAUDE_API_KEY')
    
    if telegram_token:
        print('✅ Telegram token loaded')
    else:
        print('❌ Telegram token missing')
        
    if claude_key:
        print('✅ Claude API key loaded')
    else:
        print('❌ Claude API key missing')
        
    # Test bot import
    from bot import anthropic_client
    print('✅ Bot imports successfully')
    
except Exception as e:
    print(f'❌ Bot import failed: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Bot is ready for deployment!"
else
    echo "❌ Bot has issues that need fixing"
    exit 1
fi

echo ""
echo "🚀 DEPLOYMENT READY!"
echo "==================="
echo ""
echo "Next steps:"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Deploy from your ETHOnline repository"
echo "4. Set environment variables:"
echo "   - TELEGRAM_API_TOKEN=your_telegram_bot_token_here"
echo "   - CLAUDE_API_KEY=your_claude_api_key_here"
echo "5. Click Deploy!"
echo ""
echo "🏆 Your bot will be live in minutes!"
