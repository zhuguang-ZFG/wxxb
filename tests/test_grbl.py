from __future__ import annotations

import pytest

from linktunnel.grbl.protocol import (
    is_response_done,
    is_status_line,
    preprocess_gcode_line,
    read_until_ok,
    send_line,
)
from linktunnel.grbl.status import parse_status_report


def test_preprocess_gcode_line() -> None:
    assert preprocess_gcode_line("  G0 X1  ") == "G0 X1"
    assert preprocess_gcode_line("; comment") is None
    assert preprocess_gcode_line("G1 Y2 ; tail") == "G1 Y2"
    assert preprocess_gcode_line("M3 (on) S1000") == "M3  S1000"


def test_parse_status_report() -> None:
    s = "<Idle|MPos:0.000,0.000,0.000|FS:0,0>"
    r = parse_status_report(s)
    assert r is not None
    assert r.state == "Idle"
    assert r.fields.get("MPos") == "0.000,0.000,0.000"
    assert parse_status_report("ok") is None


def test_is_status_and_done() -> None:
    assert is_status_line("<Idle|>")
    assert not is_status_line("ok")
    assert is_response_done("ok")
    assert is_response_done("error:10")


class _FakeSerial:
    timeout = 0

    def __init__(self, lines: list[bytes]) -> None:
        self._q = list(lines)
        self.written: list[bytes] = []

    def readline(self) -> bytes:
        if not self._q:
            return b""
        return self._q.pop(0)

    def write(self, data: bytes) -> int:
        self.written.append(data)
        return len(data)

    @property
    def in_waiting(self) -> int:
        return 1 if self._q else 0


def test_read_until_ok_skips_status() -> None:
    fake = _FakeSerial([b"<Idle|>\r\n", b"ok\r\n"])
    lines = read_until_ok(fake, timeout_s=1.0)
    assert lines == ["ok"]


def test_read_until_ok_with_status_echo() -> None:
    seen: list[str] = []

    def cb(s: str) -> None:
        seen.append(s)

    fake = _FakeSerial([b"<Idle|>\r\n", b"ok\r\n"])
    lines = read_until_ok(fake, timeout_s=1.0, echo_status=True, status_out=cb)
    assert lines == ["ok"]
    assert seen == ["<Idle|>"]


def test_send_line() -> None:
    fake = _FakeSerial([])
    send_line(fake, "G0")
    assert fake.written == [b"G0\r\n"]


def test_read_until_ok_timeout() -> None:
    fake = _FakeSerial([])
    with pytest.raises(TimeoutError):
        read_until_ok(fake, timeout_s=0.05)
