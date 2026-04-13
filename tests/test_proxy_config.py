from __future__ import annotations

from pathlib import Path

import yaml

from linktunnel.proxy.mihomo_config import (
    build_config_with_proxy_list,
    build_config_with_subscription,
    external_controller_hints_from_config,
    load_proxies_from_clash_file,
)


def test_build_config_with_subscription() -> None:
    s = build_config_with_subscription("https://example.com/sub")
    d = yaml.safe_load(s)
    assert d["mixed-port"] == 7890
    assert d["proxy-providers"]["nodes"]["url"] == "https://example.com/sub"
    assert "PROXY" in str(d["proxy-groups"])
    assert "external-ui" not in d


def test_build_config_embed_ui() -> None:
    s = build_config_with_subscription("https://example.com/sub", embed_ui=True)
    d = yaml.safe_load(s)
    assert d.get("external-ui") == "ui"
    assert "external-ui-url" in d


def test_build_config_with_proxy_list() -> None:
    proxies = [
        {"name": "a", "type": "ss", "server": "1.1.1.1", "port": 1, "cipher": "x", "password": "p"}
    ]
    s = build_config_with_proxy_list(proxies)
    d = yaml.safe_load(s)
    assert d["proxies"][0]["name"] == "a"
    assert d["proxy-groups"][0]["proxies"] == ["a"]


def test_external_controller_hints_from_config(tmp_path: Path) -> None:
    p = tmp_path / "c.yaml"
    p.write_text(
        """
mixed-port: 7890
external-controller: 127.0.0.1:9090
secret: "x"
""",
        encoding="utf-8",
    )
    api, sec = external_controller_hints_from_config(p)
    assert api == "http://127.0.0.1:9090"
    assert sec == "x"


def test_load_proxies_from_clash_file(tmp_path: Path) -> None:
    p = tmp_path / "p.yaml"
    p.write_text(
        """
proxies:
  - name: n1
    type: direct
""",
        encoding="utf-8",
    )
    xs = load_proxies_from_clash_file(p)
    assert xs[0]["name"] == "n1"
