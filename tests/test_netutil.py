from __future__ import annotations

import pytest

from linktunnel.netutil import parse_host_port


def test_parse_ipv4() -> None:
    assert parse_host_port("127.0.0.1:80") == ("127.0.0.1", 80)


def test_parse_wildcard() -> None:
    assert parse_host_port(":9000") == ("0.0.0.0", 9000)


def test_parse_ipv6() -> None:
    assert parse_host_port("[::1]:8080") == ("::1", 8080)
    assert parse_host_port("[2001:db8::1]:443") == ("2001:db8::1", 443)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "nocolon",
        "host:",
        ":0",
        ":65536",
        "[::1]",
        "[::1]port",
    ],
)
def test_parse_errors(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_host_port(bad)
