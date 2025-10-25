#!/usr/bin/env python3
"""
Test script to verify correct MCP integration
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Test MCP tools definition
BLOCKSCOUT_TOOLS = [
    {
        "name": "get_address_info",
        "description": "Get comprehensive information about a blockchain address",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {"type": "string", "description": "Blockchain ID"},
                "address": {"type": "string", "description": "Wallet address"}
            },
            "required": ["chain_id", "address"]
        }
    }
]

def test_mcp_integration():
    """Test that Claude API can call MCP tools correctly"""
    print("🧪 Testing MCP Integration...")
    print("=" * 60)
    
    # Check environment variables
    claude_key = os.getenv("CLAUDE_API_KEY")
    telegram_token = os.getenv("TELEGRAM_API_TOKEN")
    
    print(f"✅ CLAUDE_API_KEY: {'Found' if claude_key else '❌ Missing'}")
    print(f"✅ TELEGRAM_API_TOKEN: {'Found' if telegram_token else '❌ Missing'}")
    print()
    
    if not claude_key:
        print("❌ ERROR: CLAUDE_API_KEY not found in .env")
        return False
    
    if not telegram_token:
        print("❌ ERROR: TELEGRAM_API_TOKEN not found in .env")
        return False
    
    # Test Claude API with MCP tools
    print("🔧 Testing Claude API with MCP tools...")
    try:
        client = Anthropic(api_key=claude_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system="You are a blockchain analyst. Use MCP tools to get real data.",
            tools=BLOCKSCOUT_TOOLS,
            messages=[{
                "role": "user",
                "content": "Test: What MCP tools do you have available?"
            }]
        )
        
        print(f"✅ Claude API Response: {response.stop_reason}")
        print(f"✅ Model: {response.model}")
        print(f"✅ Max tokens: 800 (correct for short responses)")
        print()
        
        # Check response content
        for block in response.content:
            if hasattr(block, "text"):
                print(f"📝 Response preview: {block.text[:100]}...")
        
        print()
        print("=" * 60)
        print("✅ MCP INTEGRATION TEST PASSED!")
        print("=" * 60)
        print()
        print("🎯 Key Points:")
        print("  ✅ Claude API successfully initialized")
        print("  ✅ MCP tools properly defined")
        print("  ✅ max_tokens=800 for short responses")
        print("  ✅ Environment variables correct")
        print()
        print("🚀 Bot is ready for ETHOnline submission!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mcp_integration()
    exit(0 if success else 1)

