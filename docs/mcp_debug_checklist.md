## MCP Startup Debug Checklist

Quick steps to diagnose MCP (Playwright) startup issues when running `agent_webscrap.py`:

- **Verify Node/npm are installed:**
  - PowerShell: `node -v; npm -v`
  - If missing, install Node.js from https://nodejs.org/
- **Ensure `npx` can fetch packages:**
  - Try: `npx -y @playwright/mcp@latest --version` to confirm network access.
- **Check environment network restrictions:**
  - Corporate proxies or blocked outbound may prevent `npx` from downloading the MCP package.
- **Inspect agent logs:**
  - `agent_webscrap.py` configures `logging.getLogger("openai.agents")` to stdout. Look for MCP process stderr in the same console.
- **Run MCP manually to replicate failure:**
  - `npx -y @playwright/mcp@latest` — this should start the MCP process; errors here show local environment issues.
- **Common failures and fixes:**
  - `npx` fetch timeout → check DNS/proxy and retry.
  - `permission denied` on spawn → ensure antivirus or execution policy isn't blocking node child processes.
  - Missing Playwright browsers → `npx playwright install` may be required in restricted environments.
- **If model errors appear after MCP starts:**
  - Verify `GITHUB_TOKEN` env var is set and valid:
    - PowerShell: `$env:GITHUB_TOKEN`
  - The model client in `agent_webscrap.py` uses `AsyncOpenAI(base_url="https://models.github.ai/inference", api_key=os.environ['GITHUB_TOKEN'])`.

Use these steps to isolate whether the issue is local environment (Node/npx) or runtime configuration (env vars, network). If you want, I can add automated checks to `agent_webscrap.py` to print preflight status.
