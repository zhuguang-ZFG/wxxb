from __future__ import annotations

from linktunnel.grbl.stream_job import stream_gcode_file


class _OkSerial:
    timeout = 2.0

    def __init__(self, responses: list[bytes]) -> None:
        self._rx = list(responses)
        self.sent: list[bytes] = []

    def readline(self) -> bytes:
        return self._rx.pop(0) if self._rx else b""

    def write(self, data: bytes) -> int:
        self.sent.append(data)
        return len(data)

    def flush(self) -> None:
        pass

    @property
    def in_waiting(self) -> int:
        return 0


def test_stream_gcode_file_all_ok(tmp_path) -> None:
    f = tmp_path / "job.nc"
    f.write_text("G0 X1\n; c\nG1 Y2\n")
    ser = _OkSerial([b"ok\r\n", b"ok\r\n"])
    assert stream_gcode_file(ser, str(f), timeout_per_line=2.0) == 0
    assert len(ser.sent) == 2


def test_stream_gcode_file_error(tmp_path) -> None:
    f = tmp_path / "bad.nc"
    f.write_text("G99\n")
    errs: list[tuple[str, list[str]]] = []

    def on_err(line: str, rlines: list[str]) -> None:
        errs.append((line, list(rlines)))

    ser = _OkSerial([b"error:20\r\n"])
    assert stream_gcode_file(ser, str(f), timeout_per_line=2.0, on_error=on_err) == 1
    assert errs and errs[0][0] == "G99"
