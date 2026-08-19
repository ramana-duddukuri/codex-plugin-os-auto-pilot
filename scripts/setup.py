#!/usr/bin/env python3
"""Cross-platform setup script for Oniesoft Auto-Pilot Codex plugin.

Works identically on macOS, Linux, and Windows.

Usage:
    python scripts/setup.py
    python3 scripts/setup.py
"""

from __future__ import annotations

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


def check_and_sync_dependencies() -> None:
    print("\n📦 Checking dependencies...")
    uv_bin = shutil.which("uv")
    if not uv_bin:
        # Check standard user local directories
        home = Path.home()
        possible_uv = [
            home / ".local" / "bin" / "uv",
            home / ".local" / "bin" / "uv.exe",
            home / ".cargo" / "bin" / "uv",
            home / ".cargo" / "bin" / "uv.exe",
        ]
        for p in possible_uv:
            if p.exists():
                uv_bin = str(p)
                break

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
                    "path": str(PLUGIN_ROOT)
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
            # Update or append
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


def register_codex_config() -> None:
    print("\n⚙️  Configuring Codex settings in ~/.codex/config.toml...")
    codex_dir = Path.home() / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    config_file = codex_dir / "config.toml"

    req_file = (PLUGIN_ROOT / "server" / "requirements.txt").as_posix()
    launch_file = (PLUGIN_ROOT / "server" / "launch.py").as_posix()

    config_text = ""
    if config_file.exists():
        try:
            config_text = config_file.read_text(encoding="utf-8")
        except Exception:
            config_text = ""

    # Ensure [mcp_servers.auto-pilot] exists
    mcp_block = f"""
[mcp_servers.auto-pilot]
command = "uv"
args = ["run", "--with-requirements", "{req_file}", "--python", ">=3.10", "{launch_file}"]
enabled = true
startup_timeout_sec = 120
"""

    if "[mcp_servers.auto-pilot]" not in config_text:
        config_text += "\n" + mcp_block.strip() + "\n"
        config_file.write_text(config_text, encoding="utf-8")
        print(f"   ✓ Added [mcp_servers.auto-pilot] to {config_file}")
    else:
        print(f"   ✓ [mcp_servers.auto-pilot] already present in {config_file}")


def main() -> None:
    print("=" * 60)
    print("🚀 Setting up Oniesoft Auto-Pilot Plugin for Codex / ChatGPT")
    print("=" * 60)
    print(f"OS: {platform.system()} ({platform.release()})")
    print(f"Plugin Path: {PLUGIN_ROOT}")

    check_python_version()
    check_and_sync_dependencies()
    register_personal_marketplace()
    register_codex_config()

    print("\n" + "=" * 60)
    print("🎉 Plugin setup completed successfully!")
    print("=" * 60)
    print("\nNext Steps for Project Configuration:")
    print("1. In your project/workspace directory, add .env containing:")
    print("   PLATFORM_API_KEY=your-api-key")
    print("2. In your project/workspace directory, add config.json containing:")
    print("   {\"projectId\": \"...\", \"userId\": \"...\", \"companyId\": \"...\", \"platformApiUrl\": \"...\", \"backendUrl\": \"...\"}")
    print("3. Restart ChatGPT Desktop / Codex.")
    print("4. Open Plugins Directory -> My Local Plugins -> Install/Enable 'Oniesoft Auto-Pilot'.")
    print("5. Start a new chat and ask: 'get details of test case TC-10508 using get_test_cases_with_filters'")


if __name__ == "__main__":
    main()
