import asyncio, statistics, time
import agent

CASES = [
    {"q": "What is the current price of Bitcoin in USD?", "must_use": "get_price", "check": lambda a: "$" in a or "usd" in a.lower()},
    {"q": "What is Ethereum's 24h price change?", "must_use": "get_price", "check": lambda a: "%" in a},
    {"q": "What is the recent news sentiment around Bitcoin?", "must_use": "get_market_news", "check": lambda a: "sentiment" in a.lower() or "positive" in a.lower() or "negative" in a.lower()},
    {"q": "Explain what an automated market maker is and what impermanent loss means.", "must_use": "search_knowledge", "check": lambda a: "liquidity" in a.lower() and "impermanent" in a.lower()},
    {"q": "What changed for Ethereum issuance after the Merge?", "must_use": "search_knowledge", "check": lambda a: "stake" in a.lower() or "proof-of-stake" in a.lower()},
    {"q": "Given Solana's price and latest sentiment, give a balanced read.", "must_use": "get_price", "check": lambda a: "sol" in a.lower()},
]

async def main():
    rows, latencies = [], []
    print(f"Running {len(CASES)} cases...\n")
    for i, c in enumerate(CASES):
        if i: 
            print("   (waiting 15s to respect free-tier rate limit...)")
            time.sleep(15)
        res = await agent.run(c["q"], verbose=False)
        ans = res["answer"]
        used = c["must_use"] in res["tool_calls"]
        ok = used and c["check"](ans)
        latencies.append(res["latency_s"])
        rows.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] used_{c['must_use']}={used}  {res['latency_s']:>5}s  ::  {c['q']}")
    passed = sum(rows)
    print("\n" + "-"*60)
    print(f"Accuracy:     {passed}/{len(rows)}  ({100*passed/len(rows):.0f}%)")
    print(f"Avg latency:  {statistics.mean(latencies):.2f}s")
    print(f"Max latency:  {max(latencies):.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
