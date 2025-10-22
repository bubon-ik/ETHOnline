#!/usr/bin/env python3
"""
Test script to verify bot functionality
"""

import os
import asyncio
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

async def test_claude_connection():
    """Test Claude API connection"""
    try:
        client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello! Just testing the connection."}]
        )
        
        print("✅ Claude API connection successful!")
        print(f"Response: {response.content[0].text}")
        return True
        
    except Exception as e:
        print(f"❌ Claude API connection failed: {str(e)}")
        return False

def test_telegram_token():
    """Test Telegram token format"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token and ":" in token and len(token) > 20:
        print("✅ Telegram token format looks correct!")
        return True
    else:
        print("❌ Telegram token format is invalid!")
        return False

async def main():
    print("🧪 Testing BlockScout AI Bot Configuration...")
    print()
    
    # Test Telegram token
    telegram_ok = test_telegram_token()
    
    # Test Claude API
    claude_ok = await test_claude_connection()
    
    print()
    if telegram_ok and claude_ok:
        print("🎉 All tests passed! Bot should be working.")
        print()
        print("📱 Next steps:")
        print("1. Find your bot in Telegram")
        print("2. Send /start command")
        print("3. Try /analyze vitalik.eth")
    else:
        print("❌ Some tests failed. Check your configuration.")

if __name__ == "__main__":
    asyncio.run(main())
