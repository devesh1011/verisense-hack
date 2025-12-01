"""Quick test of new Rugcheck tool."""

import asyncio
from src.tools import analyze_token_with_rugcheck


async def test():
    # PUMP token
    result = await analyze_token_with_rugcheck.ainvoke(
        {"token_address": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn"}
    )
    print("Rugcheck Analysis:")
    import json

    print(json.dumps(result, indent=2))


asyncio.run(test())
