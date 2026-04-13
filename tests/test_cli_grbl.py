from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from linktunnel.cli import main


def test_grbl_stream_dry_run_count_only(tmp_path: Path) -> None:
    nc = tmp_path / "a.nc"
    nc.write_text("G1\n\n;skip\nM5\n")
    r = CliRunner().invoke(
        main,
        ["grbl", "stream", str(nc), "--dry-run", "--dry-preview", "0"],
    )
    assert r.exit_code == 0
    assert "Parsed 2" in r.output


def test_grbl_stream_dry_run_preview(tmp_path: Path) -> None:
    nc = tmp_path / "b.nc"
    nc.write_text("\n".join(f"G1 X{i}" for i in range(4)))
    r = CliRunner().invoke(main, ["grbl", "stream", str(nc), "--dry-run", "--dry-preview", "2"])
    assert r.exit_code == 0
    assert "G1 X0" in r.output
    assert "more line(s) not shown" in r.output


def test_grbl_stream_requires_serial_target(tmp_path: Path) -> None:
    nc = tmp_path / "c.nc"
    nc.write_text("G0\n")
    r = CliRunner().invoke(main, ["grbl", "stream", str(nc)])
    assert r.exit_code != 0
    assert "exactly one" in r.output.lower()
