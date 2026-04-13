from __future__ import annotations

import builtins
import sys

import pytest
from click.testing import CliRunner

from linktunnel.cli import main


def test_gui_help() -> None:
    r = CliRunner().invoke(main, ["gui", "--help"])
    assert r.exit_code == 0
    assert "gui" in r.output.lower() or "独立" in r.output
    assert "CLASH_API" in r.output


def test_gui_without_webview_shows_install_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "webview", raising=False)
    real_import = builtins.__import__

    def fake_import(
        name: str,
        globals: dict | None = None,
        locals: dict | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ):
        if name == "webview":
            raise ImportError("no webview")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    r = CliRunner().invoke(main, ["gui", "--api", "http://127.0.0.1:9090"])
    assert r.exit_code != 0
    assert "linktunnel[desktop]" in r.output
