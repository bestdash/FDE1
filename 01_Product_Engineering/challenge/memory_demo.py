"""TC7: ask the agent one question and show which tools it used.

Run from the repo root, memory on and off:
    uv run python 01_Product_Engineering/challenge/memory_demo.py
    MEMORY=off uv run python 01_Product_Engineering/challenge/memory_demo.py
"""
import sys
import retrieval

question = " ".join(sys.argv[1:]) or "When does the Vendor10 contract end?"
result = retrieval.run_agent(question, retrieval.RAG_TOOLS, retrieval.RAG_FUNCS)

print("memory:", "on" if retrieval.MEMORY_ON else "off")
print("question:", question)
#print("tools used:", [step["tool"] for step in result["trace"]])
print("tools used:", [(step["tool"], step["args"]) for step in result["trace"]])
print("tokens in:", result["tokens_in"], " tokens out:", result["tokens_out"])
print()
print(result["answer"])