from __future__ import annotations

import sys
import threading
import time

import serial

from linktunnel.grbl.protocol import REALTIME_HOLD, REALTIME_RESUME, REALTIME_STATUS
from linktunnel.grbl.status import parse_status_report


def run_monitor(
    ser: serial.Serial,
    *,
    decode_status: bool,
    status_out,
    data_out,
) -> None:
    """Read serial -> data_out; read stdin lines -> serial. EOF on stdin exits."""
    stop = threading.Event()

    def reader() -> None:
        while not stop.is_set():
            try:
                raw = ser.readline()
            except OSError:
                break
            if not raw:
                time.sleep(0.02)
                continue
            text = raw.decode("utf-8", errors="replace").strip("\r\n")
            if not text:
                continue
            if decode_status:
                rep = parse_status_report(text)
                if rep is not None:
                    data_out(text + "\n")
                    status_out(rep.format_human() + "\n")
                    continue
            data_out(text + "\n")

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    try:
        for line in sys.stdin:
            ser.write(line.encode("utf-8"))
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        t.join(timeout=1.0)


def send_realtime(ser: serial.Serial, which: str) -> None:
    m = {
        "?": REALTIME_STATUS,
        "!": REALTIME_HOLD,
        "~": REALTIME_RESUME,
    }
    b = m.get(which)
    if b is None:
        raise ValueError(f"unknown realtime key: {which!r} (use ?, !, ~)")
    ser.write(b)
