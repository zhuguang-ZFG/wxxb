from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml

_EMBED_UI_ZIP = "https://github.com/MetaCubeX/metacubexd/archive/refs/heads/gh-pages.zip"


def _apply_embed_ui(cfg: dict[str, Any], embed_ui: bool) -> None:
    """Mihomo 首次请求 ``/ui`` 时会拉取 MetaCubeXD 静态资源到工作目录。"""
    if not embed_ui:
        return
    cfg["external-ui"] = "ui"
    cfg["external-ui-url"] = _EMBED_UI_ZIP


def data_root() -> Path:
    """
    Per-user data directory (cross-platform).

    - Windows: ``%LOCALAPPDATA%\\linktunnel`` when set, else ``~\\.linktunnel``
    - macOS / Linux: ``~/.linktunnel``
    """
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / "linktunnel"
    return Path.home() / ".linktunnel"


def default_profile_dir() -> Path:
    return data_root() / "profiles" / "default"


def _ecc_to_http_api_base(ecc: str) -> str:
    """external-controller like ``127.0.0.1:9090`` -> ``http://127.0.0.1:9090``."""
    ecc = ecc.strip()
    if ecc.startswith("http://") or ecc.startswith("https://"):
        return ecc.rstrip("/")
    if ":" in ecc:
        host, port = ecc.rsplit(":", 1)
        host = host.strip() or "127.0.0.1"
        return f"http://{host}:{port.strip()}"
    return f"http://{ecc}:9090"


def external_controller_hints_from_config(config_path: Path) -> tuple[str, str]:
    """
    Read ``external-controller`` and ``secret`` from a Mihomo YAML for shell env hints.

    Returns ``(CLASH_API_value, secret)`` — CLASH_API_value is a full http(s) base URL.
    """
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return "http://127.0.0.1:9090", ""
    ecc = data.get("external-controller")
    secret = str(data.get("secret") or "")
    if ecc is None or str(ecc).strip() == "":
        return "http://127.0.0.1:9090", secret
    return _ecc_to_http_api_base(str(ecc)), secret


def build_config_with_subscription(
    subscription_url: str,
    *,
    mixed_port: int = 7890,
    external_controller: str = "127.0.0.1:9090",
    secret: str = "",
    provider_name: str = "nodes",
    embed_ui: bool = False,
) -> str:
    """Mihomo pulls nodes from HTTP(S) subscription; no Python-side parsing."""
    cfg: dict[str, Any] = {
        "mixed-port": mixed_port,
        "external-controller": external_controller,
        "secret": secret,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "proxy-providers": {
            provider_name: {
                "type": "http",
                "url": subscription_url,
                "path": f"./providers/{provider_name}.yaml",
                "interval": 3600,
                "health-check": {
                    "enable": True,
                    "url": "http://www.gstatic.com/generate_204",
                    "interval": 300,
                },
            }
        },
        "proxy-groups": [
            {
                "name": "PROXY",
                "type": "select",
                "use": [provider_name],
            }
        ],
        "rules": ["MATCH,PROXY"],
    }
    _apply_embed_ui(cfg, embed_ui)
    return yaml.safe_dump(
        cfg,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=120,
    )


def load_proxies_from_clash_file(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    proxies = data.get("proxies")
    if not isinstance(proxies, list) or not proxies:
        raise ValueError("file must contain a non-empty 'proxies' list (Clash format)")
    out: list[dict[str, Any]] = []
    for i, p in enumerate(proxies):
        if not isinstance(p, dict):
            raise ValueError(f"proxies[{i}] must be a mapping")
        pp = dict(p)
        pp.setdefault("name", f"imported-{i}")
        out.append(pp)
    return out


def build_config_with_proxy_list(
    proxies: list[dict[str, Any]],
    *,
    mixed_port: int = 7890,
    external_controller: str = "127.0.0.1:9090",
    secret: str = "",
    embed_ui: bool = False,
) -> str:
    """Static `proxies:` from an imported Clash YAML fragment."""
    names = [str(p.get("name", f"n{i}")) for i, p in enumerate(proxies)]
    cfg: dict[str, Any] = {
        "mixed-port": mixed_port,
        "external-controller": external_controller,
        "secret": secret,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "PROXY",
                "type": "select",
                "proxies": names,
            }
        ],
        "rules": ["MATCH,PROXY"],
    }
    _apply_embed_ui(cfg, embed_ui)
    return yaml.safe_dump(
        cfg,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=120,
    )
