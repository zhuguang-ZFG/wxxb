from __future__ import annotations

import asyncio
import sys
from typing import TextIO


def run_ble_scan(*, timeout_s: float, out: TextIO) -> int:
    try:
        from bleak import BleakScanner
    except ImportError:
        out.write(
            "BLE scan needs optional dependency. Install with:\n  pip install 'linktunnel[ble]'\n"
        )
        return 1

    async def _go() -> None:
        devices = await BleakScanner.discover(timeout=timeout_s)
        if not devices:
            out.write("(no BLE devices found)\n")
            return
        out.write(f"{'ADDRESS':<18} RSSI  NAME\n")
        out.write("-" * 60 + "\n")
        for d in devices:
            name = (d.name or "").replace("\n", " ")[:40]
            rssi = getattr(d, "rssi", "")
            out.write(f"{d.address:<18} {rssi!s:<5} {name}\n")

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(_go())
    return 0
