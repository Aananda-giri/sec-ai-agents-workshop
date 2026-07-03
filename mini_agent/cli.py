"""A minimal terminal chat loop for the coding agent — something in the
spirit of `claude` or nanocode's own CLI, built on the exact same Agent
class as every notebook in this workshop.

Run from the workshop/ directory:

    python3 -m mini_agent.cli
"""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from mini_agent import Agent, bash, edit_file, glob_files, grep_files, read_file, write_file
from mini_agent.coding_tools import WORKSPACE_DIR


INSTRUCTIONS = (
    "You are a concise coding assistant. Workspace: {workspace}. "
    "Only use tools when the request actually requires touching files or "
    "running something — reply directly to greetings and general questions."
)


def make_coding_agent() -> Agent:
    return Agent(
        tools=[read_file, write_file, edit_file, glob_files, grep_files, bash],
        instructions=INSTRUCTIONS.format(workspace=WORKSPACE_DIR),
        max_steps=8,
    )


async def repl() -> None:
    agent = make_coding_agent()
    print(f"mini coding agent — chatting in {WORKSPACE_DIR}")
    print("type your request, or 'exit'/'quit' to leave (Ctrl+C also works)\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("bye!")
            break

        await agent.run(user_input, verbose=True)
        print()


def main() -> None:
    load_dotenv(override=True)
    asyncio.run(repl())


if __name__ == "__main__":
    main()
