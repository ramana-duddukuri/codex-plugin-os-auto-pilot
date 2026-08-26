# Oniesoft Auto-Pilot Plugin for OpenAI Codex & ChatGPT

Drive the Oniesoft test automation platform from OpenAI Codex and ChatGPT. This plugin packages Oniesoft's test authoring, execution, and triage workflows alongside a FastMCP server exposing 31 platform tools.

**Full installation guide:** [docs/INSTALLATION.md](docs/INSTALLATION.md)

---

## Quick start

### 1. Requirements

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** (recommended for dependency syncing)
- **Git** — [git-scm.com](https://git-scm.com/downloads)

### 2. Clone and run setup (once per machine)

```bash
git clone https://bitbucket.org/onie-soft/auto-pilot-codex-plugin.git ~/auto-pilot-codex-plugin
cd ~/auto-pilot-codex-plugin
```

**macOS / Linux:**

```bash
./setup.sh
```

**Windows (PowerShell):**

```powershell
.\setup.ps1
```

**Any OS:**

```bash
python scripts/setup.py
```

If `setup.ps1` fails with an execution policy error on Windows, open PowerShell **as Administrator** and run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry `.\setup.ps1`.

The setup script will:

1. Pre-sync server dependencies via `uv`
2. Register the local marketplace in `~/.agents/plugins/marketplace.json`
3. Enable the MCP server in `~/.codex/config.toml`

### 3. Configure your test project

In each project workspace, create:

**`.env`** (API key):

```env
PLATFORM_API_KEY=your-actual-oniesoft-api-key
```

**`config.json`** (project settings):

```json
{
  "companyId": "your-company-uuid",
  "userId": "your-user-uuid",
  "projectId": "your-project-uuid",
  "platformApiUrl": "http://localhost:8000",
  "backendUrl": "http://localhost:8088"
}
```

> Never commit `.env`. See `.env.example` for a template.

### 4. Enable and use

1. **Restart** ChatGPT Desktop or Codex
2. **Plugins Directory** → **My Local Plugins** → enable **Oniesoft Auto-Pilot**
3. Open your test project and start a new chat:

```text
@auto-pilot get details of test case TC-10508 using get_test_cases_with_filters
```

### Updating

```bash
cd ~/auto-pilot-codex-plugin && git pull
./setup.sh          # or .\setup.ps1 on Windows
```

Then restart ChatGPT Desktop / Codex.

---

## What's inside

| Component | Description |
| :--- | :--- |
| **`skills/`** | 9 workflows: `analyze-requirements`, `create-tests`, `run-tests`, `schedule-test-run`, `mobile-testing`, `performance-testing`, `create-datafile`, `analyze-run`, `push-to-autopilot` |
| **`agents/`** | 3 subagents: `test-author`, `failure-analyst`, `element-discoverer` |
| **`server/`** | FastMCP server with 31 typed tools |
| **`.codex-plugin/plugin.json`** | Codex plugin manifest |
| **`.mcp.json`** | MCP server launch config (via `uv`) |
| **`hooks/hooks.json`** | SessionStart dependency bootstrap |

---

## Codex CLI (alternative)

```bash
codex plugin marketplace add .
codex plugin add auto-pilot@oniesoft
codex mcp list
```

---

## Local MCP validation

```bash
npx @modelcontextprotocol/inspector uv run --with-requirements server/requirements.txt --python ">=3.10" server/launch.py
```
