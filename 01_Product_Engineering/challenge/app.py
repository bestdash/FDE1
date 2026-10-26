"""The server.

`gradio.Server` is a FastAPI app with Gradio's API engine bolted in. You get
queueing, streaming, and MCP for free, but you bring your own frontend. That
split is the point: the API is the product, the UI is disposable.
"""

import os
import re
from pathlib import Path

from fastapi.responses import HTMLResponse
from gradio import Server


from schema import Request, ContractAnswer, build_prompt, route_request, solve
from llm import stream_reply
from retrieval import run_agent, RAG_TOOLS, RAG_FUNCS, chunks, WIKI_INDEX
CITATION = re.compile(r"\[(SYN-[^\]]+)\]")        # finds [SYN-12.md#Order.md] in the text
KNOWN_IDS = {s["id"] for s in chunks}         # every section id that really exists

app = Server()

FRONTEND = Path(__file__).parent / "frontend" / "index.html"


# --- The API -----------------------------------------------------------------
# The `-> str` return annotation is REQUIRED. Without it Gradio infers zero
# output components and silently returns nothing. Ask us how we know.


@app.api(name="chat")
def chat(message: str, history: list | None = None) -> str:
    """Stream a reply to one user message."""
    yield from stream_reply(message, history)


@app.api(name="draft_message_for_renew_or_terminate")
def draft_message_for_renew_or_terminate(
    decision: str,
    autorenew_date: str,
    end_date: str,
    today: str,
    owner_status: str,
    file_exists: bool,
) -> str:
    """Draft the next message for one contract after the owner's decision.

    decision is "renew" or "terminate"; owner_status is "active" or "left".
    Dates are text in YYYY-MM-DD format (e.g. "2026-11-15"). An empty
    autorenew_date means the contract has no auto-renewal clause.
    Returns one text with the message type, the act-by date and the draft.
    Drafts only: sends nothing to the vendor or anyone else.
    """
    request = Request(
        decision=decision,
        autorenew_date=autorenew_date or None,   # "" becomes None
        end_date=end_date,
        today=today,
        owner_status=owner_status,
        file_exists=file_exists,
    )
    response = solve(request)
    act_by = response.act_by.isoformat() if response.act_by else "none"
    return (
        f"message_type: {response.message_type}\n"
        f"act_by: {act_by}\n"
        f"\n"
        f"{response.message}"
    )


@app.api(name="show_prompt_for_renew_or_terminate")
def show_prompt_for_renew_or_terminate(
    decision: str,
    autorenew_date: str,
    end_date: str,
    today: str,
    owner_status: str,
    file_exists: bool,
) -> str:
    """Return the exact prompt the draft endpoint sends to the model.

    Same arguments as draft_message_for_renew_or_terminate. Makes no model
    call: routing and prompt building are plain code, so this is instant and
    free. Read-only, for checking a draft and for pasting the prompt elsewhere.
    """
    request = Request(
        decision=decision,
        autorenew_date=autorenew_date or None,   # "" becomes None
        end_date=end_date,
        today=today,
        owner_status=owner_status,
        file_exists=file_exists,
    )
    message_type, _ = route_request(request)
    return build_prompt(request, message_type)

# --- Retrieval from the documents ------------------------------------------------------------

@app.api(name="answer_contract_question")
def answer_contract_question(question: str) -> str:

    """ Answer one question about our contracts, asked in plain words.
    Searches the contract documents and answers only from what it finds.
    Returns the answer with [file#section] citations inline, then a last line
    "sources: <file#section>, ..." or "sources: none". 
    A "warning:" line lists citations that match no document section.
    If the contracts do not cover the question, it says so, names the document
    that seems missing, and suggests asking the vendor for the last signed copy.
    Dates computed from stated terms (for example start date plus term) come
    with the terms used: check them before acting on a deadline.
    Read-only: sends nothing, writes nothing, never guesses a figure."""

    result = run_agent(question, RAG_TOOLS, RAG_FUNCS)

    if result["stopped"] != "answer":                     # the loop ran out of turns
        reply = ContractAnswer(answer="I searched the contracts and found no answer. Either they do not cover "
                                "this topic, or the document that covers it is missing: if you think it is missing, "
                                "ask the vendor for the last signed copy of the relevant terms.", sources=[])
    else:
        cited = CITATION.findall(result["answer"])        # ["SYN-04-order.md#Terms", "SYN-04-order.md#Order"..."]
        unique = list(dict.fromkeys(cited))               # drop repeats, keep the order
        sources = [s for s in unique if s in KNOWN_IDS]        # real sections only
        unknown = [s for s in unique if s not in KNOWN_IDS]    # cited, but no such section
        reply = ContractAnswer(answer=result["answer"], sources=sources, unknown_citations=unknown)

    text = reply.answer + "\n\nsources: " + (", ".join(reply.sources) or "none")
    if reply.unknown_citations:                                # an empty list counts as False
        text += "\nwarning: cited but not found: " + ", ".join(reply.unknown_citations)
    return text

# --- The frontend ------------------------------------------------------------
# Defining a route at "/" replaces Gradio's default UI with ours.

@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return FRONTEND.read_text(encoding="utf-8")


def contracts_from_index(index_md: str) -> list[dict]:
    """Group the rows of the index.md table by contract, in file order."""
    rows = [line for line in index_md.splitlines() if line.startswith("|")]
    header = [cell.strip() for cell in rows[0].strip("|").split("|")]
    col = {name: i for i, name in enumerate(header)}
    grouped = {}                                      # dict keeps the file order
    for line in rows[2:]:                             # skip the header and the --- row
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        contract = cells[col["Contract"]]
        entry = grouped.setdefault(contract, {"contract": contract, "vendor": cells[col["Vendor"]], "documents": []})
        entry["documents"].append(cells[col["Document"]])
    return list(grouped.values())


@app.get("/contracts")
def contracts() -> list[dict]:
    """The contracts in the demo corpus, for the page's side table."""
    # Read-only: parses the index text retrieval.py already loaded, writes nothing.
    return contracts_from_index(WIKI_INDEX)


@app.get("/health")
def health() -> dict:
    """Your future ops team will thank you. Load balancers need this."""
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "gpt-4.1-mini")}


if __name__ == "__main__":
    # 0.0.0.0 so the container is reachable from the host. On your laptop this
    # is fine. On a firm network, "reachable from where, exactly?" is the
    # question this challenge wants you to go ask.
    #
    # Read the port rather than hardcoding it, so a machine that already has
    # something on 7860 can move this one without editing code.
    port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    # Gradio announces the address it BOUND to, which is 0.0.0.0 -- not an
    # address a browser can open. Windows rejects it outright; macOS and Linux
    # quietly redirect it to localhost, which is why it looks fine on some
    # machines and broken on others. Print the one that always works.
    print(f"\n  Open http://localhost:{port} in your browser\n", flush=True)
    app.launch(server_name="0.0.0.0", server_port=port)
