from __future__ import annotations

from linktunnel.dashboard_open import (
    host_port_from_api_base,
    local_embedded_ui_url,
    yacd_meta_browser_url,
)


def test_host_port_from_api_base() -> None:
    assert host_port_from_api_base("http://127.0.0.1:9090") == ("127.0.0.1", 9090)


def test_yacd_meta_url_has_query() -> None:
    u = yacd_meta_browser_url("http://127.0.0.1:9090", "s3cret")
    assert "yacd.metacubex.one" in u
    assert "127.0.0.1" in u
    assert "9090" in u
    assert "secret" in u


def test_local_ui_url() -> None:
    assert local_embedded_ui_url("http://127.0.0.1:9090") == "http://127.0.0.1:9090/ui"
