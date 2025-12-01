# 🛡️ DeFi Risk Assessment Agent

An AI-powered agent that analyzes cryptocurrency tokens for rug-pull risk, built with LangChain, Google Gemini, and Cambrian MCP.

## ✨ Features

- **Token Security Analysis**: Check mint authority, freeze authority, ownership risks
- **Holder Distribution**: Identify whale concentration and distribution patterns
- **Liquidity Assessment**: Evaluate LP depth and pool health
- **Trading Analytics**: Analyze buy/sell ratios and trading patterns
- **Risk Scoring**: Get an aggregated risk score (1-10) with recommendations

## 🚀 Quick Start

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### 2. Clone and Setup

```bash
cd verisense-hack
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### 3. Configure Environment

Create a `.env` file with:

```bash
GOOGLE_API_KEY=your_api_key_here
```

Get your Google AI API key from: https://ai.google.dev/gemini-api/docs/api-key

### 4. Run the Agent

```bash
# Interactive mode
python main.py

# Analyze a specific token
python main.py So11111111111111111111111111111111111111112

# Run as A2A server
python -m src token_analysis
```

## 📖 Usage

### Interactive CLI Mode

```
🤖 > analyze EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
🤖 > quick So11111111111111111111111111111111111111112
🤖 > holders DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
🤖 > trending
🤖 > help
```

### Programmatic Usage

```python
import asyncio
from src.agent import DeFiRiskAgent

async def main():
    async with DeFiRiskAgent() as agent:
        # Full risk analysis
        result = await agent.analyze("So11111111111111111111111111111111111111112")
        print(result)

        # Quick lookup
        result = await agent.quick_lookup("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        print(result)

        # Get trending tokens
        trending = await agent.get_trending_tokens()
        print(trending)

asyncio.run(main())
```

## 🛠️ Tech Stack

| Component       | Technology                                    |
| --------------- | --------------------------------------------- |
| Agent Framework | LangChain + LangGraph                         |
| LLM             | Google Gemini 2.0 Flash                       |
| Data Sources    | DexScreener, GoPlus, SlowMist, CertiK, Helius |
| Package Manager | uv (Rust-based, ultra-fast)                   |
| Runtime         | Python 3.12+                                  |

## 📁 Project Structure

```
verisense-hack/
├── main.py                  # Interactive CLI entry point
├── __main__.py              # CLI entry script
├── pyproject.toml           # Project configuration and dependencies
├── uv.lock                  # Locked dependency versions
├── .env                     # Environment variables (create this)
├── src/
│   ├── __init__.py
│   ├── __main__.py          # A2A server entrypoint
│   ├── agent.py             # Core DeFi risk agent
│   ├── agent_executor.py    # A2A framework executor
│   ├── config.py            # Configuration settings
│   ├── prompts.py           # System prompts
│   ├── tools.py             # DeFi analysis tools
│   └── utils.py             # Utility functions
└── test_rugcheck.py         # Tool testing suite
```

## 🔑 Example Token Addresses

| Token | Address                                        |
| ----- | ---------------------------------------------- |
| SOL   | `So11111111111111111111111111111111111111112`  |
| USDC  | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| BONK  | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` |

## 📄 License

MIT License

---

_Built for Verisense Hackathon 2025_ 🚀
