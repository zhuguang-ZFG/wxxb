from __future__ import annotations

from collections.abc import Callable, Iterator

import serial

from linktunnel.grbl.protocol import preprocess_gcode_line, read_until_ok, send_line


def iter_gcode_lines(path: str) -> Iterator[str]:
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            prep = preprocess_gcode_line(line)
            if prep is not None:
                yield prep


def stream_gcode_file(
    ser: serial.Serial,
    path: str,
    *,
    timeout_per_line: float,
    on_send: Callable[[str], None] | None = None,
    on_rx: Callable[[str], None] | None = None,
    on_error: Callable[[str, list[str]], None] | None = None,
) -> int:
    """
    Send each non-empty G-code line and wait for ok/error.
    Returns 0 on success, 1 if any line got ``error:``.
    """
    errors = 0
    for line in iter_gcode_lines(path):
        if on_send:
            on_send(line)
        send_line(ser, line)
        ser.flush()
        lines = read_until_ok(
            ser,
            timeout_s=timeout_per_line,
            echo_status=on_rx is not None,
            status_out=on_rx,
        )
        for ln in lines:
            if on_rx:
                on_rx(ln)
        last = lines[-1].strip().lower() if lines else ""
        if last.startswith("error:"):
            errors += 1
            if on_error:
                on_error(line, lines)
    return 1 if errors else 0
