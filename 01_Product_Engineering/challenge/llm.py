"""The model call.

One function, one job: take a conversation, stream back the assistant's reply.

Everything provider-specific lives in environment variables, so switching from
OpenAI to Azure to a self-hosted model is a config change, not a code change.
That property matters more than it looks like it does right now -- see the
"Where does this live?" section of the README.
"""

import json
import os
from pathlib import Path

from litellm import completion, token_counter

def _load_dotenv() -> None:
    """Read the repo root .env into os.environ, before the settings below are read.

    Local runs only. In Docker there is no .env file (keys arrive via --env-file),
    so this does nothing. A value already set in the environment always wins.
    """
    parents = Path(__file__).resolve().parents
    if len(parents) < 3:          # in Docker, /app/llm.py has no repo root above it
        return
    env = parents[2] / ".env"     # challenge/ -> 01_Product_Engineering/ -> FDE1/
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if sep and not line.lstrip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


# LiteLLM picks the provider from the model string:
#   "gpt-4.1-mini"                    -> OpenAI
#   "azure/my-deployment"             -> Azure OpenAI
#   "anthropic/claude-sonnet-5"       -> Anthropic
#   "ollama/llama3.2"                 -> a model running on your laptop
#   "openai/my-model" + LLM_API_BASE  -> any OpenAI-compatible server (vLLM, LM Studio, ...)
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
API_BASE = os.getenv("LLM_API_BASE")  # only needed for self-hosted / gateway endpoints
EXTRA_HEADERS = json.loads(os.getenv("LLM_EXTRA_HEADERS") or "{}")

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful assistant. Be concise and concrete.",
)


def stream_reply(message: str, history: list[dict] | None = None):
    """Yield the assistant's reply as it arrives, one growing string at a time.

    `history` is a list of {"role": ..., "content": ...} dicts. We rebuild the
    full message list on every turn -- the model is stateless, so the
    conversation only exists because we keep sending it.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history or [])
    messages.append({"role": "user", "content": message})

    kwargs = {"model": MODEL, "messages": messages, "stream": True}
    if API_BASE:
        kwargs["api_base"] = API_BASE
    if EXTRA_HEADERS:
        kwargs["extra_headers"] = EXTRA_HEADERS

    reply = ""
    for chunk in completion(**kwargs):
        piece = chunk.choices[0].delta.content
        if piece:
            reply += piece
            yield reply


def count_tokens(message: str, history: list[dict] | None = None) -> int:
    """Count the tokens a prompt will consume, before sending it.

    Builds the same message list stream_reply sends (system prompt,
    history, new message), so the number reflects what the model will
    actually see, not just the raw text.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history or [])
    messages.append({"role": "user", "content": message})
    return token_counter(model=MODEL, messages=messages)
