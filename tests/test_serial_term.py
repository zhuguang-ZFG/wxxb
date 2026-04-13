from __future__ import annotations

import pytest

from linktunnel.serial_term import (
    codec_decode,
    codec_encode,
    eol_bytes,
    parse_hex_input_line,
    pop_serial_text_line,
    validate_term_options,
)


def test_eol_bytes() -> None:
    assert eol_bytes("lf") == b"\n"
    assert eol_bytes("crlf") == b"\r\n"
    assert eol_bytes("none") == b""


def test_parse_hex_input_line() -> None:
    assert parse_hex_input_line("") == b""
    assert parse_hex_input_line("aa bb cc") == bytes([0xAA, 0xBB, 0xCC])
    assert parse_hex_input_line("aabbcc") == bytes([0xAA, 0xBB, 0xCC])
    assert parse_hex_input_line("01:02:03") == bytes([1, 2, 3])


def test_pop_serial_text_line() -> None:
    b = bytearray(b"line1\r\nline2\nx\ry")
    assert pop_serial_text_line(b) == b"line1"
    assert bytes(b) == b"line2\nx\ry"
    assert pop_serial_text_line(b) == b"line2"
    assert pop_serial_text_line(b) == b"x"
    assert pop_serial_text_line(b) is None
    b.append(ord("\n"))
    assert pop_serial_text_line(b) == b"y"


def test_parse_hex_input_line_invalid() -> None:
    with pytest.raises(ValueError):
        parse_hex_input_line("zzz")
    with pytest.raises(ValueError):
        parse_hex_input_line("a")


def test_validate_term_options() -> None:
    validate_term_options(
        hex_display=False,
        timestamp=False,
        timestamp_ms=False,
        raw_rx=False,
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        validate_term_options(
            hex_display=True,
            timestamp=False,
            timestamp_ms=False,
            raw_rx=True,
            encoding="utf-8",
        )
    with pytest.raises(ValueError):
        validate_term_options(
            hex_display=False,
            timestamp=True,
            timestamp_ms=False,
            raw_rx=True,
            encoding="utf-8",
        )
    with pytest.raises(ValueError):
        validate_term_options(
            hex_display=False,
            timestamp=False,
            timestamp_ms=False,
            raw_rx=True,
            encoding="gbk",
        )


def test_codec_gbk_roundtrip() -> None:
    s = "中文测试"
    b = codec_encode("gbk", s)
    assert codec_decode("gbk", b) == s


def test_codec_ascii_replace() -> None:
    t = codec_decode("ascii", b"\xff")
    assert len(t) == 1 and ord(t) == 0xFFFD
