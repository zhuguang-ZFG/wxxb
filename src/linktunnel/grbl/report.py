from __future__ import annotations

import time

import serial

from linktunnel.grbl.protocol import is_status_line, read_until_ok, send_line


def read_status_line(ser: serial.Serial, *, timeout_s: float = 2.0) -> str:
    ser.write(b"?")
    ser.flush()
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        raw = ser.readline()
        if not raw:
            if getattr(ser, "timeout", None) == 0:
                time.sleep(0.001)
            continue
        text = raw.decode("utf-8", errors="replace").strip("\r\n")
        if not text:
            continue
        if is_status_line(text):
            return text
    raise TimeoutError("no status report (<...>) received")


def dump_settings(ser: serial.Serial, *, timeout_s: float = 5.0) -> list[str]:
    send_line(ser, "$$")
    ser.flush()
    return read_until_ok(ser, timeout_s=timeout_s)


def dump_build_info(ser: serial.Serial, *, timeout_s: float = 3.0) -> list[str]:
    send_line(ser, "$I")
    ser.flush()
    return read_until_ok(ser, timeout_s=timeout_s)
