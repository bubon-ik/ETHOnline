#!/usr/bin/env python3
"""
BlockScout AI - Telegram Bot
Intelligent blockchain analysis powered by Claude 3.5 Sonnet and Blockscout MCP
"""

import os
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Blockscout MCP Tools Definition - Real MCP Tools
BLOCKSCOUT_TOOLS = [
    {
        "name": "get_address_info",
        "description": "Get comprehensive information about a blockchain address including balance, contract status, ENS name, token details, and proxy information. Essential for address analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "Wallet or contract address (0x format)"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "get_address_by_ens_name",
        "description": "Resolve ENS domain name (e.g., 'vitalik.eth') to Ethereum address",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "ENS domain name to resolve"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_tokens_by_address",
        "description": "Get ERC20 token holdings for an address with metadata, market data, and balances. Essential for portfolio analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "Wallet address"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "get_transactions_by_address",
        "description": "Get transaction history for an address with decoded parameters and token transfers. Use for activity analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "Wallet or contract address"
                },
                "age_from": {
                    "type": "string",
                    "description": "Optional: Start date/time (ISO format: 2025-01-01T00:00:00.00Z)"
                },
                "age_to": {
                    "type": "string",
                    "description": "Optional: End date/time (ISO format)"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "nft_tokens_by_address",
        "description": "Get NFT tokens (ERC-721, ERC-1155) owned by an address with collection details and metadata.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "NFT owner address"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "get_contract_abi",
        "description": "Get smart contract ABI (Application Binary Interface) for verified contracts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "Smart contract address"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "get_token_transfers_by_address",
        "description": "Get ERC20 token transfers for an address within a specific time range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "Wallet address"
                },
                "age_from": {
                    "type": "string",
                    "description": "Optional: Start date/time (ISO format)"
                },
                "age_to": {
                    "type": "string",
                    "description": "Optional: End date/time (ISO format)"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "lookup_token_by_symbol",
        "description": "Search for token addresses by symbol or name. Returns multiple potential matches.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "symbol": {
                    "type": "string",
                    "description": "Token symbol or name to search for"
                }
            },
            "required": ["chain_id", "symbol"]
        }
    }
]

# System prompt for Claude
SYSTEM_PROMPT = """You are BlockScout AI, an expert blockchain analyst powered by Blockscout MCP data.

CRITICAL: You MUST use the available MCP tools to get REAL blockchain data. Never provide placeholder or fake data.

Your role:
- Analyze REAL blockchain data using MCP tools
- Provide actionable insights based on actual on-chain data
- Explain complex concepts in simple terms
- Identify patterns, risks, and opportunities
- Provide contextual recommendations
- Be conversational and helpful

Available chains:
- Ethereum (chain_id: "1")
- Base (chain_id: "8453")
- Polygon (chain_id: "137")

MCP Tools available:
- get_address_info: Get comprehensive address information
- get_address_by_ens_name: Resolve ENS domains
- get_tokens_by_address: Get ERC20 token holdings
- get_transactions_by_address: Get transaction history
- nft_tokens_by_address: Get NFT portfolio
- get_contract_abi: Get smart contract ABI
- get_token_transfers_by_address: Get token transfer history
- lookup_token_by_symbol: Search tokens by symbol

When analyzing:
1. ALWAYS use MCP tools to get REAL data first
2. Use multiple tools if needed to get complete picture
3. Interpret data, don't just display raw numbers
4. Flag suspicious patterns or risks
5. Compare against typical behavior when relevant
6. Provide clear, concise explanations
7. NEVER use placeholder data - always call MCP tools

Always be helpful, accurate, and security-conscious. Use REAL blockchain data only."""


async def call_blockscout_mcp(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Call Blockscout MCP server directly via HTTP"""
    try:
        import requests
        
        # Blockscout MCP server endpoint
        mcp_url = "https://mcp.blockscout.com/mcp"
        
        # Prepare MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_input
            }
        }
        
        logger.info(f"Calling Blockscout MCP: {tool_name} with {tool_input}")
        
        # Make HTTP request to Blockscout MCP
        response = requests.post(
            mcp_url,
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=30
        )
        
        response.raise_for_status()
        
        # Parse Server-Sent Events (SSE) response
        result = None
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'result' in data:
                        result = data['result']
                        break
                    elif 'error' in data:
                        return {"error": data['error']}
                except json.JSONDecodeError:
                    continue
        
        if result:
            logger.info(f"MCP response: {result}")
            return result
        else:
            return {"error": "No result found in MCP response"}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"MCP HTTP request failed: {str(e)}")
        return {"error": f"Failed to connect to Blockscout MCP: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in MCP call: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


async def process_with_claude(user_message: str, chain: str = "1") -> str:
    """Process user query with Claude + MCP tools"""
    try:
        messages = [
            {
                "role": "user",
                "content": f"[Chain: {chain}] {user_message}"
            }
        ]
        
        # Tool use loop
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude API
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=BLOCKSCOUT_TOOLS,
                messages=messages
            )
            
            logger.info(f"Claude response (iteration {iteration}): {response.stop_reason}")
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Add assistant response to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Process tool calls
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info(f"Tool call: {block.name} with input: {block.input}")
                        
                        # Call Blockscout MCP tool
                        result = await call_blockscout_mcp(block.name, block.input)
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result)
                        })
                
                # Add tool results to messages
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
            elif response.stop_reason == "end_turn":
                # Extract final text response
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                
                return final_text.strip() or "I couldn't generate a response. Please try again."
            
            else:
                # Unexpected stop reason
                return f"Unexpected response from AI. Please try again."
        
        return "Analysis took too long. Please simplify your query."
        
    except Exception as e:
        logger.error(f"Error processing with Claude: {str(e)}", exc_info=True)
        return f"Sorry, I encountered an error analyzing your request. Please try again."


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    welcome_message = """🤖 *Welcome to BlockScout AI!*

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

    await update.message.reply_text(
        welcome_message,
        parse_mode=None
    )


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze command"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an address to analyze.\n\n"
            "Usage: `/analyze <address>`\n"
            "Example: `/analyze vitalik.eth`",
            parse_mode="Markdown"
        )
        return
    
    address = " ".join(context.args)
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Process with Claude
    query = f"Analyze this address: {address}. Provide a comprehensive overview including balance, tokens, recent activity, and any notable patterns or risks."
    response = await process_with_claude(query, chain="1")
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_message = """📚 *BlockScout AI - Command Reference*

*🔍 Analysis Commands:*
• `/analyze <address>` - Comprehensive address analysis
  Example: `/analyze vitalik.eth`
  Example: `/analyze 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`

*📊 Network Commands:*
• `/gas` - Current Ethereum gas prices and network status
• `/chains` - List of supported blockchain networks

*ℹ️ Info Commands:*
• `/start` - Welcome message and quick start guide
• `/help` - This command reference

*💬 Natural Language Queries:*
You can also ask questions in plain English:
• "Check balance of vitalik.eth"
• "Analyze this contract: 0x123"
• "What tokens does 0xabc hold?"
• "Show me gas prices"
• "Is this address safe?"
• "Recent transactions for 0xdef"

*🌐 Supported Networks:*
• *Ethereum* (chain_id: 1) - Mainnet
• *Base* (chain_id: 8453) - Coinbase L2
• *Polygon* (chain_id: 137) - Polygon PoS

*🎯 Features:*
✅ Real-time blockchain data via Blockscout MCP
✅ AI-powered analysis and insights
✅ Risk assessment and pattern detection
✅ Token and NFT portfolio tracking
✅ Transaction history analysis
✅ Smart contract verification

*🏆 Built for ETHOnline 2025 - Blockscout MCP Prize*

Need more help? Just ask me anything about blockchain analysis!"""

    await update.message.reply_text(
        help_message,
        parse_mode=None
    )


async def chains_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /chains command"""
    chains_message = """🌐 *Supported Blockchain Networks*

*🔗 Ethereum Mainnet*
• Chain ID: `1`
• Native Currency: ETH
• Block Time: ~12 seconds
• Gas: ETH-based
• Status: ✅ Active

*🔗 Base*
• Chain ID: `8453`
• Native Currency: ETH
• Block Time: ~2 seconds
• Gas: ETH-based (lower fees)
• Status: ✅ Active
• Powered by: Coinbase

*🔗 Polygon PoS*
• Chain ID: `137`
• Native Currency: MATIC
• Block Time: ~2 seconds
• Gas: MATIC-based (very low fees)
• Status: ✅ Active

*📊 Network Comparison:*
Network    | Block Time | Gas Fees | Speed
-----------|------------|----------|--------
Ethereum   | ~12s       | High     | Slow
Base       | ~2s        | Medium   | Fast
Polygon    | ~2s        | Low      | Fast

*🎯 Usage Examples:*
• `/analyze vitalik.eth` (Ethereum)
• `/analyze 0x123` (defaults to Ethereum)
• "Check balance on Base"
• "Analyze contract on Polygon"

*💡 Pro Tip:*
Use natural language to specify networks:
• "Check vitalik.eth on Ethereum"
• "Analyze 0x123 on Base"
• "Show tokens on Polygon"

All networks provide real-time data via Blockscout MCP! 🚀"""

    await update.message.reply_text(
        chains_message,
        parse_mode=None
    )


async def gas_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /gas command"""
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Get gas prices using MCP tools
    query = "Get current Ethereum gas prices and network status. Provide detailed analysis including slow, standard, fast, and instant gas prices, network utilization, and recommendations for optimal transaction timing."
    response = await process_with_claude(query, chain="1")
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages"""
    user_message = update.message.text
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Process with Claude
    response = await process_with_claude(user_message)
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    
    if update and update.message:
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again later."
        )


def main() -> None:
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    if not os.getenv("CLAUDE_API_KEY"):
        logger.error("CLAUDE_API_KEY not found in environment variables")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("chains", chains_command))
    application.add_handler(CommandHandler("gas", gas_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🚀 BlockScout AI Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

