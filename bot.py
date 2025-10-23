#!/usr/bin/env python3
"""
BlockScout AI - Telegram Bot
Intelligent blockchain analysis powered by Claude 3.5 Sonnet and Blockscout MCP
"""

import os
import json
import logging
import re
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

def clean_markdown(text: str) -> str:
    """Clean Markdown text to prevent Telegram parsing errors"""
    if not text:
        return text
    
    # Replace problematic characters that cause parsing errors
    text = text.replace('...', '…')  # Replace ellipses
    text = text.replace('*', '•')   # Replace asterisks with bullets
    text = text.replace('_', '')    # Remove underscores
    text = text.replace('`', '')    # Remove backticks
    text = text.replace('[', '')     # Remove square brackets
    text = text.replace(']', '')     # Remove square brackets
    text = text.replace('(', '')     # Remove parentheses
    text = text.replace(')', '')     # Remove parentheses
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove any remaining problematic characters
    text = re.sub(r'[^\w\s•…\n\-\.\,\:\!\?\%\$]', '', text)
    
    return text.strip()

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Validate environment variables
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not os.getenv("CLAUDE_API_KEY"):
    raise ValueError("CLAUDE_API_KEY environment variable is required")

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
    },
    {
        "name": "get_token_info",
        "description": "Get detailed information about a specific token including metadata, market data, holders count, and contract details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "Token contract address"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "get_latest_block",
        "description": "Get the latest indexed block number and timestamp for a blockchain network.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                }
            },
            "required": ["chain_id"]
        }
    },
    {
        "name": "get_block_info",
        "description": "Get detailed information about a specific block including timestamp, gas used, transaction count, and block details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "number_or_hash": {
                    "type": "string",
                    "description": "Block number or block hash"
                }
            },
            "required": ["chain_id", "number_or_hash"]
        }
    },
    {
        "name": "get_chains_list",
        "description": "Get the complete list of all supported blockchain networks with their IDs and names.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
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
- get_token_info: Get detailed token information
- get_transactions_by_address: Get transaction history
- get_token_transfers_by_address: Get token transfer history
- nft_tokens_by_address: Get NFT portfolio
- get_contract_abi: Get smart contract ABI
- lookup_token_by_symbol: Search tokens by symbol
- get_latest_block: Get latest block info
- get_block_info: Get specific block details
- get_chains_list: Get all supported blockchain networks

When analyzing:
1. ALWAYS use MCP tools to get REAL data first
2. Use multiple tools if needed to get complete picture
3. For token analysis: use get_token_info for detailed token data
4. For contract analysis: use get_contract_abi to check if contract is verified
5. For token search: use lookup_token_by_symbol to find tokens by name
6. For transfer history: use get_token_transfers_by_address for detailed transfers
7. For NFT analysis: use nft_tokens_by_address for NFT portfolio
8. Interpret data, don't just display raw numbers
9. Flag suspicious patterns or risks
10. Compare against typical behavior when relevant
11. Provide clear, concise explanations
12. NEVER use placeholder data - always call MCP tools

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
• `/analyze <address> [network]` - Deep analysis of any address
• `/analyze_base <address>` - Quick Base network analysis
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
• Ethereum (chain_id: 1) - Default
• Base (chain_id: 8453) - Coinbase L2
• Polygon (chain_id: 137) - Polygon PoS

*🎯 Built for ETHOnline 2025 - Blockscout MCP*

Let's explore the blockchain together! 🚀"""

    await update.message.reply_text(
        welcome_message,
        parse_mode=None
    )


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze command with optional network specification"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an address to analyze.\n\n"
            "Usage: /analyze <address> [network]\n"
            "Examples:\n"
            "• /analyze vitalik.eth (Ethereum)\n"
            "• /analyze vitalik.eth ethereum\n"
            "• /analyze 0x123 base\n"
            "• /analyze 0x123 polygon\n\n"
            "Supported networks: ethereum, base, polygon",
            parse_mode=None
        )
        return
    
    # Parse arguments
    args = context.args
    address = args[0]
    network = args[1].lower() if len(args) > 1 else "ethereum"
    
    # Map network names to chain IDs
    chain_map = {
        "ethereum": "1",
        "eth": "1",
        "base": "8453",
        "polygon": "137",
        "matic": "137",
        "arbitrum": "42161",
        "arbitrum one": "42161",
        "optimism": "10",
        "bsc": "56",
        "binance": "56",
        "avalanche": "43114",
        "avax": "43114",
        "fantom": "250",
        "gnosis": "100",
        "linea": "59144"
    }
    
    if network not in chain_map:
        # Check if it's a numeric chain ID
        if network.isdigit():
            chain_id = network
        else:
            await update.message.reply_text(
                f"❌ Unsupported network: {network}\n\n"
                "Supported networks:\n"
                "• ethereum (or eth)\n"
                "• base\n"
                "• polygon (or matic)\n"
                "• arbitrum\n"
                "• optimism\n"
                "• bsc (or binance)\n"
                "• avalanche (or avax)\n"
                "• fantom\n"
                "• gnosis\n"
                "• linea\n\n"
                "Or use chain ID directly (e.g., 42161 for Arbitrum)",
                parse_mode=None
            )
            return
    else:
        chain_id = chain_map[network]
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Process with Claude
    query = f"Analyze this address on {network.title()} network: {address}. Provide a comprehensive overview including balance, tokens, recent activity, and any notable patterns or risks."
    
    try:
        response = await process_with_claude(query, chain=chain_id)
        
        # Clean and validate Markdown
        cleaned_response = clean_markdown(response)
        
        await update.message.reply_text(cleaned_response, parse_mode=None)
        
    except Exception as e:
        logger.error(f"Error in analyze_command: {e}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again later.",
            parse_mode=None
        )


async def analyze_base_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze_base command for quick Base network analysis"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an address to analyze on Base network.\n\n"
            "Usage: /analyze_base <address>\n"
            "Example: /analyze_base 0x123\n\n"
            "This command automatically uses Base network (chain_id: 8453)",
            parse_mode=None
        )
        return
    
    address = context.args[0]
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Process with Claude on Base network
    query = f"Analyze this address on Base network: {address}. Provide a comprehensive overview including balance, tokens, recent activity, and any notable patterns or risks."
    
    try:
        response = await process_with_claude(query, chain="8453")
        
        # Clean and validate Markdown
        cleaned_response = clean_markdown(response)
        
        await update.message.reply_text(cleaned_response, parse_mode=None)
        
    except Exception as e:
        logger.error(f"Error in analyze_base_command: {e}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again later.",
            parse_mode=None
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_message = """📚 *BlockScout AI - Command Reference*

*🔍 Analysis Commands:*
• `/analyze <address> [network]` - Comprehensive address analysis
  Example: `/analyze vitalik.eth` (Ethereum)
  Example: `/analyze vitalik.eth ethereum`
  Example: `/analyze 0x123... base`
  Example: `/analyze 0x123... polygon`
• `/analyze_base <address>` - Quick Base network analysis
  Example: `/analyze_base 0x123...`

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
    """Handle /chains command - show supported blockchain networks"""
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    try:
        # Get chains list from Blockscout MCP
        chains_result = await call_blockscout_mcp("get_chains_list", {})
        
        if chains_result and "content" in chains_result:
            chains_data = json.loads(chains_result["content"][0]["text"])
            chains = chains_data.get("data", [])
            
            # Popular chains (top 10)
            popular_chains = [
                {"name": "Ethereum", "id": "1", "description": "Mainnet"},
                {"name": "Base", "id": "8453", "description": "Coinbase L2"},
                {"name": "Arbitrum One", "id": "42161", "description": "Arbitrum L2"},
                {"name": "Optimism", "id": "10", "description": "Optimism L2"},
                {"name": "Polygon", "id": "137", "description": "Polygon PoS"},
                {"name": "BSC", "id": "56", "description": "Binance Smart Chain"},
                {"name": "Avalanche", "id": "43114", "description": "Avalanche C-Chain"},
                {"name": "Fantom", "id": "250", "description": "Fantom Opera"},
                {"name": "Gnosis", "id": "100", "description": "Gnosis Chain"},
                {"name": "Linea", "id": "59144", "description": "Linea Mainnet"}
            ]
            
            # Build response
            response = "🌐 *Supported Blockchain Networks*\n\n"
            response += "*🔥 Top 10 Popular Chains:*\n"
            
            for chain in popular_chains:
                response += f"• *{chain['name']}* (ID: {chain['id']}) - {chain['description']}\n"
            
            response += f"\n📊 *Total Supported: {len(chains)}+ chains*\n\n"
            response += "*💡 How to use:*\n"
            response += "• `/analyze <address> <network>` - Use network name\n"
            response += "• `/analyze <address> <chain_id>` - Use chain ID\n\n"
            response += "*Examples:*\n"
            response += "• `/analyze vitalik.eth arbitrum`\n"
            response += "• `/analyze 0x123... optimism`\n"
            response += "• `/analyze 0x123... 42161` (Arbitrum ID)\n\n"
            response += "*🎯 All major L1s and L2s supported!*"
            
            await update.message.reply_text(response, parse_mode=None)
            
        else:
            # Fallback if MCP fails
            fallback_response = """🌐 *Supported Blockchain Networks*

*🔥 Top Popular Chains:*
• *Ethereum* (ID: 1) - Mainnet
• *Base* (ID: 8453) - Coinbase L2  
• *Arbitrum One* (ID: 42161) - Arbitrum L2
• *Optimism* (ID: 10) - Optimism L2
• *Polygon* (ID: 137) - Polygon PoS
• *BSC* (ID: 56) - Binance Smart Chain
• *Avalanche* (ID: 43114) - Avalanche C-Chain
• *Fantom* (ID: 250) - Fantom Opera
• *Gnosis* (ID: 100) - Gnosis Chain
• *Linea* (ID: 59144) - Linea Mainnet

📊 *Total Supported: 1000+ chains*

*💡 How to use:*
• `/analyze <address> <network>` - Use network name
• `/analyze <address> <chain_id>` - Use chain ID

*Examples:*
• `/analyze vitalik.eth arbitrum`
• `/analyze 0x123... optimism`
• `/analyze 0x123... 42161` (Arbitrum ID)

*🎯 All major L1s and L2s supported!*"""
            
            await update.message.reply_text(fallback_response, parse_mode=None)
            
    except Exception as e:
        logger.error(f"Error in chains_command: {e}")
        await update.message.reply_text(
            "❌ Error fetching chains list. Please try again later.",
            parse_mode=None
        )


async def gas_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /gas command"""
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Get gas prices using MCP tools
    query = "Get current Ethereum gas prices and network status. Provide detailed analysis including slow, standard, fast, and instant gas prices, network utilization, and recommendations for optimal transaction timing."
    
    try:
        response = await process_with_claude(query, chain="1")
        
        # Clean and validate Markdown
        cleaned_response = clean_markdown(response)
        
        await update.message.reply_text(cleaned_response, parse_mode=None)
        
    except Exception as e:
        logger.error(f"Error in gas_command: {e}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again later.",
            parse_mode=None
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages"""
    user_message = update.message.text
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Process with Claude
    try:
        response = await process_with_claude(user_message)
        
        # Clean and validate Markdown
        cleaned_response = clean_markdown(response)
        
        await update.message.reply_text(cleaned_response, parse_mode=None)
        
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again later.",
            parse_mode=None
        )


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
    application.add_handler(CommandHandler("analyze_base", analyze_base_command))
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

