from __future__ import annotations

import sys
from typing import TextIO


def i2c_scan(bus: int, out: TextIO) -> int:
    if sys.platform != "linux":
        out.write("I2C scan is only supported on Linux (/dev/i2c-*).\n")
        return 1
    try:
        from smbus2 import SMBus
    except ImportError:
        out.write("I2C needs smbus2. Install with:\n  pip install 'linktunnel[i2c]'\n")
        return 1

    found: list[int] = []
    with SMBus(bus) as bus_obj:
        for addr in range(0x08, 0x78):
            try:
                bus_obj.read_byte(addr)
                found.append(addr)
            except OSError:
                continue
    if not found:
        out.write(f"No devices on I2C bus {bus} (or permission denied).\n")
        return 0
    out.write(
        f"I2C bus {bus} — addresses (7-bit): " + ", ".join(f"0x{a:02x}" for a in found) + "\n"
    )
    return 0
