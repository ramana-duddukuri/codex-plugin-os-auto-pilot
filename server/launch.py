"""Launch the Oniesoft MCP server over stdio or Streamable HTTP.

Codex runs this via ``uv run --with-requirements server/requirements.txt``,
which resolves/installs a compatible Python and dependencies before handing off
here — cross-platform, with no bespoke venv-bootstrap code needed in this file.

Workspace-level credentials (PLATFORM_API_KEY in .env) and project settings
(company/user/project ID, API URLs in config.json) are read from the user's
active project directory, never from the plugin directory.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import MutableMapping

# Ensure UTF-8 on Windows stdin/stdout/stderr for clean JSON-RPC communication
if sys.platform == "win32":
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ${CODEX_PLUGIN_DATA} / ${ONIESOFT_DATA_DIR} is exported to plugin subprocesses
# where available; fall back to a local dir so a plain checkout still works.
DATA_DIR = (
    os.environ.get("CODEX_PLUGIN_DATA")
    or os.environ.get("ONIESOFT_DATA_DIR")
    or os.environ.get("CURSOR_PLUGIN_DATA")
    or os.environ.get("CLAUDE_PLUGIN_DATA")
    or os.path.join(PLUGIN_ROOT, ".data")
)

SNAPSHOT_PATH = os.path.join(DATA_DIR, "active_project.json")


def _read_snapshot() -> dict:
    try:
        with open(SNAPSHOT_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _write_snapshot(updates: dict) -> None:
    """Merge `updates` into the shared snapshot, never dropping existing keys.

    Merging rather than overwriting matters because the two writers below run in
    different situations: a workspace with only a ``.env`` records just the
    directory, while one with a ``config.json`` also records the IDs.
    """
    if not updates:
        return
    snapshot = _read_snapshot()
    snapshot.update(updates)
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SNAPSHOT_PATH, "w", encoding="utf-8") as fh:
            json.dump(snapshot, fh)
    except Exception:
        pass


def _inject_project_config(env: MutableMapping[str, str], project_dir: str) -> None:
    """Read the project's config.json (in the user's workspace — not the plugin
    directory) and inject company/user/project ID and API URLs.

    These values are per-project, not per-user plugin settings, so they live in a
    config.json that ships with the project folder itself rather than in the
    plugin's own configuration.
    """
    if os.path.abspath(project_dir) == os.path.abspath(PLUGIN_ROOT):
        return

    field_env_map = {
        "apiKey": "PLATFORM_API_KEY",
        "api_key": "PLATFORM_API_KEY",
        "platformApiKey": "PLATFORM_API_KEY",
        "platform_api_key": "PLATFORM_API_KEY",
        "companyId": "PLATFORM_COMPANY_ID",
        "company_id": "PLATFORM_COMPANY_ID",
        "userId": "PLATFORM_USER_ID",
        "user_id": "PLATFORM_USER_ID",
        "projectId": "PLATFORM_PROJECT_ID",
        "project_id": "PLATFORM_PROJECT_ID",
        "platformApiUrl": "PLATFORM_API_URL",
        "platform_api_url": "PLATFORM_API_URL",
        "backendUrl": "BACKEND_URL",
        "backend_url": "BACKEND_URL",
    }

    project_config = os.path.join(project_dir, "config.json")
    try:
        with open(project_config, encoding="utf-8") as fh:
            config = json.load(fh)
    except Exception:
        return

    for field, env_var in field_env_map.items():
        val = config.get(field)
        if val and not env.get(env_var):
            env[env_var] = str(val)

    # Persist a fixed-location snapshot of the per-project IDs so server
    # instances spawned WITHOUT workspace context can still resolve them at
    # request time.
    snapshot = {
        key: config[key]
        for key in ("projectId", "userId", "companyId", "platformApiUrl", "backendUrl")
        if config.get(key)
    }
    if snapshot.get("projectId"):
        _write_snapshot(snapshot)


#: Settings that may come from the workspace .env.
_OVERRIDABLE = ("PLATFORM_API_KEY", "PLATFORM_API_URL", "BACKEND_URL")


def _is_placeholder(val: str) -> bool:
    """True if `val` is an unsubstituted ``${VAR}`` template rather than a value."""
    return val.startswith("${") and val.endswith("}")


def _promote_configured(env: MutableMapping[str, str]) -> None:
    """Move real ``CONFIGURED_*`` values onto their plain names, highest priority."""
    for name in _OVERRIDABLE:
        configured = env.pop(f"CONFIGURED_{name}", "")
        if configured and not _is_placeholder(configured):
            env[name] = configured


def _load_env_file(env: MutableMapping[str, str], project_dir: str) -> None:
    """Fill any still-unset setting from the workspace's ``.env``."""
    if os.path.abspath(project_dir) == os.path.abspath(PLUGIN_ROOT):
        return

    path = os.path.join(project_dir, ".env")
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except Exception:
        return

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'\"")
        if not val or _is_placeholder(val):
            continue
        if key not in _OVERRIDABLE:
            continue
        if not env.get(key):
            env[key] = val


def _strip_unresolved(env: MutableMapping[str, str]) -> None:
    """Drop env vars still holding an unsubstituted ``${VAR}`` placeholder."""
    for key, val in list(env.items()):
        if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
            del env[key]


def _has_project_files(path: str) -> bool:
    """True if `path` looks like a configured workspace for this plugin."""
    return os.path.isfile(os.path.join(path, ".env")) or os.path.isfile(
        os.path.join(path, "config.json")
    )


def _resolve_project_dir() -> str:
    """Locate the workspace holding this project's ``.env`` / ``config.json``.

    Expands ``~`` first, then checks configured env vars, cwd, and falls back to
    the last directory recorded in active_project.json.
    """
    project_dir = os.path.expanduser(
        os.environ.get("CODEX_PROJECT_DIR")
        or os.environ.get("ONIESOFT_PROJECT_DIR")
        or os.environ.get("CURSOR_PROJECT_DIR")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or os.getcwd()
    )

    if _has_project_files(project_dir):
        _write_snapshot({"workspaceDir": project_dir})
        return project_dir

    recorded = _read_snapshot().get("workspaceDir")
    if recorded and _has_project_files(recorded):
        return recorded

    return project_dir


def main() -> None:
    if "--bootstrap-only" in sys.argv[1:]:
        # `uv run` has already synced the environment by the time this code
        # runs; nothing further to do.
        return

    # Precedence, highest first: Process/System Env > workspace .env > config.json.
    _promote_configured(os.environ)
    _strip_unresolved(os.environ)

    project_dir = _resolve_project_dir()
    _load_env_file(os.environ, project_dir)
    _inject_project_config(os.environ, project_dir)

    if not os.environ.get("PLATFORM_API_KEY"):
        # Fail loudly here rather than let every tool call come back 403 with no
        # hint that the cause is configuration rather than permissions.
        print(
            "auto-pilot: no PLATFORM_API_KEY configured. Add "
            f"PLATFORM_API_KEY=... to {os.path.join(project_dir, '.env')}",
            file=sys.stderr,
        )

    sys.path.insert(0, PLUGIN_ROOT)
    os.chdir(PLUGIN_ROOT)
    from server.tools import mcp  # noqa: E402

    transport = "streamable-http" if "--transport" in sys.argv[1:] else "stdio"
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
