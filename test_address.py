#!/usr/bin/env python3
"""
Test with different address
"""

import json
import requests

def test_with_usdc_contract():
    """Test with USDC contract address"""
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_address_info",
                "arguments": {
                    "chain_id": "1",
                    "address": "0xA0b86a33E6441b8c4C8C0C4C0C4C0C4C0C4C0C4C"  # Random address
                }
            }
        }
        
        print("🧪 Testing with different address...")
        
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
            print("✅ MCP working!")
            print(f"Result: {result}")
            return True
        else:
            print("❌ No result")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_with_usdc_contract()
