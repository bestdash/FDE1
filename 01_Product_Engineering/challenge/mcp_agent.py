"""Implementation two of answer_contract_question (TC5 Step 3): the same loop,
reaching search_chunks through the MCP server in its own process (stdio).
Read-only: it searches the synthetic contracts and writes nothing.
"""

import json
import time
from pathlib import Path

from fastmcp import Client
from fastmcp.client import PythonStdioTransport

from retrieval import SYSTEM, ask_model, returned_ids   # same prompt and model call as implementation one

SERVER_FILE = Path(__file__).parent / "contracts_mcp_server.py"


def openai_tools(mcp_tools) -> list[dict]:
    """MCP tool listings in the shape the chat API expects."""
    return [{"type": "function", "function": {"name": t.name, "description": t.description or "",
             "parameters": t.input_schema}} for t in mcp_tools]


async def dispatch(client, name: str, arguments: str) -> str:
    """Run one tool call through the MCP client. Failures come back as text for the model, never raised."""
    try:
        args = json.loads(arguments or "{}")
    except ValueError as error:
        return f"arguments were not a JSON object: {error}"
    if not isinstance(args, dict):
        return f"arguments were not a JSON object: got {type(args).__name__}"
    result = await client.call_tool(name, args, raise_on_error=False)
    text = "\n".join(getattr(block, "text", "") for block in result.content)
    if result.is_error and text.startswith("Unknown tool"):   # say what is wrong AND what is right
        text += ". Available tools: " + ", ".join(t.name for t in await client.list_tools())
    return text

async def run_agent_mcp(question, client, max_turns=6):

    tools = openai_tools(await client.list_tools())
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    trace, chars = [], 0
    tokens = {"tokens_in": 0, "tokens_out": 0}  # summed over every model call for this question
    started = time.perf_counter()
    for _ in range(max_turns):
        response = ask_model(messages, tools)
        usage = getattr(response, "usage", None)
        tokens["tokens_in"] += getattr(usage, "prompt_tokens", 0) or 0
        tokens["tokens_out"] += getattr(usage, "completion_tokens", 0) or 0
        msg = response.choices[0].message
        calls = msg.tool_calls or []
        if not calls:
            return {"answer": (msg.content or "").strip(), "trace": trace, "evidence_chars": chars,
                    "latency_s": time.perf_counter() - started, "stopped": "answer", **tokens}
        shaped = [{"id": call.id, "type": "function", "function": {"name": call.function.name, "arguments": call.function.arguments}} for call in calls]
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": shaped})
        for call in shaped:
            name = call["function"]["name"]
            args = {}   # set before the try: bad JSON must not log the previous call's args
            try:
                args = json.loads(call["function"]["arguments"] or "{}")
            except ValueError:
                args = {}
            if not isinstance(args, dict):
                args = {}    
            result = await dispatch(client, name, call["function"]["arguments"])   # the one call
            chars += len(result)
            trace.append({"tool": name, "args": args, "chars": len(result), "ids": returned_ids(name, args, result)})
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return {"answer": "(max turns reached)", "trace": trace, "evidence_chars": chars,
            "latency_s": time.perf_counter() - started, "stopped": "max_turns", **tokens}

async def answer_via_mcp(question: str) -> dict:
    """Implementation two: start the server as a child process, then run the same loop through it."""
    async with Client(PythonStdioTransport(SERVER_FILE, keep_alive=False)) as client:
        return await run_agent_mcp(question, client)

if __name__ == "__main__":
    import asyncio
    import sys
    started = time.perf_counter()
    result = asyncio.run(answer_via_mcp(sys.argv[1]))
    print(result["answer"], "\n")
    print("tool calls:", [(step["tool"], step["args"].get("query") or step["args"].get("vendor")) for step in result["trace"]])
    print(f"tokens in {result['tokens_in']}, out {result['tokens_out']}; loop {result['latency_s']:.1f} s; "
          f"end to end with process start {time.perf_counter() - started:.1f} s")