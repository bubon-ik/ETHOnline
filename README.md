# BlockScout AI - Intelligent Blockchain Analysis Bot

> 🏆 Built for ETHOnline 2025 - Blockscout MCP Prize

A Telegram bot that provides intelligent blockchain analysis powered by **Claude 3.5 Sonnet** and **Blockscout MCP**.

## 🌟 Features

- **AI-Powered Analysis**: Claude 3.5 Sonnet interprets blockchain data and provides actionable insights
- **Multi-Chain Support**: Ethereum and Base (more coming soon)
- **Wallet Analysis**: Check balances, token holdings, and NFT portfolios
- **Smart Contract Insights**: Analyze contracts, ABIs, and proxy patterns
- **Transaction History**: Review activity with decoded parameters
- **Natural Language Interface**: Ask questions in plain English
- **Risk Detection**: Identifies suspicious patterns and security concerns

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Bot Framework**: python-telegram-bot v21.5
- **AI Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Data Source**: Blockscout MCP Server
- **Deployment**: Railway

## 📋 Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Claude API Key (from [Anthropic Console](https://console.anthropic.com))

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd blockscout-ai-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
CLAUDE_API_KEY=your_claude_api_key_here
```

### 4. Run the bot

```bash
python bot.py
```

## 💬 Usage Examples

### Commands

- `/start` - Welcome message and bot capabilities
- `/analyze <address>` - Comprehensive address analysis

### Natural Language Queries

Just send a message to the bot:

- "Check vitalik.eth balance"
- "Analyze 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb on Ethereum"
- "What tokens does 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 hold?"
- "Show me NFTs owned by 0x123..."

## 🚢 Deployment to Railway

### 1. Create a new project on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose this repository

### 2. Configure environment variables

In Railway dashboard:
- Add `TELEGRAM_BOT_TOKEN`
- Add `CLAUDE_API_KEY`

### 3. Deploy

Railway will automatically:
- Detect Python
- Install dependencies from `requirements.txt`
- Run using the `Procfile` configuration

## 🏗️ Architecture

```
User (Telegram)
    ↓
Telegram Bot (bot.py)
    ↓
Claude API (with MCP tools)
    ↓
Blockscout MCP Server
    ↓
Claude analyzes & interprets data
    ↓
Formatted response to user
```

### Key Components

- **bot.py**: Main bot logic, handlers, Claude integration
- **BLOCKSCOUT_TOOLS**: MCP tool definitions for Claude
- **process_with_claude()**: Tool use loop (Claude → MCP → Response)
- **call_mcp_tool()**: HTTP calls to Blockscout MCP

## 🔧 Configuration

### Supported Chains

- **Ethereum**: chain_id = "1"
- **Base**: chain_id = "8453"

### Available MCP Tools

1. `get_address_info` - Comprehensive address information
2. `get_address_by_ens_name` - ENS domain resolution
3. `get_tokens_by_address` - ERC20 token holdings
4. `get_transactions_by_address` - Transaction history
5. `get_nfts_by_address` - NFT portfolio
6. `get_contract_abi` - Smart contract ABI

## 📝 Development

### Project Structure

```
blockscout-ai-bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── Procfile           # Railway deployment config
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

### Adding New Features

1. Add new tools to `BLOCKSCOUT_TOOLS` list
2. Implement tool endpoint mapping in `call_mcp_tool()`
3. Update system prompt if needed
4. Test locally before deploying

## 🐛 Troubleshooting

### Bot not responding

- Check if `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is running (`python bot.py` shows no errors)
- Check logs for error messages

### AI analysis fails

- Verify `CLAUDE_API_KEY` is valid
- Check Anthropic API quota/credits
- Review logs for API errors

### MCP tool errors

- Ensure Blockscout MCP server is accessible
- Check if chain_id is supported
- Verify address format (0x...)

## 🎯 Roadmap

- [ ] Add more chains (Polygon, Arbitrum, Optimism)
- [ ] Implement caching for frequent queries
- [ ] Add gas price tracking
- [ ] Transaction simulation
- [ ] Portfolio value tracking
- [ ] DeFi protocol integration
- [ ] Whale alerts

## 📜 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📧 Contact

Built for ETHOnline 2025 by [Your Name]

---

**Note**: This is a hackathon project. Use at your own risk. Always verify critical information independently.

