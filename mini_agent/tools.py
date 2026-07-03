"""Tools for the workshop agent. Plain functions — no decorator needed.

`tool_to_schema` in agent.py reads each function's signature and docstring
to build its schema automatically.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

GENERATED_TOOLS_DIR = Path(__file__).resolve().parent.parent / "generated_tools"


def calculator(operator: str, a: float, b: float) -> float:
    """Perform basic arithmetic. operator is one of: add, subtract, multiply, divide."""
    if operator == "add":
        return a + b
    if operator == "subtract":
        return a - b
    if operator == "multiply":
        return a * b
    if operator == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    raise ValueError(f"Unknown operator: {operator}")


def web_search(query: str) -> str:
    """Search the web for current information and return a summary of results."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return (
            "Error: TAVILY_API_KEY is not set. Get a free key at "
            "https://app.tavily.com and add it to .env to enable web search."
        )
    try:
        from tavily import TavilyClient
    except ImportError:
        return "Error: tavily-python is not installed. Run: pip install tavily-python"

    try:
        response = TavilyClient(api_key=api_key).search(query=query, max_results=5)
        results = response.get("results", [])
        if not results:
            return "No results found."
        return "\n\n".join(f"{r['title']}: {r['content']}" for r in results)
    except Exception as e:
        return f"Search error: {e}"


def execute_python(code: str, timeout: int = 10) -> str:
    """Run Python code in a subprocess and return its stdout/stderr.

    Print whatever you want to see — the return value of the last
    expression is NOT captured, only what's printed.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"Error: execution timed out after {timeout}s"

    parts = []
    if result.stdout:
        parts.append(result.stdout.rstrip("\n"))
    if result.stderr:
        parts.append(f"STDERR:\n{result.stderr.rstrip(chr(10))}")
    return "\n".join(parts) if parts else "(no output — did you forget to print()?)"


_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def write_tool(name: str, code: str, description: str) -> str:
    """Write yourself a brand-new tool when no existing tool can do the job.

    `code` must define exactly one top-level Python function named `name`,
    with type hints and a docstring. The tool becomes usable after the
    presenter reloads tools with load_generated_tools().
    """
    if not _NAME_RE.match(name):
        return f"Error: '{name}' is not a valid Python identifier"
    if f"def {name}(" not in code:
        return f"Error: code must define a top-level function named '{name}'"

    GENERATED_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_TOOLS_DIR / f"{name}.py"
    path.write_text(f'"""{description}"""\n\n{code.strip()}\n', encoding="utf-8")
    return f"Wrote tool '{name}' to {path}. Ask the presenter to reload tools."


def load_generated_tools(tools_dir: Path | str = GENERATED_TOOLS_DIR) -> list:
    """Import every .py file in tools_dir and return its top-level function."""
    directory = Path(tools_dir)
    if not directory.exists():
        return []

    loaded = []
    for path in sorted(directory.glob("*.py")):
        name = path.stem
        spec = importlib.util.spec_from_file_location(f"generated_tools.{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        func = getattr(module, name, None)
        if callable(func):
            loaded.append(func)
    return loaded
