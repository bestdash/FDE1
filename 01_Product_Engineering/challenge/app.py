"""The server.

`gradio.Server` is a FastAPI app with Gradio's API engine bolted in. You get
queueing, streaming, and MCP for free, but you bring your own frontend. That
split is the point: the API is the product, the UI is disposable.
"""

import os
from pathlib import Path

from fastapi.responses import HTMLResponse
from gradio import Server


from schema import Request, build_prompt, route_request, solve
from llm import stream_reply

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


# --- The frontend ------------------------------------------------------------
# Defining a route at "/" replaces Gradio's default UI with ours.

@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return FRONTEND.read_text(encoding="utf-8")


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
