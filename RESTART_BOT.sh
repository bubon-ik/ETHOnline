#!/bin/bash

echo "🔄 Restarting BlockScout AI Bot..."
echo "================================"

# Kill old process
pkill -f "python.*bot.py" 2>/dev/null && echo "✅ Old process stopped" || echo "No old process found"

# Wait a bit
sleep 1

# Start new process
cd /home/user/Documents/ETHOnline
source venv/bin/activate

echo ""
echo "🚀 Starting bot..."
echo "================================"
python bot.py

