"""Tools for a minimal coding agent: read, write, edit, glob, grep, bash.

Loosely modeled on nanocode (https://github.com/1rgs/nanocode) — six tools
are most of what a coding agent needs — adapted to mini_agent's plain
function + docstring style. One deliberate departure: every tool is scoped
to a `workspace/` directory so a live demo can't wander outside it. `bash`
is the exception — it can still do anything the presenter's shell user can
(same caveat as `execute_python`: this is a teaching tool, not a sandbox).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"


def _resolve(path: str) -> Path:
    """Resolve a path inside WORKSPACE_DIR, rejecting anything that escapes it."""
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    root = WORKSPACE_DIR.resolve()
    resolved = (root / path).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"'{path}' escapes the workspace — refusing.")
    return resolved


def read_file(path: str, offset: int = 0, limit: int = 200) -> str:
    """Read a file's contents with line numbers, starting at line `offset`.

    Args:
        path: File path, relative to the workspace
        offset: Line number to start reading from (0-indexed)
        limit: Max number of lines to return
    """
    target = _resolve(path)
    if not target.exists():
        return f"Error: {path} does not exist"
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    selected = lines[offset:offset + limit]
    return "\n".join(f"{i + offset + 1}\t{line}" for i, line in enumerate(selected))


def write_file(path: str, content: str) -> str:
    """Create or overwrite a file with the given content.

    Args:
        path: File path, relative to the workspace
        content: Full text content to write
    """
    target = _resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"


def edit_file(path: str, old: str, new: str, replace_all: bool = False) -> str:
    """Replace an exact string in a file. Fails if `old` isn't unique unless replace_all is set.

    Args:
        path: File path, relative to the workspace
        old: Exact text to find
        new: Text to replace it with
        replace_all: If True, replace every occurrence instead of requiring exactly one
    """
    target = _resolve(path)
    if not target.exists():
        return f"Error: {path} does not exist"
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        return f"Error: text not found in {path}"
    if count > 1 and not replace_all:
        return f"Error: text appears {count} times in {path} — pass replace_all=True or make `old` more specific"
    new_text = text.replace(old, new) if replace_all else text.replace(old, new, 1)
    target.write_text(new_text, encoding="utf-8")
    return f"Edited {path} ({count if replace_all else 1} replacement{'s' if replace_all and count > 1 else ''})"


def glob_files(pattern: str, path: str = ".") -> str:
    """Find files matching a glob pattern (e.g. '**/*.py'), most recently modified first.

    Args:
        pattern: Glob pattern to match filenames against
        path: Directory to search from, relative to the workspace
    """
    base = _resolve(path)
    if not base.exists():
        return f"Error: {path} does not exist"
    matches = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not matches:
        return "No matches"
    return "\n".join(str(m.relative_to(WORKSPACE_DIR)) for m in matches)


def grep_files(pattern: str, path: str = ".") -> str:
    """Search file contents with a regex pattern, returning matching lines as file:line:text.

    Args:
        pattern: Regular expression to search for
        path: File or directory to search, relative to the workspace
    """
    base = _resolve(path)
    if not base.exists():
        return f"Error: {path} does not exist"
    regex = re.compile(pattern)
    files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]

    hits = []
    for f in files:
        try:
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if regex.search(line):
                    hits.append(f"{f.relative_to(WORKSPACE_DIR)}:{i}:{line}")
        except Exception:
            continue
    return "\n".join(hits) if hits else "No matches"


def bash(command: str, timeout: int = 30) -> str:
    """Run a shell command in the workspace directory and return its output.

    Args:
        command: Shell command to execute
        timeout: Max seconds to allow the command to run
    """
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"

    parts = []
    if result.stdout:
        parts.append(result.stdout.rstrip("\n"))
    if result.stderr:
        parts.append(f"STDERR:\n{result.stderr.rstrip(chr(10))}")
    return "\n".join(parts) if parts else "(no output)"
