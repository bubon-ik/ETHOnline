#!/usr/bin/env python3
"""Test ENS resolution"""

import requests

print("🧪 Testing ENS resolution for vitalik.eth...")
print("=" * 60)

try:
    url = "https://eth.blockscout.com/api/v2/addresses/vitalik.eth"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    print(f"✅ ENS: vitalik.eth")
    print(f"✅ Address: {data.get('hash', 'N/A')}")
    print(f"✅ Balance: {data.get('coin_balance', 'N/A')}")
    print(f"✅ Is Contract: {data.get('is_contract', False)}")
    print()
    print("=" * 60)
    print("✅ ENS RESOLUTION WORKS!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print()
    print("Trying direct address instead...")
    
    # Try with direct address
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    url = f"https://eth.blockscout.com/api/v2/addresses/{address}"
    response = requests.get(url, timeout=10)
    data = response.json()
    
    print(f"✅ Address: {address}")
    print(f"✅ Balance: {data.get('coin_balance', 'N/A')}")

