"""DeFi Risk Assessment Agent using LangChain + Gemini + Public APIs."""

from typing import Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from .config import GOOGLE_API_KEY, MODEL_CONFIG
from .prompts import RISK_AGENT_SYSTEM_PROMPT
from .tools import get_tools


class DeFiRiskAgent:
    """
    DeFi Risk Assessment Agent using public APIs (GoPlus, DexScreener).

    Uses LangChain + Gemini with tools for:
    - Token security analysis
    - Holder distribution
    - Trading metrics
    - Token details
    - Trending tokens
    """

    def __init__(self):
        self.agent = None
        self.tools = None
        self._initialized = False

    async def initialize(self):
        """Initialize the agent with DeFi analysis tools."""
        if self._initialized:
            return

        print("🔄 Initializing DeFi Risk Agent...")

        # Load tools from public APIs
        self.tools = get_tools()
        print(f"✅ Loaded {len(self.tools)} DeFi analysis tools")
        tool_names = ", ".join(
            [
                "GoPlus Security",
                "Metadata",
                "Rugcheck",
                "SlowMist Incidents",
                "CertiK Audits",
                "Helius Holders",
                "Tx History",
                "DexScreener Holders",
                "Trading Metrics",
                "Token Details",
                "Trending Tokens",
            ]
        )
        print(f"📦 Tools: {tool_names}")

        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model=MODEL_CONFIG["model"],
            temperature=MODEL_CONFIG["temperature"],
            max_output_tokens=MODEL_CONFIG.get("max_output_tokens", 4096),
            google_api_key=GOOGLE_API_KEY,
        )

        # Create ReAct agent
        self.agent = create_agent(
            model=llm,
            tools=self.tools,
            system_prompt=RISK_AGENT_SYSTEM_PROMPT,
        )

        self._initialized = True
        print("✅ DeFi Risk Agent initialized and ready!")

    async def analyze(self, token_address: str) -> dict:
        """
        Analyze a token for rug-pull risk.

        Args:
            token_address: Token mint address (Solana base58 format)

        Returns:
            Analysis result dictionary
        """
        if not self._initialized:
            await self.initialize()

        print(f"\n🔍 Starting analysis for: {token_address}")

        result = await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Analyze this token for rug-pull risk: {token_address}

Use all available tools to gather:
1. Security metrics (mint authority, freeze authority)
2. Holder distribution and concentration
3. Liquidity and pool information
4. Trading statistics and patterns
5. Token details and metadata

Then provide a comprehensive risk assessment with score and recommendation.""",
                    }
                ]
            }
        )

        return result

    async def chat(self, message: str) -> dict:
        """
        Send a custom message to the agent.

        Args:
            message: User message/query

        Returns:
            Agent response dictionary
        """
        if not self._initialized:
            await self.initialize()

        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]}
        )

        return result

    async def get_trending_tokens(self) -> dict:
        """Get currently trending tokens on Solana."""
        return await self.chat(
            "Show me the currently trending tokens on Solana. "
            "Use the trending_tokens tool to get tokens sorted by volume and price change."
        )

    async def quick_lookup(self, token_address: str) -> dict:
        """Quick lookup of basic token information."""
        return await self.chat(
            f"Give me a quick overview of this token: {token_address}. "
            "Use the token_details tool to get basic info like name, price, and market cap."
        )

    async def check_holders(self, token_address: str) -> dict:
        """Check holder distribution for a token."""
        return await self.chat(
            f"Analyze the holder distribution for token: {token_address}. "
            "Use the holder analysis tool to show any concentration risks."
        )

    async def close(self):
        """Clean up resources."""
        self.agent = None
        self.tools = None
        self._initialized = False
        print("👋 Agent closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    # async def chat(self, message: str) -> dict:
    #     """Send a custom message to the agent."""
    #     if not self._initialized:
    #         await self.initialize()

    #     result = await self.agent.ainvoke(
    #         {"messages": [{"role": "user", "content": message}]}
    #     )

    #     return result

    # async def close(self):
    #     """Clean up resources."""
    #     if self.client:
    #         self.client = None
    #         self.agent = None
    #         self.tools = None
    #         self._initialized = False
    #         print("👋 Agent closed")


def extract_response(result: dict) -> str:
    """Extract text response from agent result."""
    if "messages" in result:
        messages = result["messages"]
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content:
                if isinstance(msg.content, list):
                    text_parts = []
                    for block in msg.content:
                        if isinstance(block, dict) and "text" in block:
                            text_parts.append(block["text"])
                        elif isinstance(block, str):
                            text_parts.append(block)
                    return "\n".join(text_parts)
                return msg.content
    return str(result)
