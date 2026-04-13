from __future__ import annotations

import sys
from pathlib import Path

import pytest

from linktunnel.proxy.mihomo_config import data_root, default_profile_dir
from linktunnel.proxy.runner import mihomo_doctor_package_lines, mihomo_release_hint


def test_data_root_unix_uses_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    dr = data_root()
    assert dr.name == ".linktunnel"
    assert dr.parent == Path.home()


def test_data_root_windows_uses_localappdata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\Test\AppData\Local")
    dr = data_root()
    assert "AppData" in str(dr)
    assert dr.name == "linktunnel"


def test_default_profile_is_under_data_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    assert default_profile_dir() == data_root() / "profiles" / "default"


def test_mihomo_release_hint_non_empty() -> None:
    h = mihomo_release_hint().lower()
    assert "mihomo" in h or "github" in h or "see" in h


def test_mihomo_doctor_package_lines() -> None:
    lines = mihomo_doctor_package_lines()
    assert any("platform" in x.lower() for x in lines)
    assert any("releases" in x.lower() for x in lines)
