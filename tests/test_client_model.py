from __future__ import annotations

from linktunnel.client_model import format_listen_line, parse_selector_groups


def test_parse_selector_groups_sorts_and_filters() -> None:
    payload = {
        "proxies": {
            "Z": {"type": "Selector", "now": "n1", "all": ["n1", "n2"]},
            "A": {"type": "Selector", "now": "x", "all": ["x"]},
            "DIRECT": {"type": "Direct"},
        }
    }
    rows = parse_selector_groups(payload)
    assert rows == [("A", "x", ["x"]), ("Z", "n1", ["n1", "n2"])]


def test_parse_selector_groups_empty() -> None:
    assert parse_selector_groups({}) == []
    assert parse_selector_groups({"proxies": None}) == []


def test_format_listen_line() -> None:
    assert format_listen_line({}) == "—"
    assert "mixed 7890" in format_listen_line({"mixed-port": 7890})
    assert "http 8080" in format_listen_line({"port": 8080})
    assert "socks 1080" in format_listen_line({"socks-port": 1080})
