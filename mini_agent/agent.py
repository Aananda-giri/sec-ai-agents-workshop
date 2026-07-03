"""The teachable agent core: a ReAct loop in ~100 lines.

An Agent is: a running list of messages (memory), an LLM call, and a loop
that executes tool calls until the model stops asking for them.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import re
from typing import Any, Callable, get_type_hints

from litellm import acompletion
from litellm.exceptions import RateLimitError, ServiceUnavailableError, Timeout, APIConnectionError

# Gemini's free tier is rate-limited (as low as 5 requests/minute on
# gemini-2.5-flash) and a ReAct loop can easily burn through that in one
# turn; it also occasionally returns transient 503s under load. Retry with
# the delay the API itself suggests so a live demo doesn't just die on a
# 429 — enabling billing on the Gemini project removes the rate-limit
# ceiling almost entirely and costs pennies.
DEFAULT_MODEL = "gemini/gemini-2.5-flash"
_TRANSIENT_ERRORS = (RateLimitError, ServiceUnavailableError, Timeout, APIConnectionError)
_RETRY_DELAY_RE = re.compile(r'"retryDelay":\s*"(\d+)s"')

_TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean"}


def tool_to_schema(func: Callable) -> dict:
    """Turn a plain Python function into an OpenAI/litellm function-calling schema.

    Reads the signature for parameter names/types/defaults and the docstring
    for the description. No decorator required.
    """
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, param in inspect.signature(func).parameters.items():
        json_type = _TYPE_MAP.get(hints.get(name), "string")
        properties[name] = {"type": json_type}
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (inspect.getdoc(func) or "").split("\n\n")[0],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


class Agent:
    """Tool-calling agent with a ReAct (think -> act -> observe) loop."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        tools: list[Callable] | None = None,
        instructions: str = "",
        max_steps: int = 8,
    ):
        self.model = model
        self.instructions = instructions
        self.max_steps = max_steps
        self.tools = {t.__name__: t for t in (tools or [])}
        self.tool_schemas = [tool_to_schema(t) for t in (tools or [])]
        # This list *is* the agent's memory: it persists across run() calls.
        self.messages: list[dict] = []
        if instructions:
            self.messages.append({"role": "system", "content": instructions})

    async def run(self, user_input: str, verbose: bool = True) -> str:
        """Send a message, looping through tool calls until a final reply."""
        self.messages.append({"role": "user", "content": user_input})

        for step in range(self.max_steps):
            response = await self._complete_with_retry(verbose=verbose)
            message = response.choices[0].message
            self.messages.append(message.model_dump())

            if not message.tool_calls:
                if verbose:
                    print(f"[reply] {message.content}")
                return message.content

            for call in message.tool_calls:
                result = self._invoke(call, verbose=verbose)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })

        return "(stopped: max_steps reached)"

    async def _complete_with_retry(self, verbose: bool, max_retries: int = 4):
        """Call the LLM, retrying on rate limits with the API-suggested delay."""
        for attempt in range(max_retries + 1):
            try:
                return await acompletion(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tool_schemas or None,
                    tool_choice="auto" if self.tool_schemas else None,
                )
            except _TRANSIENT_ERRORS as e:
                if attempt == max_retries:
                    raise
                match = _RETRY_DELAY_RE.search(str(e))
                delay = int(match.group(1)) + 1 if match else 2 ** attempt * 3
                if verbose:
                    print(f"[{type(e).__name__}] retrying in {delay}s...")
                await asyncio.sleep(delay)

    def _invoke(self, call, verbose: bool) -> str:
        name = call.function.name
        args = json.loads(call.function.arguments)
        if verbose:
            print(f"[think] calling {name}({args})")

        if name not in self.tools:
            return f"Error: no such tool '{name}'"

        try:
            output = self.tools[name](**args)
        except Exception as e:
            output = f"Error: {e}"

        if verbose:
            print(f"[observe] {output}")
        return str(output)
