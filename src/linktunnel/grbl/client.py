from __future__ import annotations

import serial

from linktunnel.serial_util import open_serial


def open_grbl_serial(
    *,
    port: str | None,
    url: str | None,
    baud: int,
    timeout: float,
) -> serial.Serial:
    """Open USB serial (--port) or PySerial URL such as ``socket://host:23`` (--url)."""
    if port and url:
        raise ValueError("use only one of port or url")
    if url:
        return serial.serial_for_url(url, baudrate=baud, timeout=timeout)
    if not port:
        raise ValueError("port or url is required")
    ser = open_serial(port, baud)
    ser.timeout = timeout
    return ser
