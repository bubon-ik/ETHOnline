#!/usr/bin/env python3
"""
Test MCP integration directly
"""

import asyncio
import json
import requests
from dotenv import load_dotenv

load_dotenv()

async def test_blockscout_mcp():
    """Test Blockscout MCP server directly"""
    try:
        # Test MCP call
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_address_info",
                "arguments": {
                    "chain_id": "1",
                    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"  # vitalik.eth
                }
            }
        }
        
        print("🧪 Testing Blockscout MCP server...")
        print(f"Request: {json.dumps(mcp_request, indent=2)}")
        
        response = requests.post(
            "https://mcp.blockscout.com/mcp",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response JSON: {json.dumps(result, indent=2)}")
                print("✅ MCP server is accessible!")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                return False
        else:
            print("❌ MCP server error!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP: {str(e)}")
        return False

async def main():
    print("🔍 Testing BlockScout MCP Integration...")
    print()
    
    success = await test_blockscout_mcp()
    
    print()
    if success:
        print("🎉 MCP integration test passed!")
        print("📱 Bot should now work with REAL blockchain data!")
    else:
        print("❌ MCP integration test failed!")
        print("🔧 Need to fix MCP connection")

if __name__ == "__main__":
    asyncio.run(main())
