from __future__ import annotations

import datetime as dt
import sys
from typing import BinaryIO, TextIO


def _ts() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log_line(stream: TextIO, direction: str, data: bytes, *, hex_mode: bool) -> None:
    if hex_mode:
        hx = data.hex()
        # wrap long hex
        chunk = 48
        parts = [hx[i : i + chunk] for i in range(0, len(hx), chunk)]
        body = " ".join(parts) if parts else ""
        stream.write(f"[{_ts()}] {direction} ({len(data)} B) {body}\n")
    else:
        text = data.decode("utf-8", errors="replace")
        text = text.replace("\r", "\\r").replace("\n", "\\n")
        stream.write(f"[{_ts()}] {direction} ({len(data)} B) {text}\n")
    stream.flush()


def open_log(path: str | None) -> TextIO | BinaryIO:
    if path:
        return open(path, "a", encoding="utf-8")
    return sys.stdout
