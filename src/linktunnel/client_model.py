from __future__ import annotations

from typing import Any


def format_listen_line(cfg: dict[str, Any]) -> str:
    """从 ``GET /configs`` 摘要 mixed / HTTP / SOCKS 监听端口。"""
    parts: list[str] = []
    mp = cfg.get("mixed-port")
    if mp is not None and mp != 0:
        parts.append(f"mixed {mp}")
    p = cfg.get("port")
    if p is not None and p != 0:
        parts.append(f"http {p}")
    sp = cfg.get("socks-port")
    if sp is not None and sp != 0:
        parts.append(f"socks {sp}")
    return " · ".join(parts) if parts else "—"


def parse_selector_groups(proxies_payload: dict[str, Any]) -> list[tuple[str, str, list[str]]]:
    """
    From ``GET /proxies`` JSON, return rows: ``(group_name, current_now, all_outbounds)``.

    Only includes Selector / URLTest / Fallback / Relay (same filter as ``format_proxy_table``).
    """
    proxies = proxies_payload.get("proxies")
    if not isinstance(proxies, dict):
        return []
    rows: list[tuple[str, str, list[str]]] = []
    for name in sorted(proxies.keys()):
        info = proxies[name]
        if not isinstance(info, dict):
            continue
        ptype = str(info.get("type", ""))
        if ptype not in ("Selector", "URLTest", "Fallback", "Relay"):
            continue
        raw_all = info.get("all")
        names: list[str] = []
        if isinstance(raw_all, list):
            names = [str(x) for x in raw_all]
        now = str(info.get("now", ""))
        rows.append((name, now, names))
    return rows
