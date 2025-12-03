<!-- Copilot / AI agent guidance for this repository -->
# Project: project_codex — AI agent connector

This repository is a small example that wires an agent runtime to MCP servers and a hosted model. The goal of this file is to give an AI coding agent the minimal, actionable knowledge to be productive here.

## Big picture
- **Single-script agent runner:** The main code is `agent_webscrap.py`. It creates an `Agent`, configures an MCP server (Playwright via `npx @playwright/mcp`), and runs the agent with `Runner.run`.
- **Model boundary:** The script uses `OpenAIChatCompletionsModel` backed by `AsyncOpenAI` and points to `https://models.github.ai/inference`. Authentication is via the `GITHUB_TOKEN` environment variable.
- **MCP integration:** MCP servers are configured in `servers` (see `MCPServerStdio` usage). The agent delegates browser automation to the external MCP process (Playwright) started via `npx`.

## How to run locally (developer workflow)
- Install dependencies (this repo relies on the `openai-agents` package version `0.*`):

```
pip install openai-agents==0.*
```

- Set environment variable required by `agent_webscrap.py`:

```
# Windows PowerShell
$env:GITHUB_TOKEN = "<your-github-pat>"
```

- Run the script:

```
python agent_webscrap.py
```

Notes: the script spawns `npx @playwright/mcp` using `MCPServerStdio`. Ensure `node`/`npx` are available on your PATH.

<!-- Copilot / AI agent guidance for this repository -->
# Project: project_codex — AI agent connector (quick guide for AI coding agents)

This repository demonstrates wiring an `Agent` to external MCP servers (Playwright) and a hosted model. The goal: give an AI coding agent immediate, actionable knowledge to be productive.

**Big picture**
- `agent_webscrap.py` is the single-run example: it creates an `Agent`, configures MCP servers (via `MCPServerStdio`), and calls `Runner.run` with a typed message list.
- Model boundary: the code uses `AsyncOpenAI` pointing to `https://models.github.ai/inference` and passes that client into `OpenAIChatCompletionsModel`. Authentication comes exclusively from the `GITHUB_TOKEN` env var.
- MCPs are external processes (started with `npx @playwright/mcp` in this repo). Treat MCP servers as out-of-process tools the agent invokes.

**Quick start (tested steps)**
- Install python deps: `pip install -r requirements.txt` (or `pip install openai-agents==0.*` if adding minimal deps).
- Set GitHub PAT (PowerShell):
  - `$env:GITHUB_TOKEN = "<your-github-pat>"`
- Ensure `node` + `npx` are on PATH (Playwright is pulled by `npx`).
- Run example: `python agent_webscrap.py`

**Important repo-specific conventions & patterns**
- Message shape: `Runner.run` expects a list of message objects. Each message uses `role` and `content` where `content` is an array of typed pieces (commonly `input_text` for user prompts and `output_text` for assistant responses). Example in `agent_webscrap.py`.
- Do NOT change the `content` entry types (`input_text` / `output_text`) or the overall list/role shape — downstream parsers and `examples/parse_output.py` assume this exact shape.
- MCP server construction: follow existing `MCPServerStdio(params=..., name=..., client_session_timeout_seconds=...)` usage. Preserve `name` and `client_session_timeout_seconds` when adding servers for discoverability and session behavior.
- Logging: the example enables `logging.getLogger("openai.agents")` and sets `set_tracing_disabled(True)`. Use the same logger name to surface agent runtime logs.

**Files to inspect (high signal)**
- `agent_webscrap.py` — canonical example: model client, MCPServerStdio params, `Runner.run` payload and example response shape.
- `examples/parse_output.py` — reference parser for `output_text` blocks: shows extracting YAML snapshots, JS code blocks, and screenshot paths.
- `requirements.txt` — canonical dependency pinning for local runs.

**Integration & runtime notes (gotchas found in code)**
- The model client uses the `GITHUB_TOKEN` PAT — do not substitute with other OpenAI-style env vars without updating the client config.
- Playwright is launched by `npx`, so Node must be installed. Playwright package is not preinstalled; `npx` fetches the MCP binary at runtime.
- MCP errors commonly indicate missing `npx`/Node or network restrictions preventing `npx` from fetching packages.

**Examples to copy when editing code**
- Minimal agent creation (from `agent_webscrap.py`):
```
agent = Agent(
  name="agent",
  instructions="You are a web exploration assistant...",
  mcp_servers=servers,
  model=OpenAIChatCompletionsModel("openai/gpt-4.1", openaiClient),
)
```
- Playwright MCP server usage:
```
MCPServerStdio(params={
  "command": "npx",
  "args": ["-y", "@playwright/mcp@latest"],
}, name="aitk-playwright-example", client_session_timeout_seconds=30)
```

**Parsing / downstream tooling expectations**
- Parsers (see `examples/parse_output.py`) look for `output_text` entries and expect YAML fenced blocks (```yaml```) and JS blocks (```js```) embedded in the assistant text. Keep that formatting when returning structured snapshots or code.

**When editing this repo**
- Preserve the `Runner.run` message schema and `content` types.
- Preserve MCP server `name` and `client_session_timeout_seconds` when adding servers.
- Keep `AsyncOpenAI(base_url=..., api_key=os.environ['GITHUB_TOKEN'])` behavior unless explicitly migrating the model endpoint.

If any part of this file is unclear or you want a shorter version for a different agent persona, tell me which section to trim or expand and I will iterate.
]
