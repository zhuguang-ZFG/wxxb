from __future__ import annotations

import webbrowser
from urllib.parse import urlencode, urlparse

# 浏览器里用的在线面板（与 Mihomo External Controller 配合；若遇 CORS 可改用 --panel local）
YACD_META_ONLINE = "https://yacd.metacubex.one/"


def host_port_from_api_base(api_base: str) -> tuple[str, int]:
    """``http://127.0.0.1:9090`` -> ``("127.0.0.1", 9090)``."""
    u = urlparse(api_base.strip())
    host = u.hostname or "127.0.0.1"
    if u.port is not None:
        return host, u.port
    if u.scheme == "https":
        return host, 443
    return host, 9090


def yacd_meta_browser_url(api_base: str, secret: str) -> str:
    """Yacd（Meta / Mihomo 常用）在线页，带 hostname、port、secret。"""
    host, port = host_port_from_api_base(api_base)
    q: dict[str, str] = {"hostname": host, "port": str(port)}
    if secret:
        q["secret"] = secret
    return f"{YACD_META_ONLINE}?{urlencode(q)}"


def local_embedded_ui_url(api_base: str) -> str:
    """Mihomo 在配置 ``external-ui`` 并启动后，一般可访问 ``<api>/ui``。"""
    return f"{api_base.rstrip('/')}/ui"


def open_in_browser(url: str) -> None:
    webbrowser.open(url, new=1)
