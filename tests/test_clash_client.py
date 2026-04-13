from __future__ import annotations

import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from linktunnel.clash.client import (
    ClashApiError,
    clash_delete,
    clash_get,
    clash_request,
    format_proxy_table,
    proxy_delay_path,
    proxy_path_segment,
)


class _Resp:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _Resp:
        return self

    def __exit__(self, *a: object) -> None:
        return None


def test_clash_get_ok() -> None:
    payload = {"version": "v1.0"}
    with patch("urllib.request.urlopen", return_value=_Resp(json.dumps(payload).encode())):
        assert clash_get("http://127.0.0.1:9090", "/version", secret="s") == payload


def test_clash_api_error() -> None:
    def raise_http(*a: object, **k: object) -> None:
        raise urllib.error.HTTPError(
            "http://h",
            401,
            "Unauthorized",
            {},
            io.BytesIO(b'{"message":"unauthorized"}'),
        )

    with patch("urllib.request.urlopen", side_effect=raise_http):
        with pytest.raises(ClashApiError) as ei:
            clash_request("http://h", "GET", "/x", secret=None)
        assert ei.value.code == 401


def test_proxy_path_segment() -> None:
    assert proxy_path_segment("🔥") != "🔥"
    assert "/" not in proxy_path_segment("a/b")


def test_proxy_delay_path() -> None:
    p = proxy_delay_path("GROUP", "http://www.gstatic.com/generate_204", 5000)
    assert p.startswith("/proxies/")
    assert "delay" in p
    assert "generate_204" in p


def test_clash_delete_calls_request() -> None:
    with patch("linktunnel.clash.client.clash_request", return_value=None) as m:
        clash_delete("http://127.0.0.1:9090", "/connections", secret="s")
    m.assert_called_once()
    assert m.call_args[0][1] == "DELETE"


def test_format_proxy_table() -> None:
    data = {
        "proxies": {
            "DIRECT": {"type": "Direct"},
            "G": {
                "type": "Selector",
                "now": "n1",
                "history": [{"delay": 42}],
            },
        }
    }
    out = format_proxy_table(data)
    assert "G" in out
    assert "Selector" in out
    assert "n1" in out
    assert "42" in out
