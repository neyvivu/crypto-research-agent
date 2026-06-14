"""MCP server exposing crypto-research tools over the Model Context Protocol.

Run standalone to inspect:  python mcp_server.py
The agent (agent.py) launches this automatically over stdio.
"""
from mcp.server.fastmcp import FastMCP
import tools

mcp = FastMCP("crypto-research")


@mcp.tool()
def get_price(coin_id: str) -> dict:
    """Get the live USD price and 24h % change for a coin.

    coin_id: a CoinGecko id such as 'bitcoin', 'ethereum', or 'solana'.
    """
    return tools.get_price(coin_id)


@mcp.tool()
def get_market_news(query: str = "crypto", limit: int = 5) -> dict:
    """Get recent crypto headlines matching a query, each scored for sentiment.

    query: keyword to filter headlines (use 'crypto' for the latest overall).
    """
    return tools.get_market_news(query, limit)


@mcp.tool()
def search_knowledge(query: str, k: int = 3) -> dict:
    """Semantic RAG search over the local crypto knowledge base (BTC, ETH, DeFi)."""
    return tools.search_knowledge(query, k)


if __name__ == "__main__":
    mcp.run()
