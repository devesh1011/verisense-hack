# 🛡️ DeFi Risk Assessment Agent

An AI-powered agent that analyzes cryptocurrency tokens for rug-pull risk, built with LangChain, Google Gemini, and Cambrian MCP.

## ✨ Features

- **Token Security Analysis**: Check mint authority, freeze authority, ownership risks
- **Holder Distribution**: Identify whale concentration and distribution patterns
- **Liquidity Assessment**: Evaluate LP depth and pool health
- **Trading Analytics**: Analyze buy/sell ratios and trading patterns
- **Risk Scoring**: Get an aggregated risk score (1-10) with recommendations

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd verisense-hack
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Google API key
```

Get your Google AI API key from: https://ai.google.dev/gemini-api/docs/api-key

### 3. Run the Agent

```bash
# Interactive mode
python main.py

# Analyze a specific token
python main.py So11111111111111111111111111111111111111112

# Show trending tokens
python main.py --trending
```

## 📖 Usage

### Interactive Mode

```
🤖 > analyze EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
🤖 > trending
🤖 > quick DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
🤖 > holders So11111111111111111111111111111111111111112
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

asyncio.run(main())
```

## 🛠️ Tech Stack

| Component       | Technology              |
| --------------- | ----------------------- |
| Agent Framework | LangChain + LangGraph   |
| LLM             | Google Gemini 2.0 Flash |
| Data Provider   | Cambrian MCP            |
| Runtime         | Python 3.11+            |

## 📁 Project Structure

```
verisense-hack/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
├── src/
│   ├── __init__.py
│   ├── agent.py         # Agent implementation
│   ├── config.py        # Configuration
│   └── prompts.py       # System prompts
└── BUILD_GUIDE.md       # Detailed build documentation
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
