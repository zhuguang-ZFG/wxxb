from __future__ import annotations

import pytest

from linktunnel.grbl.client import open_grbl_serial


def test_open_grbl_serial_rejects_both() -> None:
    with pytest.raises(ValueError, match="only one"):
        open_grbl_serial(port="/dev/ttyFAKE", url="socket://127.0.0.1:1", baud=115200, timeout=1.0)


def test_open_grbl_serial_requires_target() -> None:
    with pytest.raises(ValueError, match="port or url"):
        open_grbl_serial(port=None, url=None, baud=115200, timeout=1.0)
