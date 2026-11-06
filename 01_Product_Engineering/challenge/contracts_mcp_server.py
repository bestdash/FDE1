"""The contract search as an MCP server, in a process of its own (TC5 Step 3).

Run from 01_Product_Engineering/challenge (it speaks MCP over stdio):
    uv run python contracts_mcp_server.py
Read-only: it serves search over the synthetic contracts and writes nothing.
Never print to stdout in this file: stdout carries the MCP messages.
"""

from fastmcp import FastMCP

from retrieval import RAG_FUNCS, RAG_TOOLS

# The same words the model reads in implementation one (RAG_TOOLS in retrieval.py).
DESCRIPTIONS = {tool["function"]["name"]: tool["function"]["description"] for tool in RAG_TOOLS}


def contracts_server(funcs=RAG_FUNCS, counter=None) -> FastMCP:
    """Every function in funcs becomes one MCP tool. funcs is an argument, so a
    test or Step 4 can pass a counting version without patching anything."""
    server = FastMCP("contracts", middleware=[counter] if counter else None)
    for name, func in funcs.items():
        server.tool(func, name=name, description=DESCRIPTIONS.get(name, func.__doc__ or ""))
    return server


if __name__ == "__main__":
    contracts_server().run(show_banner=False)  # stdio by default