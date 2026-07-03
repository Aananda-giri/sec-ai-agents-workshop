# Quickstart

Get this workshop running locally: a Python virtual environment, the packages it needs,
your API key, and a smoke test to confirm everything works — **before** the session starts.

Works the same on Windows, macOS, and Linux; platform-specific commands are called out.

## 0. Prerequisites

- **Python 3.10 or newer.** Check with:
  ```bash
  python3 --version      # macOS/Linux
  python --version       # Windows
  ```
  If you don't have it: [python.org/downloads](https://www.python.org/downloads/). On Windows,
  tick **"Add python.exe to PATH"** during install, or use the `py` launcher shown below.
- A terminal: Terminal (macOS), any shell (Linux), or **PowerShell** (Windows — recommended
  over cmd.exe, see the troubleshooting note below if activation gets blocked).

## 1. Get the code

If you already have this `workshop/` folder (zip, USB, git clone), just open a terminal
**inside it** — every command below assumes your current directory is `workshop/`.

```bash
cd path/to/workshop
```

## 2. Create a virtual environment

A virtual environment keeps this workshop's packages separate from anything else on your
machine.

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (cmd.exe):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Your prompt should now start with `(.venv)`. You'll need to re-run the *activate* command
(not `venv` creation) every time you open a new terminal for this project.

<details>
<summary>Prefer <code>uv</code> instead of venv+pip?</summary>

If you have [uv](https://docs.astral.sh/uv/) installed, it replaces steps 2 and 3:
```bash
uv venv
source .venv/bin/activate      # or .venv\Scripts\Activate.ps1 on Windows
uv pip install -r requirements.txt
```
</details>

## 3. Install the packages

With the virtual environment active:

```bash
pip install -r requirements.txt
```

This installs `litellm` (the LLM client), `jupyterlab`, `python-dotenv`, `tavily-python`
(web search), `datasets` (optional real GAIA dataset), and `pydantic`.

## 4. Set up your API key

```bash
cp .env.example .env          # macOS/Linux
copy .env.example .env        # Windows cmd.exe
Copy-Item .env.example .env   # Windows PowerShell
```

Open `.env` in any text editor and fill in:

- **`DEEPSEEK_API_KEY`** (required) — get one at
  [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys).
- `TAVILY_API_KEY` (optional) — enables the live `web_search` tool in Act 2/3. Free key at
  [app.tavily.com](https://app.tavily.com). Without it, `web_search` just returns a friendly
  "not configured" message instead of crashing anything.
- `HF_TOKEN` (optional) — only needed if you want `load_hf_gaia()` to pull the real, gated
  GAIA dataset in Act 5 instead of the bundled sample questions. Not required to present.

**Do not commit `.env`** — it's already in `.gitignore`.

## 5. Run it

**Option A — Jupyter (how the workshop is actually presented):**
```bash
jupyter lab
```
This opens a browser tab. In the file browser on the left, open `notebooks/01_simplest_agent.ipynb`
and run cells top to bottom with **Shift+Enter**. Notebooks 01–05 build on each other in order.

**Option B — plain Python**, if you just want to poke at `mini_agent` without Jupyter:
```bash
python3
```
```python
import asyncio
from dotenv import load_dotenv
load_dotenv(override=True)

from mini_agent import Agent, calculator

async def main():
    agent = Agent(tools=[calculator], instructions="Use tools for math.")
    print(await agent.run("What is 91 * 7?"))

asyncio.run(main())
```

## 6. Verify your setup now, not during the workshop

Run this before you present — it's the fastest way to confirm your key actually works:

```bash
python3 -c "
import asyncio
from dotenv import load_dotenv
load_dotenv(override=True)
from litellm import acompletion

async def main():
    r = await acompletion(model='deepseek/deepseek-v4-flash', messages=[{'role': 'user', 'content': 'Say OK.'}])
    print('SUCCESS:', r.choices[0].message.content)

asyncio.run(main())
"
```

If you see `SUCCESS: OK` (or similar), you're ready. If not, see Troubleshooting below.

## Troubleshooting

**`python: command not found` (macOS/Linux)**
Use `python3` instead of `python` — some systems don't alias `python` to `python3`.

**Windows: `Activate.ps1 cannot be loaded because running scripts is disabled`**
PowerShell blocks script execution by default. Either use cmd.exe's
`.venv\Scripts\activate.bat` instead, or allow scripts for your user:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**`ModuleNotFoundError: No module named 'mini_agent'`**
Notebooks add the parent folder to `sys.path` (`sys.path.insert(0, ".."))`, which only works
if Jupyter's working directory is `notebooks/`. Make sure you launched `jupyter lab` from the
`workshop/` folder, not from inside `notebooks/`.

**Auth error / 401 from DeepSeek, but the key "should" work**
`load_dotenv()` does **not** override a variable that's already set in your shell — if you
ever `export`ed an API key manually (or your shell profile does), it silently wins over
`.env`. Check for a shadowing value:
```bash
env | grep -i api_key          # macOS/Linux
Get-ChildItem Env: | Select-String -Pattern api_key   # PowerShell
```
Every notebook here already calls `load_dotenv(override=True)` for exactly this reason — if
you add your own `load_dotenv()` call anywhere, do the same.

**`jupyter lab` opens but port 8888 is already in use**
Another Jupyter instance is running. Either stop it, or run `jupyter lab --port 8889`.

**Rate limits / slow responses mid-demo**
`mini_agent/agent.py` retries transient errors (429s, timeouts, 503s) automatically with
backoff — an occasional 5–20 second pause is normal, don't panic and re-run the cell.

**Done for the day? Deactivate the virtual environment:**
```bash
deactivate
```
