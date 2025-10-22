#!/usr/bin/env python3
"""
Quick MCP test with SSE parsing
"""

import json
import requests

def test_mcp_sse():
    """Test MCP with proper SSE parsing"""
    try:
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
        
        print("🧪 Testing MCP with SSE parsing...")
        
        response = requests.post(
            "https://mcp.blockscout.com/mcp",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        # Parse SSE response
        result = None
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'result' in data:
                        result = data['result']
                        break
                    elif 'error' in data:
                        print(f"❌ MCP Error: {data['error']}")
                        return False
                except json.JSONDecodeError:
                    continue
        
        if result:
            print("✅ MCP integration working!")
            print(f"Result preview: {str(result)[:200]}...")
            return True
        else:
            print("❌ No result found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_sse()
    if success:
        print("\n🎉 Bot is ready to use!")
        print("📱 Go to Telegram and test your bot!")
    else:
        print("\n❌ MCP integration needs more work")
