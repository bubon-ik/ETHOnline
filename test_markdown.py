#!/usr/bin/env python3
"""
Test Markdown parsing for Telegram
"""

def test_markdown():
    """Test if Markdown messages are valid"""
    
    # Test start message
    start_message = """🤖 *Welcome to BlockScout AI!*

I'm your intelligent blockchain analyst powered by Claude 3.5 Sonnet and Blockscout MCP data.

*🚀 What I can do:*
✅ Analyze wallet addresses and smart contracts
✅ Check token balances and NFT portfolios  
✅ Review transaction history with AI insights
✅ Identify patterns, risks, and opportunities
✅ Provide actionable recommendations
✅ Show current gas prices and network stats

*📊 Quick Commands:*
• `/analyze <address>` - Deep analysis of any address
• `/gas` - Current Ethereum gas prices
• `/chains` - Supported blockchain networks
• `/help` - Full command reference

*💬 Natural Language Examples:*
• "Check vitalik.eth balance on Ethereum"
• "Analyze 0x123 on Base"
• "What tokens does 0xabc hold?"
• "Show me gas prices"
• "Is this contract safe?"

*🌐 Supported Chains:*
• Ethereum (chain_id: 1)
• Base (chain_id: 8453)
• Polygon (chain_id: 137)

*🎯 Built for ETHOnline 2025 - Blockscout MCP Prize*

Let's explore the blockchain together! 🚀"""

    print("Testing Markdown messages...")
    print(f"Start message length: {len(start_message)}")
    
    # Check for common issues
    issues = []
    
    # Check for unclosed asterisks
    asterisk_count = start_message.count('*')
    if asterisk_count % 2 != 0:
        issues.append(f"Unclosed asterisks: {asterisk_count}")
    
    # Check for problematic characters
    if '...' in start_message:
        issues.append("Contains problematic ellipsis")
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Markdown looks good!")
        return True

if __name__ == "__main__":
    test_markdown()
