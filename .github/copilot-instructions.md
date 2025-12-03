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

## Key patterns and conventions (project-specific)
- Message payloads passed to `Runner.run` use a structured list of dicts: roles (`user`/`assistant`), and `content` entries with `type` values such as `input_text` and `output_text`. See the example payload in `agent_webscrap.py`.
- MCP servers are created and passed into the `Agent` via the `mcp_servers` parameter — treat MCP servers as external capabilities (browser, system commands) that the agent calls rather than internal libraries.
- Logging/tracing: the script configures `logging.getLogger("openai.agents")` and calls `set_tracing_disabled(True)` — follow this pattern if adding instrumentation.

## Integration and external dependencies
- External runtime: Node.js (`npx`) is required to start the Playwright MCP integration.
- Auth: `GITHUB_TOKEN` must be a GitHub Personal Access Token for the `models.github.ai` endpoint. The code uses `AsyncOpenAI(base_url=..., api_key=os.environ['GITHUB_TOKEN'])`.

## Files to inspect when making changes
- `agent_webscrap.py` — main example and canonical usage patterns (agent creation, model config, MCP servers, Runner invocation).

## Useful examples to copy/paste
- Minimal agent creation (from file):

```
agent = Agent(
  name="agent",
  instructions="You are a web exploration assistant...",
  mcp_servers=servers,
  model=OpenAIChatCompletionsModel("openai/gpt-4.1", openaiClient),
)
```

- MCP server example (Playwright via stdio):

```
MCPServerStdio(params={
  "command": "npx",
  "args": ["-y", "@playwright/mcp@latest"]
})
```

## What to avoid / gotchas (discoverable from code)
- Don't assume local OpenAI API keys; this script targets `models.github.ai` and expects `GITHUB_TOKEN`.
- Node and `npx` are required; errors about MCP startup typically mean `npx`/Node is missing or blocked by environment restrictions.

## If you modify this repo
- Keep the message shape used in `Runner.run` consistent. Tests or downstream tooling may rely on `content` entries with `type` fields like `input_text`/`output_text`.
- When adding new MCP servers, follow the `MCPServer*` constructors and preserve `client_session_timeout_seconds` and `name` fields for discoverability.
- When adding new MCP servers, follow the `MCPServer*` constructors and preserve `client_session_timeout_seconds` and `name` fields for discoverability.

## Message schema (example)
- Runner messages are a JSON list of message objects. Each message contains `role` and a `content` array of typed entries. Example payload used in `agent_webscrap.py`:

```json
[
  {
    "role": "user",
    "content": [
      { "type": "input_text", "text": "Please navigate to https://www.example.com and extract heading." }
    ]
  },
  {
    "role": "assistant",
    "status": "completed",
    "content": [
      { "type": "output_text", "text": "### Page Title: Example Domain\n\nSummary: Example Domain is a placeholder site used for documentation." }
    ]
  }
]
```

Use this exact shape (roles + `content` entries with `type`) when building tests or additional examples; downstream tooling expects `input_text`/`output_text` types.

## Notes about dependencies and run files
- A minimal `requirements.txt` is provided for reproducible installs. Use it to install Python deps before running the script.
- The project relies on Node.js for MCP servers (`npx @playwright/mcp`) — install Node/npm on your PATH before running.

## Multi-turn & tool-invocation example
Below is a compact multi-turn example showing how the `user` asks for a web task, the `assistant` may emit tool-invocation code (Playwright), and later return structured `output_text` with a YAML snapshot. This mirrors the example in `agent_webscrap.py` and is the shape other tooling expects.

```json
[
  { "role": "user", "content": [{ "type": "input_text", "text": "Visit https://example.com and return title + screenshot." }] },
  { "role": "assistant", "status": "tool_call", "content": [{ "type": "output_text", "text": "### Ran Playwright code\n```js\nawait page.goto('https://example.com');\nawait page.screenshot({ path: 'shot.png' });\n```" }] },
  { "role": "assistant", "status": "completed", "content": [{ "type": "output_text", "text": "### Page state\n- Page URL: https://example.com/\n- Page Title: Example Domain\n- Page Snapshot:\n```yaml\n- generic:\n  - heading \"Example Domain\"\n```" }] }
]
```

Treat `status: "tool_call"` or similar markers as informational; the runtime may use other fields to identify tool usage. Keep `content` entries as arrays of typed pieces so downstream parsers can iterate predictably.

## Parsing assistant output (example)
When the assistant embeds structured data (JSON strings or YAML blocks) inside `output_text`, you can extract and parse it programmatically. A small example script is provided at `examples/parse_output.py` that demonstrates:
- locating `output_text` entries in a `Runner.run` response
- extracting fenced ```yaml``` blocks and parsing them with `PyYAML`

Use the `examples/parse_output.py` as a copyable reference for downstream tooling that needs to extract headings, screenshots references, or snapshots from assistant outputs.

---
If anything above is unclear or you want more detail about a specific integration (for example, the exact environment `npx` expects or how responses are parsed), tell me which area to expand and I will update this file.
