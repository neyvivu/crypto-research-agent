"""Raw crypto-native data tools. Pure functions; the MCP server wraps these."""
import requests
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import rag

_VADER = SentimentIntensityAnalyzer()
_NEWS_FEED = "https://cointelegraph.com/rss"


def get_price(coin_id: str) -> dict:
    """Live USD price + 24h change for a CoinGecko coin id (e.g. 'bitcoin', 'ethereum')."""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json().get(coin_id)
        if not data:
            return {"error": f"unknown coin_id '{coin_id}'. Try bitcoin, ethereum, solana."}
        return {
            "coin": coin_id,
            "usd": data["usd"],
            "change_24h_pct": round(data.get("usd_24h_change", 0.0), 2),
        }
    except Exception as e:
        return {"error": f"price lookup failed: {e}"}


def get_market_news(query: str = "crypto", limit: int = 5) -> dict:
    """Recent crypto headlines matching a query, each with a VADER sentiment score (-1..1)."""
    try:
        feed = feedparser.parse(_NEWS_FEED)
        q = query.lower()
        items = []
        for e in feed.entries:
            title = e.get("title", "")
            if q == "crypto" or q in title.lower():
                items.append({
                    "title": title,
                    "sentiment": round(_VADER.polarity_scores(title)["compound"], 3),
                    "link": e.get("link", ""),
                })
            if len(items) >= limit:
                break
        avg = round(sum(i["sentiment"] for i in items) / len(items), 3) if items else 0.0
        return {"query": query, "avg_sentiment": avg, "count": len(items), "headlines": items}
    except Exception as e:
        return {"error": f"news lookup failed: {e}"}


def search_knowledge(query: str, k: int = 3) -> dict:
    """Semantic RAG over the local crypto knowledge base."""
    return {"query": query, "results": rag.search(query, k=k)}
