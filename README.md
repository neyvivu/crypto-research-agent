# Crypto Research Agent

An LLM agent (Gemini) that answers crypto-market questions by reasoning over **tools served
through the Model Context Protocol (MCP)**:

- `get_price` — live price + 24h change (CoinGecko)
- `get_market_news` — recent headlines with VADER sentiment (RSS)
- `search_knowledge` — **semantic RAG** over a local crypto knowledge base

Plus an **evaluation harness** that benchmarks accuracy, tool-use, and latency.

```
            ┌──────────┐   discovers + calls tools   ┌──────────────┐
question →  │ agent.py │ ──────────────────────────▶ │ mcp_server.py│
            │ (Gemini) │ ◀──────── tool results ───── │  (FastMCP)   │
            └──────────┘                              └──────┬───────┘
                                                            │
                                  get_price / get_market_news / search_knowledge
                                                            │
                                       CoinGecko · RSS+VADER · RAG (rag.py)
```

## Get a free Gemini API key (no credit card)
1. Go to https://aistudio.google.com/apikey
2. Sign in with Google → **Create API key** → copy it.
3. Do NOT enable billing on the project — that removes the free tier.

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env        # paste your key: GEMINI_API_KEY=...
```

## Run

```powershell
python rag.py                                  # sanity-check retrieval
python agent.py "Is ETH strong right now?"     # full agent with tool-use over MCP
python eval.py                                  # run the benchmark + metrics
```

## Next steps (to go deeper)
- Add an on-chain tool (gas price, wallet balance) — it auto-appears to the agent.
- Add a real vector DB (Chroma/FAISS) behind rag.py.
- Add adversarial eval cases (prompt injection in a headline) to test robustness.

## Resume bullet (add only after it runs)
> Built a crypto-research LLM agent (Gemini) with tool-use served over the **Model Context
> Protocol (MCP)** — live market data, news-sentiment, and **semantic RAG** over a local
> knowledge base — plus an **evaluation harness** scoring decision accuracy, tool-use, and
> latency across a benchmark suite.
