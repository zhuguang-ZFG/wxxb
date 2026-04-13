from __future__ import annotations

import re
from pathlib import Path


def test_version_matches_pyproject() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert m, "version not found in pyproject.toml"
    from linktunnel import __version__

    assert __version__ == m.group(1)
