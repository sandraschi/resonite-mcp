"""
Resonite REST API Tools — portmanteau for api.resonite.com endpoints.

Implements: authentication, sessions, user lookup, records/inventory browser,
and signalR message sending (for in-session GLB URL delivery).

Based on: https://wiki.resonite.com/API (last updated 2026-01-02)
Main URL: https://api.resonite.com/
Assets:   https://assets.resonite.com/
"""

from __future__ import annotations

import hashlib
import os
import uuid
import logging
from typing import Any, Dict, Optional

import httpx

try:
    from ..server import server
except ImportError:
    server = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

RESONITE_API = "https://api.resonite.com"

# In-process token store (resets on server restart; use env var as fallback)
_token_store: Dict[str, str] = {}  # {"user_id": ..., "token": ...}


def _auth_headers() -> dict[str, str]:
    """Build Authorization header from stored or env token."""
    user_id = _token_store.get("user_id") or os.getenv("RESONITE_USER_ID", "")
    token = _token_store.get("token") or os.getenv("RESONITE_TOKEN", "")
    if not (user_id and token):
        return {}
    return {"Authorization": f"res {user_id}:{token}"}


# ── Authentication ────────────────────────────────────────────────────────────


async def resonite_rest_login(
    username: str,
    password: str,
    remember_me: bool = True,
) -> Dict[str, Any]:
    """Log in to the Resonite API and store the session token.

    Args:
        username: Your Resonite username or email.
        password: Your Resonite password.
        remember_me: If True, token valid 30 days; otherwise 24 hours.

    Returns:
        Session details including user_id and token (stored for subsequent calls).

    Examples:
        >>> await resonite_rest_login("MyUser", "hunter2")
        {"status": "ok", "user_id": "U-...", "token": "...", "expires": "..."}
    """
    uid_hash = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    body = {
        "username": username,
        "authentication": {"$type": "password", "password": password},
        "secretMachineId": str(uuid.uuid4()),
        "rememberMe": remember_me,
    }
    headers = {
        "Content-Type": "application/json",
        "UID": uid_hash,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(f"{RESONITE_API}/userSessions", json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            user_id = data.get("userId", "")
            token = data.get("token", "")
            _token_store["user_id"] = user_id
            _token_store["token"] = token
            return {
                "status": "ok",
                "user_id": user_id,
                "token": token,
                "remember_me": remember_me,
                "raw": data,
            }
    except httpx.HTTPStatusError as e:
        return {"status": "error", "detail": str(e), "response": e.response.text}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Sessions ──────────────────────────────────────────────────────────────────


async def resonite_rest_get_sessions(
    name: Optional[str] = None,
    host_name: Optional[str] = None,
    host_id: Optional[str] = None,
    min_active_users: int = 0,
    include_empty_headless: bool = True,
) -> Dict[str, Any]:
    """List public Resonite world sessions.

    Does not require authentication.

    Args:
        name: Filter by session name (partial match).
        host_name: Filter by host's username.
        host_id: Filter by host's user ID (starts with U-).
        min_active_users: Minimum number of active users.
        include_empty_headless: Include empty headless servers.

    Returns:
        List of public sessions.

    Examples:
        >>> await resonite_rest_get_sessions(name="WorldLabs")
        {"status": "ok", "sessions": [...], "count": 3}
    """
    params: dict[str, Any] = {
        "minActiveUsers": min_active_users,
        "includeEmptyHeadless": str(include_empty_headless).lower(),
    }
    if name:
        params["name"] = name
    if host_name:
        params["hostName"] = host_name
    if host_id:
        params["hostId"] = host_id

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{RESONITE_API}/sessions", params=params)
            resp.raise_for_status()
            sessions = resp.json()
            return {"status": "ok", "sessions": sessions, "count": len(sessions)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Users ─────────────────────────────────────────────────────────────────────


async def resonite_rest_get_user(username_or_id: str) -> Dict[str, Any]:
    """Look up a Resonite user by username or user ID.

    Args:
        username_or_id: Username or user ID (U-...). Automatically detects format.

    Returns:
        User profile object.

    Examples:
        >>> await resonite_rest_get_user("Frooxius")
        {"status": "ok", "user": {"id": "U-...", "username": "Frooxius", ...}}
    """
    by_username = not username_or_id.startswith("U-")
    params = {"byUsername": "true"} if by_username else {}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{RESONITE_API}/users/{username_or_id}",
                params=params,
                headers=_auth_headers(),
            )
            resp.raise_for_status()
            return {"status": "ok", "user": resp.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "http_status": e.response.status_code, "detail": e.response.text}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Records / Inventory ───────────────────────────────────────────────────────


async def resonite_rest_get_records(
    user_id: Optional[str] = None,
    path: Optional[str] = None,
    record_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Browse a user's Resonite inventory records.

    Requires authentication (resonite_rest_login first, or RESONITE_USER_ID + RESONITE_TOKEN env vars).

    Args:
        user_id: User ID (U-...). Defaults to authenticated user.
        path: Inventory path to list (e.g. 'Inventory/WorldLabs').
              Omit to list root.
        record_id: If provided, fetch a single record (R-...).

    Returns:
        Records at the specified path.

    Examples:
        >>> await resonite_rest_get_records(path="Inventory")
        {"status": "ok", "records": [...], "count": 12}
    """
    auth = _auth_headers()
    if not auth:
        return {"status": "error", "detail": "Not authenticated. Call resonite_rest_login first."}

    uid = user_id or _token_store.get("user_id", "")
    if not uid:
        return {"status": "error", "detail": "user_id unknown — pass explicitly or login first."}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            if record_id:
                url = f"{RESONITE_API}/users/{uid}/records/{record_id}"
                resp = await client.get(url, headers=auth)
                resp.raise_for_status()
                return {"status": "ok", "record": resp.json()}
            elif path:
                url = f"{RESONITE_API}/users/{uid}/records"
                resp = await client.get(url, params={"path": path}, headers=auth)
                resp.raise_for_status()
                records = resp.json()
                return {"status": "ok", "records": records, "count": len(records), "path": path}
            else:
                url = f"{RESONITE_API}/users/{uid}/records/root"
                resp = await client.get(url, headers=auth)
                resp.raise_for_status()
                records = resp.json()
                return {"status": "ok", "records": records, "count": len(records), "path": "root"}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "http_status": e.response.status_code, "detail": e.response.text}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Messages ──────────────────────────────────────────────────────────────────


async def resonite_rest_send_message(
    target_user_id: str,
    message: str,
) -> Dict[str, Any]:
    """Send a chat message to a Resonite user via the REST API.

    Useful for sending a World Labs GLB/SPZ URL to yourself or a collaborator
    so it can be imported inside Resonite by dragging the link.

    Requires authentication.

    Args:
        target_user_id: The recipient's user ID (U-...).
        message: The message text. For asset import, use the signed asset URL.

    Returns:
        Confirmation of the sent message.

    Examples:
        >>> await resonite_rest_send_message("U-Frooxius", "https://cdn.worldlabs.ai/.../world.glb")
        {"status": "ok", "message_id": "M-..."}
    """
    auth = _auth_headers()
    if not auth:
        return {"status": "error", "detail": "Not authenticated. Call resonite_rest_login first."}

    sender_id = _token_store.get("user_id", "")
    body = {
        "id": f"M-{uuid.uuid4()}",
        "senderId": sender_id,
        "recipientId": target_user_id,
        "messageType": "Text",
        "content": message,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{RESONITE_API}/users/{target_user_id}/messages",
                json=body,
                headers={**_auth_headers(), "Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return {"status": "ok", "detail": "Message sent", "body": body}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "http_status": e.response.status_code, "detail": e.response.text}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Platform info ─────────────────────────────────────────────────────────────


async def resonite_rest_get_platform() -> Dict[str, Any]:
    """Get Resonite platform/server information.

    Does not require authentication.

    Returns:
        Platform info including build version and status.

    Examples:
        >>> await resonite_rest_get_platform()
        {"status": "ok", "platform": {"version": "...", ...}}
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{RESONITE_API}/platform")
            resp.raise_for_status()
            return {"status": "ok", "platform": resp.json()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── Register tools ────────────────────────────────────────────────────────────

if server is not None:
    server.tool()(resonite_rest_login)
    server.tool()(resonite_rest_get_sessions)
    server.tool()(resonite_rest_get_user)
    server.tool()(resonite_rest_get_records)
    server.tool()(resonite_rest_send_message)
    server.tool()(resonite_rest_get_platform)
