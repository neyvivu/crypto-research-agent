"""Crypto research agent (Gemini + MCP tools).

The agent discovers tools from mcp_server.py over MCP, exposes them to Gemini as function
declarations, and runs the tool-use loop itself: Gemini decides which tool to call, the agent
calls it through the MCP session, feeds the result back, and repeats until Gemini answers.
"""
import os
import sys
import time
import asyncio

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = "gemini-2.5-flash"  # free-tier model; no credit card needed
SYSTEM = (
    "You are a disciplined crypto research analyst. Ground every quantitative claim in a tool "
    "call: use get_price for prices, get_market_news for sentiment, and search_knowledge for "
    "concepts. Never invent a price or a statistic. State which tools you used and end with a "
    "short, balanced takeaway. You do not give financial advice."
)

_ALLOWED = {"type", "description", "enum", "properties", "required", "items"}


def _clean_schema(schema):
    """Convert an MCP JSON Schema into the subset Gemini accepts (uppercase types, no extras)."""
    if not isinstance(schema, dict):
        return {"type": "OBJECT", "properties": {}}
    out = {}
    for k, v in schema.items():
        if k not in _ALLOWED:
            continue
        if k == "type" and isinstance(v, str):
            out["type"] = v.upper()
        elif k == "properties" and isinstance(v, dict):
            out["properties"] = {pk: _clean_schema(pv) for pk, pv in v.items()}
        elif k == "items":
            out["items"] = _clean_schema(v)
        else:
            out[k] = v
    if out.get("type") == "OBJECT" and "properties" not in out:
        out["properties"] = {}
    return out


def _build_tools(mcp_tools):
    decls = [
        types.FunctionDeclaration(
            name=t.name,
            description=t.description or "",
            parameters=_clean_schema(t.inputSchema),
        )
        for t in mcp_tools
    ]
    return [types.Tool(function_declarations=decls)]


async def run(question: str, max_turns: int = 8, verbose: bool = True):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Put it in your .env file.")
    client = genai.Client(api_key=api_key)
    server = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    started = time.time()
    tool_calls = []

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = _build_tools((await session.list_tools()).tools)
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM, tools=tools, temperature=0,
            )
            contents = [types.Content(role="user", parts=[types.Part(text=question)])]

            for _ in range(max_turns):
                resp = await client.aio.models.generate_content(
                    model=MODEL, contents=contents, config=config,
                )
                parts = resp.candidates[0].content.parts or []
                calls = [p.function_call for p in parts if getattr(p, "function_call", None)]
                contents.append(resp.candidates[0].content)  # keep the model's turn

                if not calls:
                    answer = "".join(p.text for p in parts if getattr(p, "text", None))
                    return {
                        "answer": answer,
                        "tool_calls": tool_calls,
                        "latency_s": round(time.time() - started, 2),
                    }

                result_parts = []
                for fc in calls:
                    tool_calls.append(fc.name)
                    if verbose:
                        print(f"   -> {fc.name}({dict(fc.args or {})})")
                    out = await session.call_tool(fc.name, dict(fc.args or {}))
                    payload = out.content[0].text if out.content else ""
                    result_parts.append(
                        types.Part.from_function_response(
                            name=fc.name, response={"result": payload}
                        )
                    )
                contents.append(types.Content(role="user", parts=result_parts))

    return {
        "answer": "(stopped: max turns reached)",
        "tool_calls": tool_calls,
        "latency_s": round(time.time() - started, 2),
    }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Is Ethereum looking strong right now? Use its price and 24h move, recent news "
        "sentiment, and explain what drives ETH value from the knowledge base."
    )
    result = asyncio.run(run(question))
    print("\n=== ANSWER ===\n" + result["answer"])
    print(f"\ntools used: {result['tool_calls']} | latency: {result['latency_s']}s")
