from __future__ import annotations

import contextlib
import json
import os
import shlex
import signal
import threading
import urllib.error
from pathlib import Path

import click

from linktunnel import __version__
from linktunnel.ble_scan import run_ble_scan
from linktunnel.bridge import bridge_serial_blocking
from linktunnel.clash.client import (
    ClashApiError,
    clash_get,
    clash_patch,
    clash_put,
    format_proxy_table,
    proxy_path_segment,
)
from linktunnel.dashboard_open import local_embedded_ui_url, open_in_browser, yacd_meta_browser_url
from linktunnel.grbl.client import open_grbl_serial
from linktunnel.grbl.monitor import run_monitor, send_realtime
from linktunnel.grbl.protocol import REALTIME_RESET
from linktunnel.grbl.report import dump_build_info, dump_settings, read_status_line
from linktunnel.grbl.status import parse_status_report
from linktunnel.grbl.stream_job import iter_gcode_lines, stream_gcode_file
from linktunnel.i2c_linux import i2c_scan
from linktunnel.logfmt import open_log
from linktunnel.netutil import parse_host_port
from linktunnel.proxy.mihomo_config import (
    build_config_with_proxy_list,
    build_config_with_subscription,
    default_profile_dir,
    external_controller_hints_from_config,
    load_proxies_from_clash_file,
)
from linktunnel.proxy.runner import (
    find_mihomo_binary,
    is_running,
    mihomo_doctor_package_lines,
    start_mihomo,
    stop_mihomo,
)
from linktunnel.serial_term import run_serial_term, validate_term_options
from linktunnel.serial_util import format_ports_table, list_serial_ports, open_serial
from linktunnel.tcp_udp import run_tcp_proxy, run_udp_relay


@click.group()
@click.version_option(__version__, prog_name="linktunnel")
def main() -> None:
    """Serial bridge/terminal, TCP relay, Mihomo proxy, dashboards, native client, Grbl, Clash API."""


@main.command("gui")
@click.option(
    "--from-profile",
    is_flag=True,
    help="从默认 profile 的 config.yaml 读取 external-controller 与 secret。",
)
@click.option(
    "--panel",
    type=click.Choice(["yacd", "local"]),
    default="yacd",
    show_default=True,
    help="yacd=在线 Yacd Meta；local=本机 http(s)://…/ui（需 proxy init --embed-ui 且 mihomo 已启动）。",
)
@click.option("--api", envvar="CLASH_API", default="http://127.0.0.1:9090", show_envvar=True)
@click.option("--secret", envvar="CLASH_SECRET", default="", show_envvar=True)
@click.option("--width", default=1100, type=int)
@click.option("--height", default=760, type=int)
@click.option("--title", default="linktunnel", show_default=True)
def gui_cmd(
    from_profile: bool,
    panel: str,
    api: str,
    secret: str,
    width: int,
    height: int,
    title: str,
) -> None:
    """独立桌面窗口（内嵌 WebView，需 pip install 'linktunnel[desktop]'）。\n\n    等价命令：linktunnel-gui"""
    from linktunnel.desktop_gui import run_desktop_app

    run_desktop_app(
        from_profile=from_profile,
        panel=panel,
        api=api,
        secret=secret,
        width=width,
        height=height,
        title=title,
    )


@main.command("client")
@click.option(
    "--from-profile",
    is_flag=True,
    help="启动时从默认 profile 的 config.yaml 读取 external-controller 与 secret，并自动刷新一次。",
)
@click.option("--api", envvar="CLASH_API", default="http://127.0.0.1:9090", show_envvar=True)
@click.option("--secret", envvar="CLASH_SECRET", default="", show_envvar=True)
def client_cmd(from_profile: bool, api: str, secret: str) -> None:
    """自带图形客户端（tkinter）：直连 Mihomo External Controller，切换模式与节点。\n\n    无需 WebView / Yacd；依赖系统 Python 的 tkinter。等价命令：linktunnel-client"""
    from linktunnel.client_app import run_client_app

    run_client_app(from_profile=from_profile, api=api, secret=secret)


@main.group("serial")
def serial_grp() -> None:
    """Serial: list, bridge, single-port terminal (RYCOM-style helpers)."""


@serial_grp.command("list")
@click.option("--bluetooth-only", is_flag=True, help="Only show ports that look like Bluetooth.")
def serial_list(bluetooth_only: bool) -> None:
    ports = list_serial_ports()
    if bluetooth_only:
        ports = [p for p in ports if p.is_bluetooth]
    click.echo(format_ports_table(ports))


@serial_grp.command("bridge")
@click.option(
    "--a", "port_a", required=True, type=str, help="First serial device (e.g. /dev/ttyUSB0)."
)
@click.option("--b", "port_b", required=True, type=str, help="Second serial device.")
@click.option("--baud", default=115200, show_default=True, type=int)
@click.option("--parity", default="N", type=click.Choice(["N", "E", "O", "M", "S"]))
@click.option("--stopbits", default=1, type=int)
@click.option("--rtscts", is_flag=True)
@click.option("--xonxoff", is_flag=True)
@click.option("--log", "log_path", type=click.Path(), help="Append log file (default: stdout).")
@click.option(
    "--quiet",
    is_flag=True,
    help="No payload logging to stdout; with --log, write payloads to file only.",
)
@click.option("--hex", "hex_log", is_flag=True, help="Log payloads as hex.")
@click.option(
    "--bytesize", default=8, show_default=True, type=click.IntRange(5, 8), help="Data bits (5-8)."
)
def serial_bridge(
    port_a: str,
    port_b: str,
    baud: int,
    parity: str,
    stopbits: int,
    rtscts: bool,
    xonxoff: bool,
    log_path: str | None,
    quiet: bool,
    hex_log: bool,
    bytesize: int,
) -> None:
    """Bridge two serial ports (true passthrough). Use two USB-UART cables or BT COM + UART."""
    if quiet and log_path:
        log_f = open_log(log_path)
        close_log = True
    elif quiet:
        log_f = None
        close_log = False
    else:
        log_f = open_log(log_path)
        close_log = log_path is not None
    stop = threading.Event()

    def handle_sig(_sig: int, _frame: object) -> None:
        stop.set()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    sa = sb = None
    try:
        try:
            sa = open_serial(
                port_a,
                baud,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                rtscts=rtscts,
                xonxoff=xonxoff,
            )
            sb = open_serial(
                port_b,
                baud,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                rtscts=rtscts,
                xonxoff=xonxoff,
            )
        except OSError as e:
            click.echo(f"Failed to open serial: {e}", err=True)
            raise SystemExit(1) from e

        bridge_serial_blocking(
            sa,
            sb,
            log_stream=log_f,
            hex_log=hex_log,
            stop_event=stop,
        )
    finally:
        if sa is not None:
            with contextlib.suppress(Exception):
                sa.close()
        if sb is not None:
            with contextlib.suppress(Exception):
                sb.close()
        if close_log:
            with contextlib.suppress(Exception):
                log_f.close()


@serial_grp.command("term")
@click.option("--port", "-p", required=True, type=str, help="串口设备（如 /dev/ttyUSB0、COM3）。")
@click.option("--baud", default=115200, show_default=True, type=int)
@click.option("--parity", default="N", type=click.Choice(["N", "E", "O", "M", "S"]))
@click.option("--stopbits", default=1, type=int)
@click.option("--rtscts", is_flag=True)
@click.option("--xonxoff", is_flag=True)
@click.option(
    "--bytesize", default=8, show_default=True, type=click.IntRange(5, 8), help="数据位 5–8。"
)
@click.option(
    "--hex",
    "hex_display",
    is_flag=True,
    help="接收以十六进制显示（与 RYCOM 等调试助手类似）。",
)
@click.option(
    "--raw-rx",
    is_flag=True,
    help="接收原始字节直出 stdout（不做 UTF-8 解码/分行，且不能与 --hex/--timestamp 同用）。",
)
@click.option(
    "--hex-send",
    is_flag=True,
    help="发送行解析为十六进制（如 aa bb cc 或 aabbcc），不自动追加换行。",
)
@click.option("--timestamp", "-t", is_flag=True, help="接收行前加时间戳。")
@click.option(
    "--timestamp-ms",
    is_flag=True,
    help="时间戳含毫秒（与 --timestamp 同用）。",
)
@click.option(
    "--eol",
    "eol_name",
    type=click.Choice(["lf", "cr", "crlf", "none"]),
    default="lf",
    show_default=True,
    help="文本发送时每行末尾追加的换行（--hex-send 时无效）。",
)
@click.option(
    "--encoding",
    type=click.Choice(["utf-8", "ascii", "gbk"]),
    default="utf-8",
    show_default=True,
    help="文本模式下接收分行后的解码与发送编码（UTF-8 / ASCII / GBK）；--hex / --raw-rx / --hex-send 时不使用。",
)
@click.option(
    "--save",
    "save_path",
    type=click.Path(),
    help="将接收到的原始字节追加写入文件。",
)
@click.option(
    "--period",
    "period_s",
    type=float,
    default=None,
    help="周期发送间隔（秒）；需同时指定 --message。",
)
@click.option(
    "--message",
    "-m",
    type=str,
    default=None,
    help="单次或周期发送的内容（文本或配合 --hex-send）。",
)
@click.option(
    "--send-file",
    "send_file",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="启动后先发送该文件（二进制），再读标准输入（可用 --no-stdin 仅发送）。",
)
@click.option(
    "--no-stdin",
    is_flag=True,
    help="不读标准输入：仅 --send-file、或 --period + --message 时保持运行直到 Ctrl+C。",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="退出时不向 stderr 打印 RX/TX 字节统计。",
)
def serial_term_cmd(
    port: str,
    baud: int,
    parity: str,
    stopbits: int,
    rtscts: bool,
    xonxoff: bool,
    bytesize: int,
    hex_display: bool,
    raw_rx: bool,
    hex_send: bool,
    timestamp: bool,
    timestamp_ms: bool,
    eol_name: str,
    encoding: str,
    save_path: str | None,
    period_s: float | None,
    message: str | None,
    send_file: str | None,
    no_stdin: bool,
    quiet: bool,
) -> None:
    """单串口终端（参考 RYCOM：收发、HEX、时间戳、周期发送、保存、流量统计）。"""
    if period_s is not None and period_s <= 0:
        raise click.BadParameter("period must be positive")
    if period_s is not None and message is None:
        raise click.BadParameter("--period requires --message")
    try:
        validate_term_options(
            hex_display=hex_display,
            timestamp=timestamp,
            timestamp_ms=timestamp_ms,
            raw_rx=raw_rx,
            encoding=encoding,
        )
    except ValueError as e:
        raise click.BadParameter(str(e)) from e
    return run_serial_term(
        port,
        baud,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        rtscts=rtscts,
        xonxoff=xonxoff,
        hex_display=hex_display,
        hex_send=hex_send,
        timestamp=timestamp or timestamp_ms,
        timestamp_ms=timestamp_ms,
        eol_name=eol_name,
        save_path=save_path,
        period_s=period_s,
        message=message,
        send_file=send_file,
        no_stdin=no_stdin,
        quiet=quiet,
        raw_rx=raw_rx,
        encoding=encoding,
    )


@main.group("net")
def net_grp() -> None:
    """TCP/UDP proxy (monitor traffic in the middle)."""


@net_grp.command("tcp")
@click.option("--listen", "listen_s", required=True, help="Listen address host:port.")
@click.option("--target", "target_s", required=True, help="Upstream host:port.")
@click.option("--log", "log_path", type=click.Path(), help="Append log file (default: stdout).")
@click.option("--hex", "hex_log", is_flag=True)
def net_tcp(listen_s: str, target_s: str, log_path: str | None, hex_log: bool) -> None:
    lh, lp = _parse_host_port_click(listen_s)
    th, tp = _parse_host_port_click(target_s)
    log_f = open_log(log_path)
    try:
        run_tcp_proxy(lh, lp, th, tp, log_stream=log_f, hex_log=hex_log)
    except OSError as e:
        click.echo(f"TCP proxy error: {e}", err=True)
        raise SystemExit(1) from e
    finally:
        if log_path:
            with contextlib.suppress(Exception):
                log_f.close()


@net_grp.command("udp")
@click.option("--listen", "listen_s", required=True, help="Listen address host:port.")
@click.option("--target", "target_s", required=True, help="Upstream host:port.")
@click.option("--log", "log_path", type=click.Path(), help="Append log file (default: stdout).")
@click.option("--hex", "hex_log", is_flag=True)
def net_udp(listen_s: str, target_s: str, log_path: str | None, hex_log: bool) -> None:
    lh, lp = _parse_host_port_click(listen_s)
    th, tp = _parse_host_port_click(target_s)
    log_f = open_log(log_path)
    try:
        run_udp_relay(lh, lp, th, tp, log_stream=log_f, hex_log=hex_log)
    except OSError as e:
        click.echo(f"UDP relay error: {e}", err=True)
        raise SystemExit(1) from e
    finally:
        if log_path:
            with contextlib.suppress(Exception):
                log_f.close()


def _parse_host_port_click(s: str) -> tuple[str, int]:
    try:
        return parse_host_port(s)
    except ValueError as e:
        raise click.BadParameter(str(e)) from e


@main.group("ble")
def ble_grp() -> None:
    """Bluetooth Low Energy discovery (not RFCOMM sniffer)."""


@ble_grp.command("scan")
@click.option("--timeout", default=5.0, show_default=True, type=float)
def ble_scan_cmd(timeout: float) -> None:
    raise SystemExit(run_ble_scan(timeout_s=timeout, out=click.get_text_stream("stdout")))


@main.group("grbl")
def grbl_grp() -> None:
    """Grbl / Grbl_Esp32: G-code stream, monitor, settings (USB serial or socket://)."""


def _grbl_port_url_opts(f):
    f = click.option(
        "--port",
        "-p",
        type=str,
        default=None,
        help="Serial device (e.g. /dev/ttyUSB0, COM3).",
    )(f)
    f = click.option(
        "--url",
        "-u",
        type=str,
        default=None,
        help="PySerial URL, e.g. socket://192.168.4.1:23 for WiFi telnet.",
    )(f)
    f = click.option("--baud", default=115200, show_default=True, type=int)(f)
    return f


def _require_grbl_target(port: str | None, url: str | None) -> None:
    if (port is None) == (url is None):
        raise click.UsageError("Specify exactly one of --port or --url.")


@grbl_grp.command("monitor")
@_grbl_port_url_opts
@click.option("--decode-status/--raw", default=True, help="Decode <...> status lines.")
@click.option(
    "--realtime",
    type=click.Choice(["?", "!", "~"]),
    default=None,
    help="Send one realtime byte once at startup (then use stdin for lines).",
)
def grbl_monitor(
    port: str | None,
    url: str | None,
    baud: int,
    decode_status: bool,
    realtime: str | None,
) -> None:
    """Interactive RX to stdout, stdin to controller (line-based). Ctrl+C to exit."""
    _require_grbl_target(port, url)
    try:
        ser = open_grbl_serial(port=port, url=url, baud=baud, timeout=0.1)
    except OSError as e:
        click.echo(f"open failed: {e}", err=True)
        raise SystemExit(1) from e
    out = click.get_text_stream("stdout")
    err = click.get_text_stream("stderr")
    try:
        if realtime is not None:
            send_realtime(ser, realtime)
        run_monitor(ser, decode_status=decode_status, status_out=err.write, data_out=out.write)
    finally:
        ser.close()


@grbl_grp.command("stream")
@click.argument("gcode_file", type=click.Path(exists=True, dir_okay=False))
@_grbl_port_url_opts
@click.option("--timeout", "timeout_s", default=30.0, show_default=True, type=float)
@click.option("-v", "--verbose", is_flag=True, help="Print each TX/RX line.")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Parse and count G-code lines only (no serial; ignores --port/--url).",
)
@click.option(
    "--dry-preview",
    default=25,
    show_default=True,
    type=click.IntRange(0, 5000),
    help="With --dry-run, how many lines to print (0 = count only).",
)
def grbl_stream(
    gcode_file: str,
    port: str | None,
    url: str | None,
    baud: int,
    timeout_s: float,
    verbose: bool,
    dry_run: bool,
    dry_preview: int,
) -> None:
    """Stream a G-code file; wait for ok/error per line (Grbl serial protocol)."""
    if dry_run:
        lines = list(iter_gcode_lines(gcode_file))
        click.echo(f"Parsed {len(lines)} command line(s) after comment strip.")
        if dry_preview > 0:
            for i, line in enumerate(lines[:dry_preview], 1):
                click.echo(f"  {i:4d}  {line}")
            if len(lines) > dry_preview:
                click.echo(f"  ... {len(lines) - dry_preview} more line(s) not shown")
        return

    _require_grbl_target(port, url)
    try:
        ser = open_grbl_serial(port=port, url=url, baud=baud, timeout=timeout_s)
    except OSError as e:
        click.echo(f"open failed: {e}", err=True)
        raise SystemExit(1) from e
    out = click.get_text_stream("stdout")

    def on_send(line: str) -> None:
        if verbose:
            click.echo(f">> {line}", file=out)

    def on_rx(line: str) -> None:
        if verbose:
            click.echo(f"<< {line}", file=out)

    def on_error(line: str, rlines: list[str]) -> None:
        click.echo(f"error on: {line}", err=True)
        for ln in rlines:
            click.echo(f"  {ln}", err=True)

    try:
        code = stream_gcode_file(
            ser,
            gcode_file,
            timeout_per_line=timeout_s,
            on_send=on_send if verbose else None,
            on_rx=on_rx if verbose else None,
            on_error=on_error,
        )
    except TimeoutError as e:
        click.echo(str(e), err=True)
        raise SystemExit(2) from e
    finally:
        ser.close()
    raise SystemExit(code)


@grbl_grp.command("settings")
@_grbl_port_url_opts
@click.option("--timeout", default=8.0, show_default=True, type=float)
def grbl_settings(port: str | None, url: str | None, baud: int, timeout: float) -> None:
    """Send $$ and print firmware response until ok."""
    _require_grbl_target(port, url)
    try:
        ser = open_grbl_serial(port=port, url=url, baud=baud, timeout=timeout)
    except OSError as e:
        click.echo(f"open failed: {e}", err=True)
        raise SystemExit(1) from e
    try:
        for ln in dump_settings(ser, timeout_s=timeout):
            click.echo(ln)
    except TimeoutError as e:
        click.echo(str(e), err=True)
        raise SystemExit(2) from e
    finally:
        ser.close()


@grbl_grp.command("build-info")
@_grbl_port_url_opts
@click.option("--timeout", default=5.0, show_default=True, type=float)
def grbl_build_info(port: str | None, url: str | None, baud: int, timeout: float) -> None:
    """Send $I (build / version info)."""
    _require_grbl_target(port, url)
    try:
        ser = open_grbl_serial(port=port, url=url, baud=baud, timeout=timeout)
    except OSError as e:
        click.echo(f"open failed: {e}", err=True)
        raise SystemExit(1) from e
    try:
        for ln in dump_build_info(ser, timeout_s=timeout):
            click.echo(ln)
    except TimeoutError as e:
        click.echo(str(e), err=True)
        raise SystemExit(2) from e
    finally:
        ser.close()


@grbl_grp.command("status")
@_grbl_port_url_opts
@click.option("--timeout", default=2.0, show_default=True, type=float)
@click.option("--decode/--raw", default=True)
def grbl_status(
    port: str | None,
    url: str | None,
    baud: int,
    timeout: float,
    decode: bool,
) -> None:
    """Send realtime ? once and print status report."""
    _require_grbl_target(port, url)
    try:
        ser = open_grbl_serial(port=port, url=url, baud=baud, timeout=timeout)
    except OSError as e:
        click.echo(f"open failed: {e}", err=True)
        raise SystemExit(1) from e
    try:
        line = read_status_line(ser, timeout_s=timeout)
        click.echo(line)
        if decode:
            rep = parse_status_report(line)
            if rep is not None:
                click.echo(rep.format_human())
    except TimeoutError as e:
        click.echo(str(e), err=True)
        raise SystemExit(2) from e
    finally:
        ser.close()


@grbl_grp.command("reset")
@_grbl_port_url_opts
def grbl_reset(port: str | None, url: str | None, baud: int) -> None:
    """Send soft reset (Ctrl+X / 0x18)."""
    _require_grbl_target(port, url)
    try:
        ser = open_grbl_serial(port=port, url=url, baud=baud, timeout=0.5)
    except OSError as e:
        click.echo(f"open failed: {e}", err=True)
        raise SystemExit(1) from e
    try:
        ser.write(REALTIME_RESET)
        ser.flush()
        click.echo("sent soft reset (0x18)")
    finally:
        ser.close()


@grbl_grp.command("report")
@_grbl_port_url_opts
@click.option("--timeout", default=8.0, show_default=True, type=float)
def grbl_report(port: str | None, url: str | None, baud: int, timeout: float) -> None:
    """Run status, $$, and $I in one go (handy after connect)."""
    _require_grbl_target(port, url)
    try:
        ser = open_grbl_serial(port=port, url=url, baud=baud, timeout=timeout)
    except OSError as e:
        click.echo(f"open failed: {e}", err=True)
        raise SystemExit(1) from e
    try:
        click.echo("--- status (? ) ---")
        line = read_status_line(ser, timeout_s=min(3.0, timeout))
        click.echo(line)
        rep = parse_status_report(line)
        if rep is not None:
            click.echo(rep.format_human())
        click.echo("--- settings ($$) ---")
        for ln in dump_settings(ser, timeout_s=timeout):
            click.echo(ln)
        click.echo("--- build ($I) ---")
        for ln in dump_build_info(ser, timeout_s=min(5.0, timeout)):
            click.echo(ln)
    except TimeoutError as e:
        click.echo(str(e), err=True)
        raise SystemExit(2) from e
    finally:
        ser.close()


@main.group("clash", invoke_without_command=True)
@click.option(
    "--api",
    envvar="CLASH_API",
    default="http://127.0.0.1:9090",
    show_default=True,
    show_envvar=True,
    help="External Controller base URL (Clash Verge Rev → 设置 → 核心 → 外部控制).",
)
@click.option(
    "--secret",
    envvar="CLASH_SECRET",
    default="",
    show_envvar=True,
    help="API secret (Bearer); empty if not set in Verge.",
)
@click.pass_context
def clash_grp(ctx: click.Context, api: str, secret: str) -> None:
    """
    Mihomo / Clash Meta External Controller (Clash Verge Rev 等 GUI 开启「外部控制」后可用).

    在 Clash Verge Rev 中查看端口与密钥：设置 → 核心 / 开发者相关页面（与内核 YAML 中
    ``external-controller``、``secret`` 一致）。
    """
    ctx.ensure_object(dict)
    ctx.obj["api"] = api.rstrip("/")
    ctx.obj["secret"] = secret.strip() or None
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _clash_handle_exc(e: Exception) -> None:
    if isinstance(e, ClashApiError):
        click.echo(str(e), err=True)
        raise SystemExit(1) from e
    if isinstance(e, urllib.error.URLError):
        click.echo(f"connection failed: {e.reason}", err=True)
        raise SystemExit(1) from e
    raise


@clash_grp.command("version")
@click.pass_context
def clash_version_cmd(ctx: click.Context) -> None:
    """GET /version — core name and version."""
    try:
        data = clash_get(ctx.obj["api"], "/version", secret=ctx.obj["secret"])
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        _clash_handle_exc(e)


@clash_grp.command("configs")
@click.option("--raw", is_flag=True, help="Print full JSON (can be large).")
@click.pass_context
def clash_configs_cmd(ctx: click.Context, raw: bool) -> None:
    """GET /configs — mode, ports, etc."""
    try:
        data = clash_get(ctx.obj["api"], "/configs", secret=ctx.obj["secret"])
        if raw or not isinstance(data, dict):
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
            return
        subset = {
            k: data.get(k)
            for k in (
                "mode",
                "mixed-port",
                "port",
                "socks-port",
                "redir-port",
                "tproxy-port",
                "allow-lan",
                "bind-address",
                "log-level",
            )
            if k in data
        }
        click.echo(json.dumps(subset, indent=2, ensure_ascii=False))
    except Exception as e:
        _clash_handle_exc(e)


@clash_grp.command("mode")
@click.argument("value", required=False, type=str)
@click.pass_context
def clash_mode_cmd(ctx: click.Context, value: str | None) -> None:
    """Get or set running mode (rule / global / direct)."""
    try:
        if value is None:
            data = clash_get(ctx.obj["api"], "/configs", secret=ctx.obj["secret"])
            if isinstance(data, dict) and "mode" in data:
                click.echo(str(data["mode"]))
            else:
                click.echo(json.dumps(data, indent=2, ensure_ascii=False))
            return
        v = value.strip().lower()
        if v not in ("rule", "global", "direct"):
            raise click.BadParameter("must be rule, global, or direct")
        clash_patch(ctx.obj["api"], "/configs", {"mode": v}, secret=ctx.obj["secret"])
        click.echo(f"mode -> {v}")
    except click.BadParameter:
        raise
    except Exception as e:
        _clash_handle_exc(e)


@clash_grp.command("proxies")
@click.pass_context
def clash_proxies_cmd(ctx: click.Context) -> None:
    """List Selector / URLTest / Fallback groups and current node."""
    try:
        data = clash_get(ctx.obj["api"], "/proxies", secret=ctx.obj["secret"])
        if not isinstance(data, dict):
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
            return
        click.echo(format_proxy_table(data))
    except Exception as e:
        _clash_handle_exc(e)


@clash_grp.command("select")
@click.argument("group")
@click.argument("outbound")
@click.pass_context
def clash_select_cmd(ctx: click.Context, group: str, outbound: str) -> None:
    """PUT /proxies/{group} — switch a policy group to an outbound (node) name."""
    try:
        path = f"/proxies/{proxy_path_segment(group)}"
        clash_put(ctx.obj["api"], path, {"name": outbound}, secret=ctx.obj["secret"])
        click.echo(f"{group} -> {outbound}")
    except Exception as e:
        _clash_handle_exc(e)


@clash_grp.command("connections")
@click.option("--json-out", "json_out", is_flag=True, help="Full JSON instead of summary.")
@click.pass_context
def clash_connections_cmd(ctx: click.Context, json_out: bool) -> None:
    """GET /connections — active connections summary."""
    try:
        data = clash_get(ctx.obj["api"], "/connections", secret=ctx.obj["secret"])
        if json_out or not isinstance(data, dict):
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
            return
        conns = data.get("connections")
        n = len(conns) if isinstance(conns, list) else 0
        click.echo(f"connections: {n}")
        click.echo(f"downloadTotal: {data.get('downloadTotal', '')}")
        click.echo(f"uploadTotal: {data.get('uploadTotal', '')}")
    except Exception as e:
        _clash_handle_exc(e)


@main.group("proxy", invoke_without_command=True)
@click.pass_context
def proxy_grp(ctx: click.Context) -> None:
    """
    本地代理：调用本机 **Mihomo (Clash Meta)** 二进制 + 生成的 YAML。

    需自行安装 mihomo 并放入 PATH，或设置环境变量 MIHOMO_BIN（Windows / macOS / Linux 通用）。

    默认配置目录：Windows 为 ``%LOCALAPPDATA%\\linktunnel``，Unix 为 ``~/.linktunnel``。
    订阅通过内核 ``proxy-providers`` 拉取节点；也可用 ``--import-yaml`` 导入 Clash ``proxies`` 片段。
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@proxy_grp.command("init")
@click.option(
    "--dir",
    "profile_dir",
    type=click.Path(),
    default=None,
    help="Profile dir (default: data root …/profiles/default; Windows %%LOCALAPPDATA%%/linktunnel/…).",
)
@click.option("--sub-url", type=str, default=None, help="HTTP(S) subscription URL (内核拉取).")
@click.option(
    "--import-yaml",
    "import_yaml",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Clash 格式文件，含 proxies: 列表（静态节点）.",
)
@click.option("--mixed-port", default=7890, show_default=True, type=int)
@click.option(
    "--external-controller",
    "ecc",
    default="127.0.0.1:9090",
    show_default=True,
    help="与 clash 子命令 / Web 面板一致.",
)
@click.option("--secret", default="", show_default=True, help="external-controller 密钥（可空）.")
@click.option("--provider-name", default="nodes", show_default=True)
@click.option(
    "--embed-ui/--no-embed-ui",
    default=False,
    help="在配置中启用 Mihomo 内置 Web 面板（MetaCubeXD zip，首次访问 /ui 时下载）.",
)
def proxy_init(
    profile_dir: str | None,
    sub_url: str | None,
    import_yaml: str | None,
    mixed_port: int,
    ecc: str,
    secret: str,
    provider_name: str,
    embed_ui: bool,
) -> None:
    """Write config.yaml（订阅 URL 或导入 proxies 文件二选一）."""
    if (sub_url is None) == (import_yaml is None):
        raise click.UsageError("Specify exactly one of --sub-url or --import-yaml.")
    root = Path(profile_dir) if profile_dir else default_profile_dir()
    root.mkdir(parents=True, exist_ok=True)
    (root / "providers").mkdir(parents=True, exist_ok=True)
    cfg_path = root / "config.yaml"
    if sub_url:
        if not sub_url.startswith(("http://", "https://")):
            raise click.BadParameter("sub-url should start with http:// or https://")
        text = build_config_with_subscription(
            sub_url,
            mixed_port=mixed_port,
            external_controller=ecc,
            secret=secret,
            provider_name=provider_name,
            embed_ui=embed_ui,
        )
    else:
        plist = load_proxies_from_clash_file(Path(import_yaml))
        text = build_config_with_proxy_list(
            plist,
            mixed_port=mixed_port,
            external_controller=ecc,
            secret=secret,
            embed_ui=embed_ui,
        )
    cfg_path.write_text(text, encoding="utf-8")
    click.echo(f"Wrote {cfg_path.resolve()}")
    if embed_ui:
        api, _ = external_controller_hints_from_config(cfg_path)
        click.echo(f"内置面板（mihomo 启动后）: {local_embedded_ui_url(api)}")
        click.echo("或浏览器: linktunnel dashboard open --panel local --from-profile")


@proxy_grp.command("run")
@click.option("--dir", "profile_dir", type=click.Path(), default=None)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Defaults to <profile>/config.yaml",
)
@click.option("--bin", type=str, default=None, envvar="MIHOMO_BIN", help="mihomo 可执行文件路径.")
def proxy_run(profile_dir: str | None, config: str | None, bin: str | None) -> None:
    """后台启动 mihomo（日志写入 profile/mihomo.log）。"""
    root = Path(profile_dir) if profile_dir else default_profile_dir()
    cfg = Path(config) if config else root / "config.yaml"
    if not cfg.is_file():
        click.echo(f"Missing {cfg}; run: linktunnel proxy init ...", err=True)
        raise SystemExit(1)
    try:
        pid = start_mihomo(root, cfg, binary=bin)
    except (FileNotFoundError, RuntimeError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1) from e
    click.echo(f"mihomo pid={pid}")
    click.echo(f"log: {(root / 'mihomo.log').resolve()}")
    click.echo("Browser: system proxy → HTTP/SOCKS on mixed-port (see config, default 7890).")
    api_base, sec = external_controller_hints_from_config(cfg)
    click.echo("CLI (match this profile’s external-controller / secret):")
    if os.name == "nt":
        click.echo(f"set CLASH_API={api_base}")
        if sec:
            click.echo(f"set CLASH_SECRET={sec}")
    else:
        click.echo(f"export CLASH_API={shlex.quote(api_base)}")
        if sec:
            click.echo(f"export CLASH_SECRET={shlex.quote(sec)}")
    click.echo(
        "Web UI: linktunnel dashboard open --from-profile  （或 --panel local 若已 --embed-ui）"
    )


@proxy_grp.command("stop")
@click.option("--dir", "profile_dir", type=click.Path(), default=None)
def proxy_stop(profile_dir: str | None) -> None:
    """停止由本工具记录的 mihomo 进程。"""
    root = Path(profile_dir) if profile_dir else default_profile_dir()
    if stop_mihomo(root):
        click.echo("stopped.")
    else:
        click.echo("no pid file (not running).")


@proxy_grp.command("status")
@click.option("--dir", "profile_dir", type=click.Path(), default=None)
def proxy_status(profile_dir: str | None) -> None:
    """查看本 profile 是否仍有 mihomo 进程。"""
    root = Path(profile_dir) if profile_dir else default_profile_dir()
    ok, pid = is_running(root)
    click.echo(f"running={ok} pid={pid}")


@proxy_grp.command("doctor")
def proxy_doctor() -> None:
    """先根据当前系统打印建议下载的 Mihomo 包，再检测 PATH / MIHOMO_BIN。"""
    for line in mihomo_doctor_package_lines():
        click.echo(line)
    click.echo("")
    click.echo("=== 二进制检测 ===")
    b = find_mihomo_binary(None)
    if b:
        click.echo(f"OK: {b}")
    else:
        click.echo("未找到 mihomo（PATH 中无常见名称，且未设置 MIHOMO_BIN）。", err=True)
        click.echo("  https://github.com/MetaCubeX/mihomo/releases", err=True)
        click.echo(
            "下载后解压，把可执行文件加入 PATH，或设置环境变量 MIHOMO_BIN=完整路径", err=True
        )
        raise SystemExit(1)


@main.group("dashboard", invoke_without_command=True)
@click.pass_context
def dashboard_grp(ctx: click.Context) -> None:
    """
    在浏览器中打开 Mihomo 控制台（在线 Yacd 或本机 /ui）。

    完整 GUI 客户端请使用 **Clash Verge Rev** 等；此处为「浏览器 + 面板」。
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@dashboard_grp.command("open")
@click.option(
    "--api",
    envvar="CLASH_API",
    default="http://127.0.0.1:9090",
    show_default=True,
    show_envvar=True,
)
@click.option("--secret", envvar="CLASH_SECRET", default="", show_envvar=True)
@click.option(
    "--from-profile",
    is_flag=True,
    help="从默认 profile 的 config.yaml 读取 external-controller 与 secret。",
)
@click.option(
    "--panel",
    type=click.Choice(["yacd", "local"]),
    default="yacd",
    show_default=True,
    help="yacd=在线 Yacd Meta；local=本机 http(s)://…/ui（需 proxy init --embed-ui 且 mihomo 已启动）.",
)
@click.option("--print-url", is_flag=True, help="只打印 URL，不打开浏览器。")
def dashboard_open_cmd(
    api: str,
    secret: str,
    from_profile: bool,
    panel: str,
    print_url: bool,
) -> None:
    """用系统默认浏览器打开面板。"""
    if from_profile:
        cfg = default_profile_dir() / "config.yaml"
        if not cfg.is_file():
            click.echo(f"Missing {cfg}; run: linktunnel proxy init ...", err=True)
            raise SystemExit(1)
        api, secret = external_controller_hints_from_config(cfg)
    if panel == "local":
        url = local_embedded_ui_url(api)
        click.echo(f"Local UI: {url}")
    else:
        url = yacd_meta_browser_url(api, secret)
        click.echo(f"Online Yacd (Meta): {url}")
    if print_url:
        return
    open_in_browser(url)
    click.echo("Opened in default browser.")


@dashboard_grp.command("info")
def dashboard_info_cmd() -> None:
    """说明：浏览器面板 vs Clash Verge Rev 客户端。"""
    lines = [
        "=== 浏览器里用面板 ===",
        "1) 在线 Yacd（默认）: linktunnel dashboard open",
        "2) 本机 Mihomo 内置页: 先 proxy init --embed-ui，再 proxy run，然后:",
        "   linktunnel dashboard open --panel local --from-profile",
        "",
        "=== 完整 GUI 客户端（另装）===",
        "Clash Verge Rev: https://github.com/clash-verge-rev/clash-verge-rev",
        "与 linktunnel clash 使用同一 External Controller API。",
        "",
        "在线面板仓库: https://github.com/MetaCubeX/Yacd-meta / https://github.com/MetaCubeX/metacubexd",
    ]
    click.echo("\n".join(lines))


@main.group("i2c")
def i2c_grp() -> None:
    """Linux I2C bus scan (needs permissions for /dev/i2c-*)."""


@i2c_grp.command("scan")
@click.option("--bus", default=1, show_default=True, type=int)
def i2c_scan_cmd(bus: int) -> None:
    raise SystemExit(i2c_scan(bus, click.get_text_stream("stdout")))


if __name__ == "__main__":
    main()
