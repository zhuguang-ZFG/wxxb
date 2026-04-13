from __future__ import annotations

from io import StringIO

from linktunnel.logfmt import log_line


def test_log_line_text() -> None:
    buf = StringIO()
    log_line(buf, "dir", b"a\nb", hex_mode=False)
    s = buf.getvalue()
    assert "dir" in s
    assert "3 B" in s
    assert "\\n" in s


def test_log_line_hex() -> None:
    buf = StringIO()
    log_line(buf, "x", b"\x01\x02", hex_mode=True)
    assert "0102" in buf.getvalue()
