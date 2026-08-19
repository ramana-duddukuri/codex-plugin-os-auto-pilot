# Oniesoft Auto-Pilot Plugin for OpenAI Codex & ChatGPT

Drive the Oniesoft test automation platform from OpenAI Codex and ChatGPT. This plugin packages Oniesoft's test authoring, execution, and triage workflows alongside a FastMCP server exposing 31 platform tools.

---

## ⚡ Quick Start for Colleagues (1-Minute Setup)

### 1. Requirements
- **Python 3.10+** on PATH.
- **[uv](https://github.com/astral-sh/uv)** (recommended for instant dependency syncing).

### 2. Run Setup (Once per machine)

- **macOS / Linux:**
  ```bash
  ./setup.sh
  ```
- **Windows (PowerShell):**
  ```powershell
  .\setup.ps1
  ```
- **Or directly via Python (Any OS):**
  ```bash
  python scripts/setup.py
  ```

This script will:
1. Pre-sync all server dependencies automatically.
2. Register the local plugin marketplace in `~/.agents/plugins/marketplace.json`.
3. Enable the MCP server in `~/.codex/config.toml`.

---

## 📁 Project-Level Configuration (In Your Project / Workspace Folder)

All credentials and project configurations are read strictly from your **working project directory** (the project folder you opened in Codex / ChatGPT), **not** from the plugin directory:

### 1. Project `.env` (API Key)
In your project root directory, create `.env`:
```env
PLATFORM_API_KEY=your-actual-oniesoft-api-key
```

### 2. Project `config.json` (Project Settings)
In your project root directory, create `config.json`:
```json
{
  "companyId": "your-company-uuid",
  "userId": "your-user-uuid",
  "projectId": "your-project-uuid",
  "platformApiUrl": "http://localhost:8000",
  "backendUrl": "http://localhost:8088"
}
```

---

## 🚀 Using the Plugin in ChatGPT Desktop / Codex

1. **Restart** ChatGPT Desktop or Codex.
2. In **Plugins Directory** (Marketplace picker), look under **My Local Plugins** and enable **Oniesoft Auto-Pilot**.
3. Open your test project/workspace.
4. Start a new chat session and test:
   ```text
   @auto-pilot get details of test case TC-10508 using get_test_cases_with_filters
   ```

---

## 📦 What's Inside

| Component | Description |
| :--- | :--- |
| **`skills/`** | 9 end-to-end testing workflows: `analyze-requirements`, `create-tests`, `run-tests`, `schedule-test-run`, `mobile-testing`, `performance-testing`, `create-datafile`, `analyze-run`, and `push-to-autopilot`. |
| **`agents/`** | 3 specialist subagents: `test-author`, `failure-analyst`, `element-discoverer`. |
| **`server/`** | Bundled FastMCP server exposing 31 typed tools over stdio and Streamable HTTP. |
| **`.codex-plugin/plugin.json`** | Codex plugin manifest referencing skills, marketplace metadata, and `.mcp.json`. |
| **`.mcp.json`** | Portable MCP server launch configuration using `uv`. |
| **`hooks/hooks.json`** | `SessionStart` background dependency bootstrap hook. |

---

## 🛠️ Installing via Codex CLI (Alternative)

If using the Codex CLI directly:
```bash
# Add the local marketplace from this repository
codex plugin marketplace add .

# Or inspect MCP server status
codex mcp list
```

---

## 🧪 Validating Locally

You can test the MCP server interactively via the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector uv run --with-requirements server/requirements.txt --python ">=3.10" server/launch.py
```
