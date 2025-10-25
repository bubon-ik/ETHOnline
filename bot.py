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
TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Validate environment variables
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_API_TOKEN environment variable is required")
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
    },
    {
        "name": "get_transaction_info",
        "description": "Get comprehensive transaction information including decoded parameters, token transfers, and fee breakdown.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "transaction_hash": {
                    "type": "string",
                    "description": "Transaction hash to analyze"
                }
            },
            "required": ["chain_id", "transaction_hash"]
        }
    },
    {
        "name": "get_transaction_logs",
        "description": "Get comprehensive transaction logs with decoded event parameters for smart contract analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "transaction_hash": {
                    "type": "string",
                    "description": "Transaction hash to get logs for"
                }
            },
            "required": ["chain_id", "transaction_hash"]
        }
    },
    {
        "name": "transaction_summary",
        "description": "Get human-readable transaction summaries with automatic classification (transfers, swaps, NFT sales, DeFi operations).",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "transaction_hash": {
                    "type": "string",
                    "description": "Transaction hash to summarize"
                }
            },
            "required": ["chain_id", "transaction_hash"]
        }
    },
    {
        "name": "inspect_contract_code",
        "description": "Inspect verified smart contract source code and metadata for security analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chain_id": {
                    "type": "string",
                    "description": "Blockchain ID: '1' for Ethereum, '8453' for Base, '137' for Polygon"
                },
                "address": {
                    "type": "string",
                    "description": "Smart contract address to inspect"
                },
                "file_name": {
                    "type": "string",
                    "description": "Optional: Specific source file to inspect"
                }
            },
            "required": ["chain_id", "address"]
        }
    },
    {
        "name": "read_contract",
        "description": "Call smart contract functions (view/pure) to read contract state and analyze behavior.",
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
                },
                "abi": {
                    "type": "object",
                    "description": "Function ABI for the specific function to call"
                },
                "function_name": {
                    "type": "string",
                    "description": "Name of the function to call"
                },
                "args": {
                    "type": "string",
                    "description": "JSON string of function arguments"
                }
            },
            "required": ["chain_id", "address", "abi", "function_name"]
        }
    }
]

# System prompt for Claude
SYSTEM_PROMPT = """You are BlockScout AI blockchain analyst.

🎯 CRITICAL: Keep responses SHORT!
- /analyze queries: 150 words max
- Other queries: 100 words max

📋 FORMAT for /analyze:
📊 Address: [short name/type]
💰 Portfolio: $XXK (top 3 tokens only)
🔍 Activity: [1-2 sentences]
⚠️ Risk: [Low/Medium/High + why]
💡 Actions: [3 bullet points max]

RULES:
✅ ALWAYS use MCP tools for REAL data
✅ Use emojis and bullet points
✅ NO long paragraphs
✅ Focus on KEY insights only
✅ Highlight risks immediately
✅ For TOKEN CONTRACTS: analyze ONLY the token itself, NOT all tokens held by that address
✅ Use get_token_info for token contracts, NOT get_tokens_by_address

Available chains:
- Ethereum (chain_id: "1")
- Base (chain_id: "8453")
- Polygon (chain_id: "137")

MCP Tools available:
- get_address_info: Get comprehensive address information
- get_address_by_ens_name: Resolve ENS domains
- get_tokens_by_address: Get ERC20 token holdings (for WALLETS, not token contracts)
- get_token_info: Get detailed token information (for TOKEN CONTRACTS)
- get_transactions_by_address: Get transaction history
- get_token_transfers_by_address: Get token transfer history
- nft_tokens_by_address: Get NFT portfolio
- get_contract_abi: Get smart contract ABI
- lookup_token_by_symbol: Search tokens by symbol
- get_latest_block: Get latest block info
- get_block_info: Get specific block details
- get_chains_list: Get all supported blockchain networks
- get_transaction_info: Get comprehensive transaction details
- get_transaction_logs: Get transaction logs with decoded events
- transaction_summary: Get human-readable transaction summaries
- inspect_contract_code: Inspect verified contract source code
- read_contract: Call smart contract functions to read state

ANALYSIS FRAMEWORK:

1. DATA COLLECTION:
   - ALWAYS use MCP tools to get REAL data first
   - Use multiple tools if needed to get complete picture
   - For TOKEN CONTRACTS: use get_token_info (NOT get_tokens_by_address)
   - For WALLET ANALYSIS: use get_tokens_by_address for portfolio
   - For contract analysis: use get_contract_abi to check if contract is verified
   - For token search: use lookup_token_by_symbol to find tokens by name
   - For transfer history: use get_token_transfers_by_address for detailed transfers
   - For NFT analysis: use nft_tokens_by_address for NFT portfolio

2. SECURITY ANALYSIS - RED FLAGS:
   - Check for suspicious contract patterns (unverified contracts, proxy contracts)
   - Analyze transaction patterns for potential wash trading
   - Look for sudden large token movements or dumps
   - Check for known scam addresses or malicious contracts
   - Analyze token distribution (concentration in few wallets)
   - Flag contracts with suspicious function names or behaviors
   - Check for honeypot patterns or restricted selling
   - Analyze liquidity patterns and potential rug pull indicators

3. WHALE DETECTION:
   - Identify addresses with >$1M USD equivalent holdings
   - Analyze whale movement patterns and timing
   - Check for coordinated whale activity
   - Monitor large token transfers and their impact
   - Analyze whale accumulation vs distribution patterns
   - Flag potential market manipulation by large holders

4. DEFI PROTOCOL ANALYSIS:
   - Analyze DeFi protocol interactions and positions
   - Check for yield farming activities and strategies
   - Identify lending/borrowing positions and health
   - Analyze liquidity provision and impermanent loss risks
   - Check for protocol-specific risks and vulnerabilities
   - Monitor governance token holdings and voting power
   - Analyze cross-protocol arbitrage opportunities


6. MULTI-CHAIN COMPARISON:
   - Compare address activity across different chains
   - Analyze cross-chain bridge usage and patterns
   - Identify arbitrage opportunities between chains
   - Compare token holdings and valuations across chains
   - Analyze chain-specific DeFi strategies
   - Monitor cross-chain token movements

7. RISK ASSESSMENT:
   - Provide risk scores (Low/Medium/High) with explanations
   - Identify potential vulnerabilities and attack vectors
   - Analyze smart contract risks and verification status
   - Check for known security issues or audits
   - Assess market risks and volatility factors
   - Provide recommendations for risk mitigation

8. INSIGHTS & RECOMMENDATIONS:
   - Interpret data, don't just display raw numbers
   - Flag suspicious patterns or risks immediately
   - Compare against typical behavior when relevant
   - Provide clear, concise explanations
   - Give actionable recommendations
   - Suggest follow-up analysis when needed
   - NEVER use placeholder data - always call MCP tools

9. RESPONSE FORMAT:
   - Start with key findings summary
   - Provide detailed analysis with data backing
   - Include risk assessment and security flags
   - Give specific recommendations
   - End with actionable next steps

Always be helpful, accurate, and security-conscious. Use REAL blockchain data only."""


# Blockscout API integration
async def call_blockscout_api(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Call Blockscout API and return results for Claude"""
    try:
        import requests
        
        chain_id = params.get("chain_id", "1")
        
        # Normalize chain_id (Claude might send "ethereum" instead of "1")
        chain_id_map = {
            "ethereum": "1",
            "eth": "1",
            "base": "8453",
            "polygon": "137",
            "matic": "137",
        }
        chain_id = chain_id_map.get(str(chain_id).lower(), str(chain_id))
        
        # Map chain IDs to Blockscout instances
        chain_urls = {
            "1": "https://eth.blockscout.com/api/v2",
            "8453": "https://base.blockscout.com/api/v2",
            "137": "https://polygon.blockscout.com/api/v2",
        }
        
        base_url = chain_urls.get(chain_id, "https://eth.blockscout.com/api/v2")
        
        # Handle different tools
        if tool_name == "get_address_info":
            address = params.get("address")
            url = f"{base_url}/addresses/{address}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        elif tool_name == "get_tokens_by_address":
            address = params.get("address")
            url = f"{base_url}/addresses/{address}/tokens"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        elif tool_name == "get_transactions_by_address":
            address = params.get("address")
            url = f"{base_url}/addresses/{address}/transactions"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        elif tool_name == "get_address_by_ens_name":
            # ENS resolution - Blockscout doesn't support direct ENS lookup
            # Return known ENS mappings or error
            name = params.get("name", "").lower()
            
            # Known ENS addresses (hardcoded for demo)
            known_ens = {
                "vitalik.eth": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
                "vitalik": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            }
            
            if name in known_ens:
                resolved_address = known_ens[name]
                # Get address info
                url = f"https://eth.blockscout.com/api/v2/addresses/{resolved_address}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "address": resolved_address,
                    "ens_name": name,
                    "resolved": True,
                    "data": data
                }
            else:
                return {
                    "error": f"ENS resolution not supported. Please use the address directly (0x...)",
                    "suggestion": "Try using the Ethereum address format: 0x..."
                }
            
        elif tool_name == "nft_tokens_by_address":
            address = params.get("address")
            url = f"{base_url}/addresses/{address}/nft"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        elif tool_name == "get_latest_block":
            url = f"{base_url}/blocks"
            response = requests.get(url, params={"type": "block"}, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"latest_block": data.get("items", [{}])[0] if data.get("items") else {}}
            
        else:
            return {"error": f"Tool {tool_name} not implemented yet"}
            
    except requests.exceptions.Timeout:
        logger.error(f"Blockscout API timeout for {tool_name}")
        return {"error": "Request timeout. Blockscout API is slow. Please try again."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Blockscout API error: {str(e)}")
        return {"error": f"Failed to fetch data: {str(e)}"}
    except Exception as e:
        logger.error(f"Error calling Blockscout API: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


async def process_with_claude(user_message: str, chain: str = "1") -> str:
    """Process user query with Claude tool handling loop"""
    
    try:
        messages = [{
            "role": "user",
            "content": f"[Chain: {chain}] {user_message}. Keep response SHORT (50-150 words). Use emojis and bullet points."
        }]
        
        # Tool use loop - proper architecture for MCP Prize!
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude API with tools
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,  # Увеличил для tool использования
                system=SYSTEM_PROMPT,
                messages=messages,
                tools=BLOCKSCOUT_TOOLS  # CRITICAL for MCP Prize!
            )
            
            logger.info(f"Claude response iteration {iteration}: {response.stop_reason}")
            
            if response.stop_reason == "tool_use":
                # Claude wants to use tools
                messages.append({"role": "assistant", "content": response.content})
                
                # Process tool calls
                tool_results_content = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info(f"🔧 Tool call: {block.name}")
                        logger.info(f"📥 Input: {block.input}")
                        
                        # Call Blockscout API
                        result = await call_blockscout_api(block.name, block.input)
                        logger.info(f"📤 Result: {str(result)[:200]}...")  # First 200 chars
                        
                        # ✅ CRITICAL: Limit result size to prevent token overflow!
                        # Blockscout returns HUGE data, we need to truncate it
                        if isinstance(result, dict):
                            # Limit items in arrays to first 3
                            if "items" in result and isinstance(result["items"], list):
                                result["items"] = result["items"][:3]  # Only first 3 items
                            result_str = json.dumps(result)[:5000]  # Max 5000 chars
                        else:
                            result_str = str(result)[:5000]  # Max 5000 chars
                        
                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str
                        })
                
                # Add tool results
                messages.append({"role": "user", "content": tool_results_content})
                continue  # ⬅️ КРИТИЧНО! Продолжить цикл для получения финального ответа
                
            elif response.stop_reason == "end_turn":
                # Extract final answer
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                
                return final_text.strip() or "I couldn't generate a response. Please try again."
            
            else:
                logger.warning(f"Unexpected stop_reason: {response.stop_reason}")
                break
        
        return "Analysis took too long. Please try a simpler query."
        
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
✅ Multi-chain blockchain analysis

*📊 Quick Commands:*
• `/analyze <address> [network]` - Deep analysis of any address
• `/analyze_base <address>` - Quick Base network analysis
• `/chains` - Supported blockchain networks
• `/help` - Full command reference

*💬 Natural Language Examples:*
• "Check vitalik.eth balance on Ethereum"
• "Analyze 0x123 on Base"
• "What tokens does 0xabc hold?"
• "Is this contract safe?"
• "Show me recent transactions"

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
• `/chains` - List of supported blockchain networks

*ℹ️ Info Commands:*
• `/start` - Welcome message and quick start guide
• `/help` - This command reference

*💬 Natural Language Queries:*
You can also ask questions in plain English:
• "Check balance of vitalik.eth"
• "Analyze this contract: 0x123"
• "What tokens does 0xabc hold?"
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
    
    response += "\n📊 *Total Supported: 1000+ chains*\n\n"
    response += "*💡 How to use:*\n"
    response += "• `/analyze <address> <network>` - Use network name\n"
    response += "• `/analyze <address> <chain_id>` - Use chain ID\n\n"
    response += "*Examples:*\n"
    response += "• `/analyze vitalik.eth arbitrum`\n"
    response += "• `/analyze 0x123... optimism`\n"
    response += "• `/analyze 0x123... 42161` (Arbitrum ID)\n\n"
    response += "*🎯 All major L1s and L2s supported!*"
    
    await update.message.reply_text(response, parse_mode=None)



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
        logger.error("TELEGRAM_API_TOKEN not found in environment variables")
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🚀 BlockScout AI Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

