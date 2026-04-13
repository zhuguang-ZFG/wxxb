from __future__ import annotations

import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


def mihomo_binary_names_to_try() -> list[str]:
    """Executable names commonly used after download / install (cross-OS)."""
    if sys.platform == "win32":
        return [
            "mihomo.exe",
            "clash-meta.exe",
            "clash.exe",
            "mihomo-windows-amd64.exe",
            "mihomo",
        ]
    return ["mihomo", "clash-meta", "clash"]


def mihomo_release_hint() -> str:
    """One-line summary: which Mihomo release asset matches this machine."""
    sysname = platform.system()
    machine = platform.machine().lower()
    if sysname == "Windows":
        return "Suggested asset: mihomo-windows-amd64.exe (x86_64) or mihomo-windows-arm64.exe"
    if sysname == "Darwin":
        arch = "arm64" if "arm" in machine else "amd64"
        return f"Suggested asset: mihomo-darwin-{arch}-*.gz (extract → chmod +x → PATH)"
    if sysname == "Linux":
        if "aarch" in machine or "arm64" in machine:
            return "Suggested asset: mihomo-linux-arm64-*.gz"
        return "Suggested asset: mihomo-linux-amd64-*.gz"
    return "See GitHub Releases for your OS/arch."


def mihomo_doctor_package_lines() -> list[str]:
    """Printed first by ``proxy doctor``: OS/arch + download hint."""
    return [
        "=== Mihomo 推荐包（当前系统）===",
        f"platform: {platform.system()}  machine: {platform.machine()}",
        mihomo_release_hint(),
        "Releases: https://github.com/MetaCubeX/mihomo/releases",
    ]


def find_mihomo_binary(explicit: str | None = None) -> str | None:
    if explicit:
        p = Path(os.path.expanduser(explicit)).resolve()
        return str(p) if p.is_file() else None
    env = os.environ.get("MIHOMO_BIN") or os.environ.get("CLASH_META_BIN")
    if env:
        ep = Path(os.path.expanduser(env)).resolve()
        if ep.is_file():
            return str(ep)
    for name in mihomo_binary_names_to_try():
        w = shutil.which(name)
        if w:
            return w
    return None


def _pid_file(workdir: Path) -> Path:
    return workdir / ".linktunnel" / "mihomo.pid"


def is_running(workdir: Path) -> tuple[bool, int | None]:
    pf = _pid_file(workdir)
    if not pf.is_file():
        return False, None
    try:
        pid = int(pf.read_text(encoding="utf-8").strip())
    except ValueError:
        return False, None
    try:
        os.kill(pid, 0)
    except OSError:
        return False, pid
    return True, pid


def start_mihomo(
    workdir: Path,
    config_path: Path,
    *,
    binary: str | None = None,
) -> int:
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "providers").mkdir(parents=True, exist_ok=True)
    bin_path = find_mihomo_binary(binary)
    if not bin_path:
        raise FileNotFoundError("mihomo binary not found; set MIHOMO_BIN or install mihomo")

    running, old_pid = is_running(workdir)
    if running and old_pid:
        raise RuntimeError(f"mihomo already running (pid {old_pid}) for this profile")

    log_path = workdir / "mihomo.log"
    cfg_abs = config_path.resolve()
    wd_abs = workdir.resolve()
    args = [bin_path, "-d", str(wd_abs), "-f", str(cfg_abs)]
    kw: dict = {
        "args": args,
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.STDOUT,
    }
    if sys.platform == "win32":
        cflags = 0
        cng = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        cnw = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        cflags |= cng | cnw
        if cflags:
            kw["creationflags"] = cflags
    else:
        kw["start_new_session"] = True
    with open(log_path, "ab", buffering=0) as lf:
        kw["stdout"] = lf
        proc = subprocess.Popen(**kw)

    pid_dir = workdir / ".linktunnel"
    pid_dir.mkdir(parents=True, exist_ok=True)
    _pid_file(workdir).write_text(str(proc.pid), encoding="utf-8")
    time.sleep(0.15)
    if proc.poll() is not None:
        raise RuntimeError(f"mihomo exited immediately (code {proc.poll()}); see {log_path}")
    return proc.pid


def stop_mihomo(workdir: Path) -> bool:
    pf = _pid_file(workdir)
    if not pf.is_file():
        return False
    try:
        pid = int(pf.read_text(encoding="utf-8").strip())
    except ValueError:
        pf.unlink(missing_ok=True)
        return False
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                check=False,
            )
        else:
            os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    pf.unlink(missing_ok=True)
    return True
