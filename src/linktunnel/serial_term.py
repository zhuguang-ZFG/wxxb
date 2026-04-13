from __future__ import annotations

import contextlib
import re
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, TextIO

from linktunnel.serial_util import open_serial

# 文本模式收发（与常见串口助手一致：UTF-8 / 纯 ASCII / 中文 Windows GBK）
SUPPORTED_TEXT_ENCODINGS = frozenset({"utf-8", "ascii", "gbk"})


def codec_decode(encoding: str, data: bytes) -> str:
    """将接收到的行字节解码为 str（非法字节用替换符，避免抛错中断）。"""
    if encoding not in SUPPORTED_TEXT_ENCODINGS:
        raise ValueError(f"unsupported encoding: {encoding}")
    return data.decode(encoding, errors="replace")


def codec_encode(encoding: str, text: str) -> bytes:
    """将文本行编码为字节（用于非 hex-send 的发送）。"""
    if encoding not in SUPPORTED_TEXT_ENCODINGS:
        raise ValueError(f"unsupported encoding: {encoding}")
    return text.encode(encoding, errors="replace")


def eol_bytes(name: str) -> bytes:
    return {
        "lf": b"\n",
        "cr": b"\r",
        "crlf": b"\r\n",
        "none": b"",
    }[name]


def pop_serial_text_line(buf: bytearray) -> bytes | None:
    """
    从缓冲区取出一行原始字节（不含行尾）。支持 ``\\n``、``\\r``、``\\r\\n``；
    单独的 ``\\r`` 也视为行尾（常见嵌入式固件）。
    """
    if not buf:
        return None
    for i in range(len(buf)):
        if buf[i] == 0x0A:
            raw = bytes(buf[:i])
            del buf[: i + 1]
            return raw.rstrip(b"\r")
        if buf[i] == 0x0D:
            if i + 1 < len(buf) and buf[i + 1] == 0x0A:
                raw = bytes(buf[:i])
                del buf[: i + 2]
                return raw
            raw = bytes(buf[:i])
            del buf[: i + 1]
            return raw
    return None


def parse_hex_input_line(line: str) -> bytes:
    """
    Parse one line of user hex input: ``aa bb cc`` / ``AA:BB`` / ``aabbcc`` (偶数字节).
    """
    s = line.strip()
    if not s:
        return b""
    if re.search(r"[\s,:]", s):
        parts = [p for p in re.split(r"[\s,:]+", s) if p]
        if not parts:
            return b""
        return bytes(int(x, 16) for x in parts)
    if len(s) % 2 == 0:
        return bytes.fromhex(s)
    raise ValueError(f"invalid hex line: {line!r}")


def _ts_prefix(with_ms: bool) -> str:
    if with_ms:
        now = datetime.now()
        return now.strftime("%H:%M:%S.") + f"{now.microsecond // 1000:03d} "
    return datetime.now().strftime("%H:%M:%S ")


def validate_term_options(
    *,
    hex_display: bool,
    timestamp: bool,
    timestamp_ms: bool,
    raw_rx: bool,
    encoding: str,
) -> None:
    if raw_rx and hex_display:
        raise ValueError("--raw-rx 与 --hex 不能同时使用")
    if raw_rx and (timestamp or timestamp_ms):
        raise ValueError("--raw-rx 与 --timestamp/--timestamp-ms 不能同时使用")
    if raw_rx and encoding != "utf-8":
        raise ValueError("--raw-rx 与 --encoding 不能同时使用（原始接收不解码）")


def run_serial_term(
    port: str,
    baud: int,
    *,
    bytesize: int,
    parity: str,
    stopbits: int,
    rtscts: bool,
    xonxoff: bool,
    hex_display: bool,
    hex_send: bool,
    timestamp: bool,
    timestamp_ms: bool,
    eol_name: str,
    save_path: str | None,
    period_s: float | None,
    message: str | None,
    send_file: str | None,
    no_stdin: bool,
    quiet: bool,
    raw_rx: bool,
    encoding: str,
) -> int:
    """
    RYCOM 风格的单串口终端：stdin → 串口，串口 → stdout；可选周期发送、保存、十六进制与统计。
    """
    if encoding not in SUPPORTED_TEXT_ENCODINGS:
        raise ValueError(f"unsupported encoding: {encoding}")
    eol = eol_bytes(eol_name)
    stop = threading.Event()
    rx_total = [0]
    tx_total = [0]
    lock = threading.Lock()

    save_f: BinaryIO | None = None
    if save_path:
        save_f = open(save_path, "ab")

    ser = open_serial(
        port,
        baud,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        rtscts=rtscts,
        xonxoff=xonxoff,
    )

    out: TextIO = sys.stdout

    def handle_sig(_sig: int, _frame: object) -> None:
        stop.set()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    def reader() -> None:
        buf = bytearray()
        try:
            while not stop.is_set():
                try:
                    n = ser.in_waiting
                    chunk = ser.read(n if n else 4096)
                except OSError:
                    break
                if not chunk:
                    time.sleep(0.02)
                    continue
                with lock:
                    rx_total[0] += len(chunk)
                if save_f:
                    save_f.write(chunk)
                    save_f.flush()
                if raw_rx:
                    # 原始模式：字节直出 stdout，不做文本解码/分行
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                    continue
                if hex_display:
                    line = chunk.hex(" ")
                    prefix = _ts_prefix(timestamp_ms) if timestamp else ""
                    out.write(prefix + line + "\n")
                    out.flush()
                    continue
                buf.extend(chunk)
                while True:
                    pl = pop_serial_text_line(buf)
                    if pl is None:
                        break
                    text = codec_decode(encoding, pl)
                    prefix = _ts_prefix(timestamp_ms) if timestamp else ""
                    out.write(prefix + text + "\n")
                    out.flush()
                while len(buf) > 65536:
                    pl = pop_serial_text_line(buf)
                    if pl is None:
                        text = codec_decode(encoding, bytes(buf))
                        buf.clear()
                        prefix = _ts_prefix(timestamp_ms) if timestamp else ""
                        out.write(prefix + text + "\n")
                        out.flush()
                        break
                    text = codec_decode(encoding, pl)
                    prefix = _ts_prefix(timestamp_ms) if timestamp else ""
                    out.write(prefix + text + "\n")
                    out.flush()
        finally:
            if not hex_display and not raw_rx and buf:
                text = codec_decode(encoding, bytes(buf))
                prefix = _ts_prefix(timestamp_ms) if timestamp else ""
                out.write(prefix + text + "\n")
                out.flush()
            if save_f:
                with contextlib.suppress(Exception):
                    save_f.close()

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    def write_raw(data: bytes) -> None:
        if not data:
            return
        ser.write(data)
        ser.flush()
        with lock:
            tx_total[0] += len(data)

    def encode_tx_line(line: str) -> bytes:
        if hex_send:
            return parse_hex_input_line(line)
        s = line.rstrip("\r\n")
        return codec_encode(encoding, s) + eol

    try:
        if send_file:
            data = Path(send_file).read_bytes()
            write_raw(data)
            if no_stdin:
                while not stop.is_set():
                    time.sleep(0.2)
                return 0

        if period_s is not None:
            if message is None:
                raise ValueError("period requires --message")
            msg_b = encode_tx_line(message)

            def tick() -> None:
                while not stop.is_set():
                    write_raw(msg_b)
                    time.sleep(max(0.05, period_s))

            threading.Thread(target=tick, daemon=True).start()
            if no_stdin:
                while not stop.is_set():
                    time.sleep(0.2)
                return 0

        for line in sys.stdin:
            if stop.is_set():
                break
            try:
                write_raw(encode_tx_line(line))
            except ValueError as e:
                sys.stderr.write(f"[serial] send: {e}\n")
                sys.stderr.flush()
    except KeyboardInterrupt:
        stop.set()
    finally:
        stop.set()
        t.join(timeout=1.5)
        if not quiet:
            with lock:
                rx_n = rx_total[0]
                tx_n = tx_total[0]
            sys.stderr.write(f"\n[serial] RX {rx_n} bytes, TX {tx_n} bytes\n")
            sys.stderr.flush()
        with contextlib.suppress(Exception):
            ser.close()
    return 0
