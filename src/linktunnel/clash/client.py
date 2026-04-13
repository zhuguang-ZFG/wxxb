from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import quote, urlencode


class ClashApiError(Exception):
    """Raised when the External Controller returns a non-2xx response."""

    def __init__(self, code: int, body: str) -> None:
        self.code = code
        self.body = body
        snippet = body[:300] + ("…" if len(body) > 300 else "")
        super().__init__(f"HTTP {code}: {snippet}")


def clash_request(
    base_url: str,
    method: str,
    path: str,
    *,
    secret: str | None = None,
    json_body: dict[str, Any] | list[Any] | None = None,
    timeout: float = 20.0,
) -> Any | None:
    """Call External Controller REST API. ``path`` must start with ``/``."""
    url = base_url.rstrip("/") + path
    data: bytes | None = None
    headers: dict[str, str] = {}
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            if not raw.strip():
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise ClashApiError(e.code, body) from e


def clash_get(
    base_url: str, path: str, *, secret: str | None = None, timeout: float = 20.0
) -> Any | None:
    return clash_request(base_url, "GET", path, secret=secret, timeout=timeout)


def clash_patch(
    base_url: str,
    path: str,
    body: dict[str, Any],
    *,
    secret: str | None = None,
    timeout: float = 20.0,
) -> Any | None:
    return clash_request(base_url, "PATCH", path, secret=secret, json_body=body, timeout=timeout)


def clash_put(
    base_url: str,
    path: str,
    body: dict[str, Any],
    *,
    secret: str | None = None,
    timeout: float = 20.0,
) -> Any | None:
    return clash_request(base_url, "PUT", path, secret=secret, json_body=body, timeout=timeout)


def clash_delete(
    base_url: str,
    path: str,
    *,
    secret: str | None = None,
    timeout: float = 20.0,
) -> Any | None:
    return clash_request(base_url, "DELETE", path, secret=secret, timeout=timeout)


def proxy_path_segment(name: str) -> str:
    """URL-encode a proxy or group name for use in ``/proxies/{name}``."""
    return quote(name, safe="")


def proxy_delay_path(proxy_name: str, test_url: str, timeout_ms: int) -> str:
    """Path + query for ``GET /proxies/{name}/delay`` (Mihomo / Clash Meta)."""
    q = urlencode({"url": test_url, "timeout": str(int(timeout_ms))})
    return f"/proxies/{proxy_path_segment(proxy_name)}/delay?{q}"


def format_proxy_table(data: dict[str, Any]) -> str:
    """Turn ``GET /proxies`` JSON into a short text table."""
    proxies = data.get("proxies")
    if not isinstance(proxies, dict):
        return "(no proxies object in response)"
    rows: list[tuple[str, str, str, str]] = []
    for name in sorted(proxies.keys()):
        info = proxies[name]
        if not isinstance(info, dict):
            continue
        ptype = str(info.get("type", ""))
        if ptype not in ("Selector", "URLTest", "Fallback", "Relay"):
            continue
        now = str(info.get("now", ""))
        delay = info.get("history")
        delay_s = ""
        if isinstance(delay, list) and delay:
            last = delay[-1]
            if isinstance(last, dict) and "delay" in last:
                delay_s = str(last.get("delay", ""))
        rows.append((name, ptype, now, delay_s))
    if not rows:
        return "(no Selector/URLTest/Fallback groups found)"
    w = max(len(r[0]) for r in rows)
    lines = [f"{'GROUP':<{w}}  {'TYPE':<10}  {'NOW':<24}  DELAY(ms)"]
    lines.append("-" * (w + 10 + 24 + 12))
    for name, ptype, now, d in rows:
        lines.append(f"{name:<{w}}  {ptype:<10}  {now:<24}  {d}")
    return "\n".join(lines)
