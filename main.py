import asyncio

from src.agent import DeFiRiskAgent, extract_response


HELP_TEXT = """
Available Commands:
───────────────────────────────────────────────────────────────
  analyze <token>    Full risk analysis for a token address
  quick <token>      Quick lookup of token info
  holders <token>    Check holder distribution
  trending           Show trending tokens on Solana
  help               Show this help message
  quit / exit        Exit the agent
───────────────────────────────────────────────────────────────

Example Token Addresses:
  SOL:   So11111111111111111111111111111111111111112
  USDC:  EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  BONK:  DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263

Or just ask any question about DeFi tokens!
"""


async def interactive_mode():
    """Run the agent in interactive mode."""

    agent = DeFiRiskAgent()

    try:
        await agent.initialize()

        print(HELP_TEXT)

        while True:
            try:
                user_input = input("\n🤖 > ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            print("\n💭 Processing your question...")
            result = await agent.chat(user_input)
            print(extract_response(result))

    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await agent.close()


def main():
    """Main entry point."""

    asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
