# project_codex

Small example that wires an agent runtime to MCP servers and a hosted model. Primary file: `agent_webscrap.py`.

Quick start

1. Install Python deps:

```powershell
pip install -r requirements.txt
```

2. Set your GitHub PAT (used by the model client):

```powershell
$env:GITHUB_TOKEN = "<your-github-pat>"
```

3. Ensure `node` and `npx` are on your PATH (Playwright MCP runs via `npx`). Then run:

```powershell
python agent_webscrap.py
```

Notes
- The script launches `npx @playwright/mcp` to provide browser automation; Node is required but Playwright is handled by `npx`.
- The example targets `https://models.github.ai/inference` and expects `GITHUB_TOKEN` for auth.
