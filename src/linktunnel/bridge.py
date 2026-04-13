from __future__ import annotations

import select
import sys
import threading
import time
from typing import TextIO

import serial

from linktunnel.logfmt import log_line


def bridge_serial_blocking(
    a: serial.Serial,
    b: serial.Serial,
    *,
    log_stream: TextIO | None,
    hex_log: bool,
    stop_event: threading.Event,
) -> None:
    """Bidirectional copy using select (Unix). Falls back to threads on Windows."""

    if sys.platform == "win32":
        _bridge_threads(a, b, log_stream=log_stream, hex_log=hex_log, stop_event=stop_event)
        return

    fds = [a.fileno(), b.fileno()]
    while not stop_event.is_set():
        r, _, _ = select.select(fds, [], [], 0.25)
        if not r:
            continue
        for fd in r:
            src = a if fd == a.fileno() else b
            dst = b if fd == a.fileno() else a
            try:
                chunk = src.read(4096)
            except OSError:
                stop_event.set()
                break
            if not chunk:
                stop_event.set()
                break
            direction = "A->B" if src is a else "B->A"
            if log_stream is not None:
                log_line(log_stream, direction, chunk, hex_mode=hex_log)
            try:
                dst.write(chunk)
            except OSError:
                stop_event.set()
                break


def _bridge_threads(
    a: serial.Serial,
    b: serial.Serial,
    *,
    log_stream: TextIO | None,
    hex_log: bool,
    stop_event: threading.Event,
) -> None:
    # Non-blocking read(…) with timeout=0 returns immediately and would busy-spin.
    for p in (a, b):
        if getattr(p, "timeout", None) == 0:
            p.timeout = 0.05

    def pipe(src: serial.Serial, dst: serial.Serial, label: str) -> None:
        while not stop_event.is_set():
            try:
                n = max(1, src.in_waiting or 1)
                chunk = src.read(n)
            except OSError:
                stop_event.set()
                return
            if not chunk:
                time.sleep(0.002)
                continue
            if log_stream is not None:
                log_line(log_stream, label, chunk, hex_mode=hex_log)
            try:
                dst.write(chunk)
            except OSError:
                stop_event.set()
                return

    t1 = threading.Thread(target=pipe, args=(a, b, "A->B"), daemon=True)
    t2 = threading.Thread(target=pipe, args=(b, a, "B->A"), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
