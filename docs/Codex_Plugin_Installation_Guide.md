# Installing the Oniesoft Auto-Pilot Codex Plugin

This guide covers installing **Oniesoft Auto-Pilot** for **OpenAI Codex** and **ChatGPT Desktop** — a plugin that connects the agent to the Oniesoft test automation platform via MCP tools, skills, and subagents.

Installation is done by **cloning this repository** and running the setup script once per machine (and again after every plugin update).

---

## What you need before you start

| Requirement | Why | Download / docs |
|---|---|---|
| **ChatGPT Desktop** or **Codex** | Hosts the plugin and agent | [openai.com/chatgpt](https://openai.com/chatgpt/download) |
| **Python 3.10+** | Runs the setup script | [python.org/downloads](https://www.python.org/downloads/) |
| **uv** (recommended) | Launches the MCP server and syncs dependencies | [uv installation](https://docs.astral.sh/uv/getting-started/installation/) |
| **Git** | Clone and pull plugin updates | [git-scm.com](https://git-scm.com/downloads) |
| **Oniesoft platform access** | The plugin calls your platform API | Cloud or self-hosted instance |
| **Personal API key** | Authenticates every API call (`x-api-key` header) | Platform → **Users → API Keys** |

### Install Python 3.10+

Download from [python.org/downloads](https://www.python.org/downloads/). On Windows, check **Add Python to PATH** during installation.

Verify:

```bash
python --version
# or
python3 --version
```

### Install uv (recommended)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:

```bash
uv --version
```

Full details: [docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/)

If `uv` is not installed, the setup script still runs but you must install server dependencies manually:

```bash
pip install -r server/requirements.txt
```

---

## Step 1 — Clone the repository

```bash
git clone https://bitbucket.org/onie-soft/auto-pilot-codex-plugin.git ~/auto-pilot-codex-plugin
cd ~/auto-pilot-codex-plugin
```

---

## Step 2 — Run the setup script (once per machine)

The setup script registers the local marketplace, configures Codex, pre-syncs MCP server dependencies, and caches plugin files.

### macOS / Linux

```bash
chmod +x setup.sh
./setup.sh
```

### Windows (PowerShell)

```powershell
cd C:\path\to\auto-pilot-codex-plugin
.\setup.ps1
```

### Any OS (direct Python)

```bash
python scripts/setup.py
```

### What the setup script does

1. Verifies **Python 3.10+**
2. Pre-syncs server dependencies via **uv** (if available)
3. Registers the local marketplace in `~/.agents/plugins/marketplace.json` (shown as **My Local Plugins**)
4. Copies plugin files to the Codex cache (`~/.codex/plugins/cache/oniesoft/auto-pilot/`)
5. Enables the plugin and MCP server in `~/.codex/config.toml`
6. If the **Codex CLI** is found, runs `codex plugin marketplace add` and `codex plugin add`

### PowerShell execution policy error (Windows)

If `.\setup.ps1` fails with an execution policy error, open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then close PowerShell, open a normal terminal, `cd` back to the plugin folder, and run `.\setup.ps1` again.

---

## Step 3 — Configure your test project

Credentials and project settings are read from your **workspace folder** (the project you open in Codex / ChatGPT) — **not** from the plugin directory.

### `.env` — API key (required)

Create `.env` in your project root:

```env
PLATFORM_API_KEY=your-personal-api-key-here
```

> **Never commit `.env`** — add it to `.gitignore`. See `.env.example` in the plugin repo for a template.

**Generate a key:** In the Oniesoft platform UI, go to **Profile → API Keys**. Create a key. A `401` from any tool means the key is missing or expired; a `403` means it lacks the required scope.

### `config.json` — project settings (required)

The API key is the **only** global plugin setting. Everything else is **per-project** and lives in a `config.json` file in the root of the project you are working in.

Download `config.json` and place it in your project folder. The downloaded file looks like this:

```json
{
  "companyId": "your-company-uuid",
  "projectId": "your-project-uuid",
  "userId": "your-user-uuid",
  "platformApiUrl": "https://your-platform-api.example.com",
  "backendUrl": "https://your-backend.example.com"
}
```

| Field | Description |
|---|---|
| `companyId` | Your Oniesoft company UUID |
| `projectId` | The test project UUID |
| `userId` | Your user/register UUID |
| `platformApiUrl` | Platform API base URL (e.g. `http://localhost:8000` for local dev) |
| `backendUrl` | Execution backend URL (e.g. `http://localhost:8088` for local dev) |

Codex reads this file at the start of each session. Pass these IDs explicitly on MCP tool calls — they are not auto-injected into every request.

To Download `config.json`:

1. Go to your Oniesoft platform and navigate to the project (Workspace) you want to work on.
2. Click the **Download config** button to download `config.json`.

---

## Step 4 — Enable the plugin in Codex / ChatGPT

1. **Restart** ChatGPT Desktop or Codex completely (quit and reopen).
2. Open **Plugins Directory** (marketplace picker).
3. Under **My Local Plugins**, enable **Oniesoft Auto-Pilot**.
4. Open your test project workspace (the folder containing `.env` and `config.json`).
5. Start a **new chat** session.

---

## Step 5 — Verify the installation

Ask in a new chat:

```text
@auto-pilot get details of test case TC-10508 using get_test_cases_with_filters
```

Or:

```text
List the available auto-pilot MCP tools.
```

A successful tool response confirms the API key, URLs, and project config are correct.

If the API key is missing, the MCP server logs:

```
auto-pilot: no PLATFORM_API_KEY configured. Add PLATFORM_API_KEY=... to /path/to/project/.env
```

---

## Updating to a new plugin version

After `git pull`, you must **re-run the setup script** and **restart Codex / ChatGPT**.

```bash
cd ~/auto-pilot-codex-plugin
git pull
./setup.sh          # macOS / Linux
# .\setup.ps1       # Windows
# python scripts/setup.py
```

Then **quit and reopen** ChatGPT Desktop or Codex.

---

## Alternative: Codex CLI

If you use the Codex CLI directly (after setup has been run at least once):

```bash
cd ~/auto-pilot-codex-plugin

# Add local marketplace from this repo
codex plugin marketplace add .

# Install the plugin
codex plugin add auto-pilot@oniesoft

# Check MCP server status
codex mcp list
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `setup.ps1` blocked on Windows | PowerShell execution policy | Open PowerShell as Admin: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then retry |
| `Python 3.10+ is required` | Python missing or too old | Install Python 3.10+ and ensure it is on `PATH` |
| `uv: command not found` | uv not installed | Install uv, or `pip install -r server/requirements.txt` |
| Plugin not in **My Local Plugins** | Setup not run or failed | Re-run `./setup.sh` or `.\setup.ps1` |
| `no PLATFORM_API_KEY configured` | Missing `.env` | Add `PLATFORM_API_KEY=...` to workspace root `.env` |
| `401` on tool calls | Bad or expired key | Regenerate key in platform, update `.env`, restart |
| `403` on tool calls | Key lacks scope | Regenerate with `generate` / `run` / `read` scopes |
| `No project_id given...` | Missing `config.json` | Add `config.json` to workspace root |
| Old behavior after `git pull` | Stale cache / config | Re-run setup script, restart ChatGPT / Codex |
| MCP server won't start | Deps not bootstrapped | Re-run setup; or: `uv run --with-requirements server/requirements.txt --python ">=3.10" server/launch.py --bootstrap-only` |

### Validate the MCP server locally

```bash
npx @modelcontextprotocol/inspector uv run --with-requirements server/requirements.txt --python ">=3.10" server/launch.py
```

---

## Quick reference

```bash
# Prerequisites: Python 3.10+, uv, Git

# Clone & setup
git clone https://bitbucket.org/onie-soft/auto-pilot-codex-plugin.git ~/auto-pilot-codex-plugin
cd ~/auto-pilot-codex-plugin
./setup.sh                    # macOS / Linux
# .\setup.ps1                 # Windows

# Per test project: .env + config.json in workspace root
# Restart ChatGPT / Codex → enable Oniesoft Auto-Pilot under My Local Plugins

# On update:
git pull && ./setup.sh && restart ChatGPT / Codex
```

**Windows execution policy (if needed):**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
