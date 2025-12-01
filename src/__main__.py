import asyncio
import os
import sys

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import DeFiRiskAgentExecutor
from dotenv import load_dotenv


load_dotenv(override=True)


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 10002
DEFAULT_LOG_LEVEL = "info"


def main(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    log_level: str = DEFAULT_LOG_LEVEL,
):
    """Command Line Interface to start the DefiRisk Agent server."""
    # Verify an API key is set.
    # Not required if using Vertex AI APIs.
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI") != "TRUE" and not os.getenv(
        "GOOGLE_API_KEY"
    ):
        raise ValueError(
            "GOOGLE_API_KEY environment variable not set and "
            "GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
        )

    async def run_server_async():
        defi_risk_agent_executor = DeFiRiskAgentExecutor()

        request_handler = DefaultRequestHandler(
            agent_executor=defi_risk_agent_executor,
            task_store=InMemoryTaskStore(),
        )

        # Create the A2AServer instance
        a2a_server = A2AStarletteApplication(
            agent_card=get_agent_card(host, port),
            http_handler=request_handler,
        )

        # Get the ASGI app from the A2AServer instance
        asgi_app = a2a_server.build()

        config = uvicorn.Config(
            app=asgi_app,
            host=host,
            port=port,
            log_level=log_level.lower(),
            lifespan="auto",
        )

        uvicorn_server = uvicorn.Server(config)

        print(
            f"Starting Uvicorn server at http://{host}:{port} with log-level {log_level}..."
        )
        try:
            await uvicorn_server.serve()
        except KeyboardInterrupt:
            print("Server shutdown requested (KeyboardInterrupt).")
        finally:
            print("Uvicorn server has stopped.")

    try:
        asyncio.run(run_server_async())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            print(
                "Critical Error: Attempted to nest asyncio.run(). This should have been prevented.",
                file=sys.stderr,
            )
        else:
            print(f"RuntimeError in main: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred in main: {e}", file=sys.stderr)
        sys.exit(1)


def get_agent_card(host: str, port: int):
    """Returns the Agent Card for the DeFi Risk Assessment Agent."""
    capabilities = AgentCapabilities(streaming=True, push_notifications=True)

    # Skill 1: Token Risk Analysis
    risk_analysis_skill = AgentSkill(
        id="token_risk_analysis",
        name="DeFi Token Risk Analysis",
        description="Analyzes cryptocurrency tokens for rug-pull risk using security metrics, holder distribution, liquidity, and trading patterns",
        tags=["defi", "risk-assessment", "rug-pull-detection", "token-security"],
        examples=[
            "Analyze this token for risk: So11111111111111111111111111111111111111112",
            "Check the rug-pull risk for token EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "Is this token safe? EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        ],
    )

    # Skill 2: Holder Distribution Analysis
    holder_analysis_skill = AgentSkill(
        id="holder_analysis",
        name="Holder Distribution Analysis",
        description="Analyzes token holder concentration and distribution patterns to identify whale risks and potential rug-pull indicators",
        tags=["defi", "holders", "concentration", "whale-analysis"],
        examples=[
            "Show me the top holders for this token: So11111111111111111111111111111111111111112",
            "What's the holder concentration for DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263?",
        ],
    )

    # Skill 3: Trending Tokens
    trending_skill = AgentSkill(
        id="trending_tokens",
        name="Trending Tokens Discovery",
        description="Identifies currently trending tokens on Solana based on price change and trading volume",
        tags=["defi", "trending", "discovery", "market-analysis"],
        examples=[
            "What are the trending tokens right now?",
            "Show me top trending tokens on Solana",
        ],
    )

    app_url = os.environ.get("APP_URL", f"http://{host}:{port}")

    return AgentCard(
        name="DeFi Risk Assessment Agent",
        description="AI-powered agent that analyzes cryptocurrency tokens for rug-pull risk using Cambrian DeFi APIs and Google Gemini",
        url=app_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=capabilities,
        skills=[risk_analysis_skill, holder_analysis_skill, trending_skill],
    )


@click.command()
@click.option(
    "--host",
    "host",
    default=DEFAULT_HOST,
    help="Hostname to bind the server to.",
)
@click.option(
    "--port",
    "port",
    default=DEFAULT_PORT,
    type=int,
    help="Port to bind the server to.",
)
@click.option(
    "--log-level",
    "log_level",
    default=DEFAULT_LOG_LEVEL,
    help="Uvicorn log level.",
)
def cli(host: str, port: int, log_level: str):
    main(host, port, log_level)


if __name__ == "__main__":
    main()
