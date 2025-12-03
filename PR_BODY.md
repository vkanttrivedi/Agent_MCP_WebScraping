Summary
- Adds lightweight preflight checks to `agent_webscrap.py` that verify required runtime pieces are present before starting the agent:
  - `GITHUB_TOKEN` environment variable (used by the model client)
  - `node` on PATH
  - `npx` on PATH
- Adds a short non-invasive `npx --version` probe and prints a warning if it fails.
- The checks are skippable via environment variable `SKIP_PREFLIGHT=1` (intended for CI or constrained environments).

Files changed
- `agent_webscrap.py` — added preflight checks and a quick `npx --version` probe.

Why
- Gives faster, clearer failure messages for the most common setup problems (missing PAT or Node installation) rather than failing later when MCP is spawned.
- Improves developer experience for new contributors running the example locally.

Behavior & usage
- Normal run (PowerShell):
  ```powershell
  pip install -r requirements.txt
  $env:GITHUB_TOKEN = "<your-github-pat>"
  python agent_webscrap.py
  ```
- If preflight fails, the script prints missing items and exits with status 1.
- To bypass (useful in CI or when you intentionally want to skip checks):
  - PowerShell: `$env:SKIP_PREFLIGHT = "1"; python agent_webscrap.py`

Testing performed
- Local static verification and commit on branch `feat/preflight-check`.
- Branch pushed to remote; PR can be created from branch `feat/preflight-check`.

Notes for reviewers
- The preflight check is intentionally minimal and non-invasive (it does not install packages).
- If desired, we can extend preflight to:
  - Check `npx @playwright/mcp` reachability
  - Suggest commands to fix issues (e.g., `npx playwright install`)
  - Add a small `--preflight` CLI flag instead of env var.
