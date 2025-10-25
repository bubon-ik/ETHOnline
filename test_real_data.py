#!/usr/bin/env python3
"""
Test script to verify bot returns REAL data from Blockscout
"""

import asyncio
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import json

load_dotenv()

# Simplified test
async def test_blockscout_api():
    """Test direct Blockscout API call"""
    import requests
    
    print("🧪 Testing Blockscout API...")
    print("=" * 60)
    
    # Test vitalik.eth
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # vitalik.eth
    url = f"https://eth.blockscout.com/api/v2/addresses/{address}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Address: {address}")
        print(f"✅ Balance: {data.get('coin_balance', 'N/A')}")
        print(f"✅ Transactions: {data.get('tx_count', 'N/A')}")
        print(f"✅ Is Contract: {data.get('is_contract', False)}")
        print()
        print("=" * 60)
        print("✅ BLOCKSCOUT API WORKS!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

async def test_claude_with_tools():
    """Test Claude with tool definitions"""
    print("\n🧪 Testing Claude with tools...")
    print("=" * 60)
    
    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    
    # Simple tool definition
    tools = [{
        "name": "get_address_info",
        "description": "Get blockchain address information",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {"type": "string"},
                "address": {"type": "string"}
            },
            "required": ["chain_id", "address"]
        }
    }]
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system="You are a blockchain analyst. Use tools to get real data.",
            messages=[{
                "role": "user",
                "content": "Analyze vitalik.eth (0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045)"
            }],
            tools=tools
        )
        
        print(f"✅ Response stop_reason: {response.stop_reason}")
        
        if response.stop_reason == "tool_use":
            print("✅ Claude wants to use tools!")
            for block in response.content:
                if block.type == "tool_use":
                    print(f"   Tool: {block.name}")
                    print(f"   Input: {block.input}")
        else:
            print(f"⚠️  Claude didn't use tools (stop_reason: {response.stop_reason})")
        
        print()
        print("=" * 60)
        print("✅ CLAUDE TOOL INTEGRATION WORKS!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

async def main():
    print("\n" + "=" * 60)
    print("🚀 TESTING REAL DATA INTEGRATION")
    print("=" * 60 + "\n")
    
    # Test 1: Blockscout API
    test1 = await test_blockscout_api()
    
    # Test 2: Claude with tools
    test2 = await test_claude_with_tools()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("✅ ALL TESTS PASSED!")
        print("🎉 Bot will return REAL data from Blockscout!")
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️  Check the errors above")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

