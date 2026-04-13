from __future__ import annotations

from click.testing import CliRunner

from linktunnel.cli import main


def test_client_help() -> None:
    r = CliRunner().invoke(main, ["client", "--help"])
    assert r.exit_code == 0
    assert "tkinter" in r.output
    assert "CLASH_API" in r.output
