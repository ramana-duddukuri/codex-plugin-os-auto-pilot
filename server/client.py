"""Thin async HTTP client over the two Oniesoft backends.

The MCP server holds NO business logic — every tool is a typed wrapper around a
REST call to either:
  * the platform API (agentic_ai_be, generation + analysis), or
  * the execution API (python_tool, runs).

Auth is a single per-user API key sent as the ``x-api-key`` header (the backend's
existing convention), read from the environment (.env / PLATFORM_API_KEY).
Project details (projectId, userId, companyId, platformApiUrl, backendUrl) are
read from the user's project-level config.json.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

_DATA_DIR = os.environ.get("ONIESOFT_DATA_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".data"
)
_SHARED_CONFIG_PATH = os.path.join(_DATA_DIR, "active_project.json")


def _read_shared_config() -> dict:
    try:
        with open(_SHARED_CONFIG_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def platform_api_url() -> str:
    url = os.environ.get("PLATFORM_API_URL") or _read_shared_config().get("platformApiUrl") or "http://localhost:8000"
    return url.rstrip("/")


def backend_url() -> str:
    url = os.environ.get("BACKEND_URL") or _read_shared_config().get("backendUrl") or "http://localhost:8088"
    return url.rstrip("/")


def api_key() -> str:
    return os.environ.get("PLATFORM_API_KEY", "")


def default_project_id() -> str | None:
    """Project ID from env/config.json, falling back to the shared active-project snapshot."""
    return os.environ.get("PLATFORM_PROJECT_ID") or _read_shared_config().get("projectId")


def default_user_id() -> str | None:
    """User ID from env/config.json, falling back to the shared active-project snapshot."""
    return os.environ.get("PLATFORM_USER_ID") or _read_shared_config().get("userId")


def default_company_id() -> str | None:
    """Company ID from env/config.json, falling back to the shared active-project snapshot."""
    return os.environ.get("PLATFORM_COMPANY_ID") or _read_shared_config().get("companyId")


_TIMEOUT = httpx.Timeout(connect=10.0, read=300.0, write=30.0, pool=10.0)

_client: httpx.AsyncClient | None = None


def _headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    key = api_key()
    if key:
        headers["x-api-key"] = key
    return headers


def get_client() -> httpx.AsyncClient:
    """Lazily create one shared AsyncClient for the process."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=_TIMEOUT, headers=_headers())
    return _client


async def aclose() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _result(resp: httpx.Response) -> dict[str, Any]:
    """Normalize any response into a JSON-able dict the model can read."""
    body: Any
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    return {"status_code": resp.status_code, "ok": resp.is_success, "data": body}


async def post_platform(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    resp = await get_client().post(f"{platform_api_url()}{path}", json=payload)
    return _result(resp)


async def get_platform(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    resp = await get_client().get(f"{platform_api_url()}{path}", params=params)
    return _result(resp)


async def post_backend(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    resp = await get_client().post(f"{backend_url()}{path}", json=payload)
    return _result(resp)


async def post_backend_multipart(
    path: str, data: dict[str, Any], files: dict[str, tuple[str, bytes, str]]
) -> dict[str, Any]:
    resp = await get_client().post(f"{backend_url()}{path}", data=data, files=files)
    return _result(resp)


async def get_backend(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    resp = await get_client().get(f"{backend_url()}{path}", params=params)
    return _result(resp)


async def patch_backend(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    resp = await get_client().patch(f"{backend_url()}{path}", json=payload)
    return _result(resp)


async def put_backend(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    resp = await get_client().put(f"{backend_url()}{path}", json=payload)
    return _result(resp)
