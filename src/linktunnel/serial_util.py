from __future__ import annotations

from dataclasses import dataclass

import serial
import serial.tools.list_ports


@dataclass
class PortInfo:
    device: str
    name: str | None
    description: str | None
    hwid: str | None
    vid: int | None
    pid: int | None
    manufacturer: str | None
    is_bluetooth: bool

    def as_row(self) -> tuple[str, str, str]:
        kind = "BT" if self.is_bluetooth else "serial"
        desc = (self.description or "").replace("\n", " ")
        return self.device, kind, desc[:80]


def _looks_bluetooth(device: str, desc: str | None, hwid: str | None) -> bool:
    dev_lower = device.lower()
    if any(
        x in dev_lower
        for x in (
            "bluetooth",
            "blth",
            "rfcomm",
            "incoming-port",
        )
    ):
        return True
    blob = f"{desc or ''} {hwid or ''}".lower()
    return any(
        k in blob
        for k in (
            "bluetooth",
            "btserial",
            "rfcomm",
            "ble",
            "spp",
        )
    )


def list_serial_ports() -> list[PortInfo]:
    out: list[PortInfo] = []
    for p in serial.tools.list_ports.comports():
        vid = getattr(p, "vid", None)
        pid = getattr(p, "pid", None)
        desc = p.description or None
        hwid = p.hwid or None
        out.append(
            PortInfo(
                device=p.device,
                name=getattr(p, "name", None),
                description=desc,
                hwid=hwid,
                vid=vid if isinstance(vid, int) else None,
                pid=pid if isinstance(pid, int) else None,
                manufacturer=getattr(p, "manufacturer", None),
                is_bluetooth=_looks_bluetooth(p.device, desc, hwid),
            )
        )
    return out


def format_ports_table(ports: list[PortInfo]) -> str:
    if not ports:
        return "(no serial ports found)"
    lines = [f"{'DEVICE':<32} {'KIND':<8} DESCRIPTION"]
    lines.append("-" * 100)
    for p in ports:
        dev, kind, desc = p.as_row()
        lines.append(f"{dev:<32} {kind:<8} {desc}")
    return "\n".join(lines)


_BYTESIZE_MAP: dict[int, int] = {
    5: serial.FIVEBITS,
    6: serial.SIXBITS,
    7: serial.SEVENBITS,
    8: serial.EIGHTBITS,
}


def open_serial(
    device: str,
    baudrate: int,
    *,
    bytesize: int = 8,
    parity: str = "N",
    stopbits: int = 1,
    rtscts: bool = False,
    xonxoff: bool = False,
) -> serial.Serial:
    bs = _BYTESIZE_MAP.get(bytesize)
    if bs is None:
        raise ValueError(f"unsupported bytesize: {bytesize}")
    return serial.Serial(
        port=device,
        baudrate=baudrate,
        bytesize=bs,
        parity=parity,
        stopbits=stopbits,
        timeout=0,
        write_timeout=0,
        rtscts=rtscts,
        xonxoff=xonxoff,
    )
