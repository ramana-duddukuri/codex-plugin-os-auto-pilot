#!/usr/bin/env python3
"""Cross-platform setup script for Oniesoft Auto-Pilot Codex plugin.

Works identically on Windows, macOS, and Linux.

Usage:
    python scripts/setup.py
    python3 scripts/setup.py
"""

from __future__ import annotations

import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def check_python_version() -> None:
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 10):
        print(f"❌ Error: Python 3.10 or higher is required (current: {sys.version.split()[0]}).")
        sys.exit(1)
    print(f"   ✓ Python {sys.version.split()[0]} detected.")


def find_uv_binary() -> str | None:
    uv_bin = shutil.which("uv") or shutil.which("uv.exe")
    if uv_bin:
        return Path(uv_bin).as_posix()

    home = Path.home()
    possible_uv = [
        home / ".local" / "bin" / "uv",
        home / ".local" / "bin" / "uv.exe",
        home / ".cargo" / "bin" / "uv",
        home / ".cargo" / "bin" / "uv.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "uv" / "uv.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "uv" / "uv.exe",
    ]
    for p in possible_uv:
        if p and p.exists() and p.is_file():
            return p.resolve().as_posix()
    return None


def check_and_sync_dependencies() -> None:
    print("\n📦 Checking dependencies...")
    uv_bin = find_uv_binary()

    if uv_bin:
        print(f"   ✓ Found uv at {uv_bin}")
        print("   ⏳ Pre-syncing server requirements via uv...")
        try:
            req_file = str(PLUGIN_ROOT / "server" / "requirements.txt")
            launch_file = str(PLUGIN_ROOT / "server" / "launch.py")
            subprocess.run(
                [uv_bin, "run", "--with-requirements", req_file, "--python", ">=3.10", launch_file, "--bootstrap-only"],
                cwd=str(PLUGIN_ROOT),
                check=True,
            )
            print("   ✓ Server dependencies pre-synced successfully.")
        except Exception as e:
            print(f"   ⚠️  Note: uv bootstrap returned: {e}")
    else:
        print("   ℹ️  'uv' not found on PATH. If needed, install it via https://github.com/astral-sh/uv")
        print("      or install requirements manually: pip install -r server/requirements.txt")


def register_personal_marketplace() -> None:
    print("\n🛒 Registering local marketplace in ~/.agents/plugins/marketplace.json...")
    agents_plugins_dir = Path.home() / ".agents" / "plugins"
    agents_plugins_dir.mkdir(parents=True, exist_ok=True)
    marketplace_file = agents_plugins_dir / "marketplace.json"

    # Always use posix forward slashes for cross-platform JSON compatibility
    plugin_path_str = PLUGIN_ROOT.resolve().as_posix()

    marketplace_data = {
        "name": "personal-marketplace",
        "interface": {
            "displayName": "My Local Plugins"
        },
        "plugins": [
            {
                "name": "auto-pilot",
                "source": {
                    "source": "local",
                    "path": plugin_path_str
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL"
                },
                "category": "Productivity"
            }
        ]
    }

    if marketplace_file.exists():
        try:
            with open(marketplace_file, encoding="utf-8") as fh:
                existing = json.load(fh)
            plugins = existing.setdefault("plugins", [])
            updated = False
            for idx, p in enumerate(plugins):
                if p.get("name") == "auto-pilot":
                    plugins[idx] = marketplace_data["plugins"][0]
                    updated = True
                    break
            if not updated:
                plugins.append(marketplace_data["plugins"][0])
            marketplace_data = existing
        except Exception:
            pass

    with open(marketplace_file, "w", encoding="utf-8") as fh:
        json.dump(marketplace_data, fh, indent=2)
        fh.write("\n")
    print(f"   ✓ Marketplace entry updated at {marketplace_file}")


def get_plugin_version() -> str:
    plugin_json = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    if plugin_json.exists():
        try:
            with open(plugin_json, encoding="utf-8") as fh:
                data = json.load(fh)
                return str(data.get("version", "0.1.0"))
        except Exception:
            pass
    return "0.1.0"


def populate_codex_cache() -> None:
    version = get_plugin_version()
    cache_dir = Path.home() / ".codex" / "plugins" / "cache" / "oniesoft" / "auto-pilot" / version
    print(f"\n📂 Syncing clean plugin files to Codex cache ({cache_dir})...")
    try:
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)
        cache_dir.mkdir(parents=True, exist_ok=True)

        items_to_copy = [
            ".codex-plugin",
            ".mcp.json",
            "skills",
            "agents",
            "server",
            "hooks",
            "docs",
            "AGENTS.md",
            "README.md",
        ]
        for item in items_to_copy:
            src = PLUGIN_ROOT / item
            dst = cache_dir / item
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.is_file():
                shutil.copy2(src, dst)

        # In the cached .mcp.json, inject resolved uv path and UTF-8 env
        uv_bin = find_uv_binary()
        if uv_bin:
            cached_mcp_json = cache_dir / ".mcp.json"
            if cached_mcp_json.exists():
                try:
                    with open(cached_mcp_json, encoding="utf-8") as fh:
                        mcp_cfg = json.load(fh)
                    servers = mcp_cfg.get("mcp_servers") or mcp_cfg.get("mcpServers") or mcp_cfg
                    if "auto-pilot" in servers:
                        servers["auto-pilot"]["command"] = uv_bin
                        servers["auto-pilot"]["env"] = {
                            "PYTHONUNBUFFERED": "1",
                            "PYTHONUTF8": "1",
                            "PYTHONIOENCODING": "utf-8"
                        }
                    with open(cached_mcp_json, "w", encoding="utf-8") as fh:
                        json.dump(mcp_cfg, fh, indent=2)
                except Exception:
                    pass

        print("   ✓ Plugin files cached successfully.")
    except Exception as e:
        print(f"   ⚠️  Could not populate cache directly: {e}")


def register_codex_config() -> None:
    print("\n⚙️  Configuring Codex settings in ~/.codex/config.toml...")
    codex_dir = Path.home() / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    config_file = codex_dir / "config.toml"

    plugin_root_posix = PLUGIN_ROOT.resolve().as_posix()
    req_file = (PLUGIN_ROOT / "server" / "requirements.txt").as_posix()
    launch_file = (PLUGIN_ROOT / "server" / "launch.py").as_posix()
    uv_bin = find_uv_binary() or "uv"
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    config_text = ""
    if config_file.exists():
        try:
            config_text = config_file.read_text(encoding="utf-8")
        except Exception:
            config_text = ""

    additions = []

    # 1. Enable plugin
    if '[plugins."auto-pilot@oniesoft"]' not in config_text:
        additions.append(f"""
[plugins."auto-pilot@oniesoft"]
enabled = true
""")

    # 2. Explicitly enable MCP tools under the plugin namespace
    if '[plugins."auto-pilot@oniesoft".mcp_servers."auto-pilot"]' not in config_text:
        additions.append(f"""
[plugins."auto-pilot@oniesoft".mcp_servers."auto-pilot"]
enabled = true
default_tools_approval_mode = "prompt"
""")

    if '[plugins."auto-pilot".mcp_servers."auto-pilot"]' not in config_text:
        additions.append(f"""
[plugins."auto-pilot".mcp_servers."auto-pilot"]
enabled = true
default_tools_approval_mode = "prompt"
""")

    # 3. Register marketplace
    if '[marketplaces.oniesoft]' not in config_text:
        additions.append(f"""
[marketplaces.oniesoft]
last_updated = "{now_iso}"
source_type = "local"
source = "{plugin_root_posix}"
""")

    # 4. Register fallback MCP server
    if '[mcp_servers.auto-pilot]' not in config_text:
        additions.append(f"""
[mcp_servers.auto-pilot]
command = "{uv_bin}"
args = ["run", "--with-requirements", "{req_file}", "--python", ">=3.10", "{launch_file}"]
enabled = true
startup_timeout_sec = 120
""")

    if additions:
        config_text = config_text.rstrip() + "\n" + "\n".join(additions).strip() + "\n"
        config_file.write_text(config_text, encoding="utf-8")
        print(f"   ✓ Added plugin, marketplace, and MCP configuration to {config_file}")
    else:
        print(f"   ✓ Configuration already up to date in {config_file}")


def find_codex_cli() -> str | None:
    cli = shutil.which("codex") or shutil.which("codex.exe")
    if cli:
        return Path(cli).as_posix()

    home = Path.home()
    possible_paths = [
        # macOS
        Path("/Applications/ChatGPT.app/Contents/Resources/codex"),
        home / ".local" / "bin" / "codex",
        # Windows
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ChatGPT" / "resources" / "codex.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "ChatGPT" / "resources" / "codex.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "ChatGPT" / "resources" / "codex.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "ChatGPT" / "resources" / "codex.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "codex" / "codex.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "OpenAI" / "Codex" / "bin" / "f71e347eb70b3d24" / "codex.exe",
        home / ".codex" / "bin" / "codex.exe",
        home / ".codex" / "bin" / "codex",
    ]

    for p in possible_paths:
        if p and p.exists() and p.is_file():
            return p.resolve().as_posix()
    return None


def run_codex_cli_registration() -> None:
    codex_cli = find_codex_cli()
    if not codex_cli:
        return

    print(f"\n⚡ Found Codex CLI at {codex_cli}")
    print("   Running 'codex plugin marketplace add' and 'codex plugin add'...")
    plugin_path_str = PLUGIN_ROOT.resolve().as_posix()
    try:
        subprocess.run([codex_cli, "plugin", "marketplace", "add", plugin_path_str], check=False)
        subprocess.run([codex_cli, "plugin", "add", "auto-pilot@oniesoft"], check=False)
        print("   ✓ Plugin registered via Codex CLI.")
    except Exception as e:
        print(f"   ⚠️  Codex CLI registration note: {e}")


def main() -> None:
    print("=" * 60)
    print("🚀 Setting up Oniesoft Auto-Pilot Plugin for Codex / ChatGPT")
    print("=" * 60)
    print(f"OS: {platform.system()} ({platform.release()})")
    print(f"Plugin Path: {PLUGIN_ROOT}")

    check_python_version()
    check_and_sync_dependencies()
    register_personal_marketplace()
    populate_codex_cache()
    register_codex_config()
    run_codex_cli_registration()

    print("\n" + "=" * 60)
    print("🎉 Plugin setup completed successfully!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. In your test workspace directory, make sure you have:")
    print("   - .env (containing PLATFORM_API_KEY=...)")
    print("   - config.json (containing projectId, userId, etc.)")
    print("2. Restart ChatGPT Desktop / Codex.")
    print("3. You will see 'Oniesoft Auto-Pilot' under Plugins and in the Plugins Directory.")
    print("4. Start a new chat and ask: 'get details of test case TC-10508 using get_test_cases_with_filters'")


if __name__ == "__main__":
    main()
