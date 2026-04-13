from __future__ import annotations

from click.testing import CliRunner

from linktunnel.cli import main


def test_serial_term_help() -> None:
    r = CliRunner().invoke(main, ["serial", "term", "--help"])
    assert r.exit_code == 0
    assert "RYCOM" in r.output or "hex" in r.output.lower()


def test_serial_term_period_requires_message() -> None:
    r = CliRunner().invoke(main, ["serial", "term", "-p", "COM1", "--period", "1"])
    assert r.exit_code != 0


def test_serial_term_raw_rx_conflict() -> None:
    r = CliRunner().invoke(main, ["serial", "term", "-p", "COM1", "--raw-rx", "--hex"])
    assert r.exit_code != 0


def test_serial_term_raw_rx_encoding_conflict() -> None:
    r = CliRunner().invoke(main, ["serial", "term", "-p", "COM1", "--raw-rx", "--encoding", "gbk"])
    assert r.exit_code != 0
