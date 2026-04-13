from __future__ import annotations

import re
import time
from typing import Protocol

# Grbl realtime (single byte, no line ending) — see gnea/grbl wiki
REALTIME_STATUS = b"?"  # status report
REALTIME_RESET = b"\x18"  # soft reset Ctrl+X
REALTIME_HOLD = b"!"  # feed hold
REALTIME_RESUME = b"~"  # cycle start / resume
REALTIME_DOOR = b"\x84"  # safety door (Grbl 1.1)


class SerialLike(Protocol):
    def readline(self) -> bytes: ...

    def write(self, data: bytes) -> int: ...

    @property
    def in_waiting(self) -> int: ...


_PAREN_COMMENT = re.compile(r"\([^()]*\)")


def preprocess_gcode_line(line: str) -> str | None:
    """Strip whitespace, full-line / semicolon / parenthesis comments. Returns None to skip."""
    s = line.strip()
    if not s:
        return None
    if s.startswith(";"):
        return None
    while True:
        ns = _PAREN_COMMENT.sub("", s)
        if ns == s:
            break
        s = ns.strip()
        if not s:
            return None
    if ";" in s:
        s = s.split(";", 1)[0].strip()
    if not s:
        return None
    return s


def is_status_line(text: str) -> bool:
    t = text.strip()
    return len(t) >= 2 and t[0] == "<" and t[-1] == ">"


def is_response_done(text: str) -> bool:
    tl = text.strip().lower()
    return tl == "ok" or tl.startswith("error:")


def read_until_ok(
    ser: SerialLike,
    *,
    timeout_s: float,
    echo_status: bool = False,
    status_out=None,
) -> list[str]:
    """Read lines until ``ok`` or ``error:`` (ignoring ``<...>`` status lines unless echo_status)."""
    out: list[str] = []
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        raw = ser.readline()
        if not raw:
            # Non-blocking readline (timeout==0) returns immediately; avoid a tight loop.
            if getattr(ser, "timeout", None) == 0:
                time.sleep(0.001)
            continue
        text = raw.decode("utf-8", errors="replace").strip("\r\n")
        if not text:
            continue
        if is_status_line(text):
            if echo_status:
                if status_out is not None:
                    status_out(text)
            continue
        out.append(text)
        if is_response_done(text):
            return out
    raise TimeoutError(f"no ok/error within {timeout_s}s; last lines: {out[-5:]}")


def send_line(ser: SerialLike, line: str, *, ending: str = "\r\n") -> None:
    ser.write((line + ending).encode("utf-8"))
