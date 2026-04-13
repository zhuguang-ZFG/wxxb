from __future__ import annotations

from click.testing import CliRunner

from linktunnel.cli import main


def test_clash_help_lists_defaults() -> None:
    r = CliRunner().invoke(main, ["clash", "--help"])
    assert r.exit_code == 0
    assert "9090" in r.output
    assert "CLASH_API" in r.output
