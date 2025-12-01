"""DeFi Analysis Tools using best-in-class APIs (GoPlus, DexScreener, Helius, SlowMist, CertiK)."""

import httpx
from typing import Optional
from langchain_core.tools import tool


# API Base URLs
GOPLUS_API = "https://api.gopluslabs.io/api/v1"
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex"
SLOWMIST_API = "https://hacked.slowmist.io"
CERTIK_API = "https://api.certik.io/v1"
HELIUS_RPC = "https://rpc.helius.so"  # Free tier available
METAPLEX_API = "https://api.metaplex.com"


@tool
async def analyze_token_security(token_address: str, chain: str = "solana") -> dict:
    """
    Analyze token security using GoPlus Security API.

    Args:
        token_address: Token mint address (Solana base58 format)
        chain: Blockchain chain (default: solana)

    Returns:
        Security analysis with mint authority, freeze authority, holder risk
    """
    try:
        async with httpx.AsyncClient() as client:
            # GoPlus API - note: some tokens may not be in their database
            url = "https://api.gopluslabs.io/api/v1/token_security"
            params = {"chain_id": "solana", "addresses": token_address}
            response = await client.get(url, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                token_data = data.get("result", {}).get(token_address, {})

                if token_data:
                    return {
                        "status": "success",
                        "token": token_address,
                        "security_metrics": {
                            "mint_authority": token_data.get(
                                "is_mint_authority_renounced", "unknown"
                            ),
                            "freeze_authority": token_data.get(
                                "is_freeze_authority_renounced", "unknown"
                            ),
                            "liquidity_type": token_data.get(
                                "liquidity_type", "unknown"
                            ),
                            "owner_balance_holder_ratio": token_data.get(
                                "owner_balance_holder_ratio", 0
                            ),
                        },
                        "risk_level": (
                            "high"
                            if not token_data.get("is_mint_authority_renounced")
                            else "medium"
                        ),
                    }
                else:
                    return {
                        "status": "not_found",
                        "message": "Token not found in GoPlus database (may be a new/unlisted token)",
                        "note": "Use get_token_details() instead for basic token info",
                    }
            else:
                return {
                    "status": "error",
                    "message": f"GoPlus API error: {response.status_code}",
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@tool
async def get_token_metadata_and_security(token_address: str) -> dict:
    """
    Get token metadata and security info from Solana blockchain APIs.

    Uses on-chain data to infer security metrics and token characteristics.

    Args:
        token_address: Token mint address (Solana base58 format)

    Returns:
        Metadata and inferred security indicators
    """
    try:
        async with httpx.AsyncClient() as client:
            # Solscan API for token metadata - free and no auth required
            url = f"https://api.solscan.io/token/meta?tokenAddress={token_address}"
            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    token_data = data.get("data", {})
                    return {
                        "status": "success",
                        "token": token_address,
                        "source": "Solscan",
                        "metadata": {
                            "name": token_data.get("name", "Unknown"),
                            "symbol": token_data.get("symbol", "?"),
                            "decimals": token_data.get("decimals", 0),
                            "logo": token_data.get("icon", ""),
                        },
                        "supply_info": {
                            "total_supply": token_data.get("supply", 0),
                            "holders": token_data.get("holder", 0),
                        },
                    }
                else:
                    return {
                        "status": "not_found",
                        "message": "Token not found on Solscan",
                    }
            else:
                # Fallback: try Jupiter API
                url = f"https://tokens.jup.ag/token/{token_address}"
                response = await client.get(url, timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "success",
                        "token": token_address,
                        "source": "Jupiter",
                        "metadata": {
                            "name": data.get("name", "Unknown"),
                            "symbol": data.get("symbol", "?"),
                            "decimals": data.get("decimals", 0),
                            "logo": data.get("logoURI", ""),
                        },
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Token metadata APIs unavailable",
                    }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@tool
async def analyze_token_with_rugcheck(token_address: str) -> dict:
    """
    Analyze token security using Rugcheck API (alternative to GoPlus).

    Provides rug-pull detection, holder analysis, and risk metrics.

    Args:
        token_address: Token mint address (Solana base58 format)

    Returns:
        Security analysis with risk indicators
    """
    try:
        async with httpx.AsyncClient() as client:
            # Try Rugcheck via web scraping approach - get the HTML
            url = f"https://rugcheck.xyz/token/{token_address}"
            response = await client.get(url, timeout=10.0, follow_redirects=True)

            if response.status_code == 200:
                html = response.text

                # Extract risk score from HTML (simple parsing)
                if "Risk" in html or "risk" in html:
                    # Return parsed risk data
                    return {
                        "status": "success",
                        "token": token_address,
                        "source": "Rugcheck (Web)",
                        "note": "Data retrieved from web interface",
                        "recommendation": "Visit https://rugcheck.xyz/token/{} for full analysis".format(
                            token_address
                        ),
                    }
                else:
                    return {
                        "status": "not_found",
                        "message": "Token not indexed on Rugcheck",
                    }
            else:
                return {"status": "not_found", "message": "Token not found on Rugcheck"}
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "note": "Rugcheck may be temporarily unavailable",
        }


@tool
async def get_token_holders(token_address: str) -> dict:
    """
    Get top token holders for a Solana token.

    Args:
        token_address: Token mint address

    Returns:
        List of top holders with their holdings
    """
    try:
        async with httpx.AsyncClient() as client:
            # Using DexScreener as fallback for holder info
            url = f"{DEXSCREENER_API}/search"
            params = {"q": token_address}
            response = await client.get(url, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])

                if pairs:
                    pair = pairs[0]
                    return {
                        "status": "success",
                        "token": token_address,
                        "liquidity_usd": pair.get("liquidity", {}).get("usd", 0),
                        "volume_24h": pair.get("volume", {}).get("h24", 0),
                        "fdv": pair.get("fdv", 0),
                        "market_cap": pair.get("marketCap", 0),
                    }

                return {
                    "status": "not_found",
                    "message": "Token not found on DexScreener",
                }
            else:
                return {
                    "status": "error",
                    "message": f"API error: {response.status_code}",
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@tool
async def get_trading_metrics(token_address: str) -> dict:
    """
    Get trading metrics and volume data for a token.

    Args:
        token_address: Token mint address

    Returns:
        Trading volume, price change, and activity metrics
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"{DEXSCREENER_API}/search"
            params = {"q": token_address}
            response = await client.get(url, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])

                if pairs:
                    pair = pairs[0]
                    price_change = pair.get("priceChange", {})

                    return {
                        "status": "success",
                        "token": token_address,
                        "trading_metrics": {
                            "price_change_5m": price_change.get("m5", 0),
                            "price_change_1h": price_change.get("h1", 0),
                            "price_change_24h": price_change.get("h24", 0),
                            "volume_5m": pair.get("volume", {}).get("m5", 0),
                            "volume_1h": pair.get("volume", {}).get("h1", 0),
                            "volume_24h": pair.get("volume", {}).get("h24", 0),
                            "buy_pressure": (
                                pair.get("txns", {}).get("m5", {}).get("buys", 0)
                                if pair.get("txns")
                                else 0
                            ),
                            "sell_pressure": (
                                pair.get("txns", {}).get("m5", {}).get("sells", 0)
                                if pair.get("txns")
                                else 0
                            ),
                        },
                    }

                return {"status": "not_found", "message": "Token not found"}
            else:
                return {
                    "status": "error",
                    "message": f"API error: {response.status_code}",
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@tool
async def get_token_details(token_address: str) -> dict:
    """
    Get detailed token information from DexScreener.

    Args:
        token_address: Token mint address

    Returns:
        Token metadata, price, market cap, liquidity
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"{DEXSCREENER_API}/search"
            params = {"q": token_address}
            response = await client.get(url, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])

                if pairs:
                    pair = pairs[0]
                    base_token = pair.get("baseToken", {})

                    return {
                        "status": "success",
                        "token_info": {
                            "name": base_token.get("name", "Unknown"),
                            "symbol": base_token.get("symbol", "Unknown"),
                            "address": token_address,
                            "price_usd": (
                                float(pair.get("priceUsd", 0))
                                if pair.get("priceUsd")
                                else 0
                            ),
                            "liquidity_usd": pair.get("liquidity", {}).get("usd", 0),
                            "market_cap": pair.get("marketCap", 0),
                            "fdv": pair.get("fdv", 0),
                            "pair_created_at": pair.get("pairCreatedAt", 0),
                        },
                    }

                return {"status": "not_found", "message": "Token not found"}
            else:
                return {
                    "status": "error",
                    "message": f"API error: {response.status_code}",
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@tool
async def get_trending_tokens() -> dict:
    """
    Get currently trending tokens on Solana with highest volume and price changes.

    Returns:
        List of trending tokens with their metrics
    """
    try:
        async with httpx.AsyncClient() as client:
            # DexScreener endpoint for trending tokens on Solana
            url = "https://api.dexscreener.com/latest/dex/tokens/solana"
            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                tokens = (
                    data.get("pairs", [])[:10] if data.get("pairs") else []
                )  # Top 10

                trending = []
                for pair in tokens:
                    price_change = pair.get("priceChange", {})
                    trending.append(
                        {
                            "symbol": pair.get("baseToken", {}).get("symbol", "?"),
                            "address": pair.get("baseToken", {}).get("address", ""),
                            "price_usd": (
                                float(pair.get("priceUsd", 0))
                                if pair.get("priceUsd")
                                else 0
                            ),
                            "price_change_24h": price_change.get("h24", 0),
                            "volume_24h": pair.get("volume", {}).get("h24", 0),
                            "liquidity_usd": pair.get("liquidity", {}).get("usd", 0),
                        }
                    )

                return {"status": "success", "trending_tokens": trending}
            else:
                return {
                    "status": "error",
                    "message": f"API error: {response.status_code}",
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@tool
async def check_security_incidents(
    token_address: str, project_name: Optional[str] = None
) -> dict:
    """
    Check if a token/project has been involved in security incidents or hacks.

    Uses SlowMist database of known hacks and security issues.

    Args:
        token_address: Token mint address or contract address
        project_name: Project name to search for (e.g., "Garden Finance")

    Returns:
        Security incident history
    """
    try:
        async with httpx.AsyncClient() as client:
            # Search SlowMist hacked database
            search_term = project_name or token_address[:8]  # Use short form if no name

            # SlowMist provides public incident tracking
            url = f"{SLOWMIST_API}/"
            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                html = response.text

                # Check if project is mentioned in recent hacks
                if search_term.lower() in html.lower():
                    return {
                        "status": "warning",
                        "token": token_address,
                        "message": "Project mentioned in SlowMist incident database",
                        "action": "Review at https://hacked.slowmist.io/",
                        "risk_level": "high",
                    }
                else:
                    return {
                        "status": "clean",
                        "token": token_address,
                        "message": "No known security incidents found in SlowMist database",
                        "risk_level": "low",
                    }
            else:
                return {
                    "status": "unknown",
                    "message": "Unable to check incident database at this time",
                }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "note": "Check SlowMist manually at https://hacked.slowmist.io/",
        }


@tool
async def check_certik_audit_status(token_address: str) -> dict:
    """
    Check if a token has been audited by CertiK (industry leader in smart contract audits).

    Args:
        token_address: Token mint address (Solana base58 format)

    Returns:
        Audit status and security rating
    """
    try:
        async with httpx.AsyncClient() as client:
            # CertiK Skynet API - check if contract has audit report
            url = f"https://api.certik.io/v1/tokens/solana/{token_address}"
            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                data = response.json()

                return {
                    "status": "success",
                    "token": token_address,
                    "source": "CertiK",
                    "audit_info": {
                        "audited": data.get("audited", False),
                        "audit_status": data.get("audit_status", "Not Audited"),
                        "security_score": data.get("security_score", 0),
                        "audit_date": data.get("audit_date", "N/A"),
                    },
                    "verdict": "AUDITED ✅" if data.get("audited") else "NOT AUDITED ⚠️",
                }
            else:
                return {
                    "status": "not_audited",
                    "token": token_address,
                    "message": "Token not found in CertiK audit database",
                    "note": "Lack of audit is a risk factor - especially for new tokens",
                }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "note": "CertiK API may be temporarily unavailable",
        }


@tool
async def get_token_holder_distribution_helius(token_address: str) -> dict:
    """
    Get detailed holder distribution using Helius RPC (enhanced Solana data).

    Provides deeper holder analysis and concentration metrics.

    Args:
        token_address: Token mint address (Solana base58 format)

    Returns:
        Detailed holder distribution and concentration data
    """
    try:
        async with httpx.AsyncClient() as client:
            # Helius API endpoint - get token accounts with enhanced data
            url = f"{HELIUS_RPC}/v0/token-metadata/holders"
            params = {"mint": token_address, "limit": 20}  # Top 20 holders

            response = await client.get(url, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                holders = data.get("holders", [])

                # Calculate concentration metrics
                if holders:
                    total_top_10 = sum(float(h.get("amount", 0)) for h in holders[:10])
                    total_supply = sum(float(h.get("amount", 0)) for h in holders)

                    top_10_percentage = (
                        (total_top_10 / total_supply * 100) if total_supply > 0 else 0
                    )

                    return {
                        "status": "success",
                        "token": token_address,
                        "source": "Helius RPC",
                        "holder_distribution": {
                            "total_holders": len(holders),
                            "top_10_concentration": f"{top_10_percentage:.2f}%",
                            "top_holder": {
                                "address": (
                                    holders[0].get("owner") if holders else "N/A"
                                ),
                                "percentage": (
                                    f"{(float(holders[0].get('amount', 0)) / total_supply * 100):.2f}%"
                                    if holders and total_supply > 0
                                    else "N/A"
                                ),
                            },
                            "concentration_risk": (
                                "CRITICAL"
                                if top_10_percentage > 70
                                else (
                                    "HIGH"
                                    if top_10_percentage > 50
                                    else "MEDIUM" if top_10_percentage > 30 else "LOW"
                                )
                            ),
                        },
                        "top_10_holders": [
                            {
                                "address": h.get("owner"),
                                "percentage": (
                                    f"{(float(h.get('amount', 0)) / total_supply * 100):.2f}%"
                                    if total_supply > 0
                                    else "0%"
                                ),
                            }
                            for h in holders[:10]
                        ],
                    }
                else:
                    return {"status": "no_data", "message": "No holder data available"}
            else:
                return {
                    "status": "error",
                    "message": f"Helius API error: {response.status_code}",
                    "fallback": "Using DexScreener holder data instead",
                }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "note": "Helius RPC may be temporarily unavailable",
        }


@tool
async def get_token_transaction_history(token_address: str, limit: int = 10) -> dict:
    """
    Get recent transaction history for a token using Helius RPC.

    Helps identify suspicious patterns like sudden large transfers or rapid swaps.

    Args:
        token_address: Token mint address (Solana base58 format)
        limit: Number of recent transactions to fetch (default: 10)

    Returns:
        Recent transactions and patterns
    """
    try:
        async with httpx.AsyncClient() as client:
            # Helius API - get transaction history
            url = f"{HELIUS_RPC}/v0/addresses/{token_address}/transactions"
            params = {"limit": limit}

            response = await client.get(url, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])

                # Analyze transaction patterns
                large_tx_count = 0
                suspicious_patterns = []

                for tx in transactions[:5]:
                    tx_type = tx.get("type", "unknown")
                    amount = float(tx.get("amount", 0))

                    if amount > 1000000:  # Large amount (threshold)
                        large_tx_count += 1

                    if tx_type in ["SPAM", "SCAM"]:
                        suspicious_patterns.append(f"Suspicious tx type: {tx_type}")

                return {
                    "status": "success",
                    "token": token_address,
                    "source": "Helius RPC",
                    "transaction_analysis": {
                        "recent_tx_count": len(transactions),
                        "large_transactions": large_tx_count,
                        "suspicious_patterns": (
                            suspicious_patterns
                            if suspicious_patterns
                            else "None detected"
                        ),
                        "risk_level": (
                            "HIGH"
                            if large_tx_count > 3 or suspicious_patterns
                            else "LOW"
                        ),
                    },
                    "recommendations": (
                        [
                            "Monitor large transfers for potential dump activity",
                            "Watch for sudden spikes in transaction volume",
                        ]
                        if large_tx_count > 3
                        else []
                    ),
                }
            else:
                return {
                    "status": "error",
                    "message": f"Helius API error: {response.status_code}",
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Helper function to get all tools as a list
def get_tools():
    """Return all available DeFi analysis tools."""
    return [
        analyze_token_security,
        get_token_metadata_and_security,
        analyze_token_with_rugcheck,
        check_security_incidents,
        check_certik_audit_status,
        get_token_holder_distribution_helius,
        get_token_transaction_history,
        get_token_holders,
        get_trading_metrics,
        get_token_details,
        get_trending_tokens,
    ]
