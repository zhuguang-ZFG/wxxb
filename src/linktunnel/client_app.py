from __future__ import annotations

import os
import queue
import shlex
import shutil
import subprocess
import threading
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.parse import urlparse

import click

from linktunnel.clash.client import (
    ClashApiError,
    clash_delete,
    clash_get,
    clash_patch,
    clash_put,
    proxy_delay_path,
    proxy_path_segment,
)
from linktunnel.client_model import format_listen_line, parse_selector_groups
from linktunnel.proxy.mihomo_config import (
    default_profile_dir,
    external_controller_hints_from_config,
)


def _fetch_snapshot(api: str, secret: str | None) -> dict[str, Any]:
    """并行请求，降低首屏与手动刷新的总等待时间。"""

    def get_version() -> Any:
        return clash_get(api, "/version", secret=secret)

    def get_configs() -> Any:
        return clash_get(api, "/configs", secret=secret)

    def get_proxies() -> Any:
        return clash_get(api, "/proxies", secret=secret)

    def get_connections() -> Any:
        return clash_get(api, "/connections", secret=secret)

    with ThreadPoolExecutor(max_workers=4) as pool:
        f_ver = pool.submit(get_version)
        f_cfg = pool.submit(get_configs)
        f_px = pool.submit(get_proxies)
        f_cn = pool.submit(get_connections)
    return {
        "version": f_ver.result(),
        "configs": f_cfg.result(),
        "proxies": f_px.result(),
        "connections": f_cn.result(),
    }


def _fetch_light_snapshot(api: str, secret: str | None) -> dict[str, Any]:
    """仅刷新运行态配置与代理列表（自动刷新用，减轻与 Clash Verge 类似的轮询压力）。"""

    def get_configs() -> Any:
        return clash_get(api, "/configs", secret=secret)

    def get_proxies() -> Any:
        return clash_get(api, "/proxies", secret=secret)

    def get_connections() -> Any:
        return clash_get(api, "/connections", secret=secret)

    with ThreadPoolExecutor(max_workers=3) as pool:
        f_cfg = pool.submit(get_configs)
        f_px = pool.submit(get_proxies)
        f_cn = pool.submit(get_connections)
    return {
        "configs": f_cfg.result(),
        "proxies": f_px.result(),
        "connections": f_cn.result(),
    }


def linktunnel_cli_argv0() -> list[str]:
    """用于 subprocess：优先 PATH 中的 ``linktunnel``，否则 ``python -m linktunnel.cli``。"""
    import sys

    exe = shutil.which("linktunnel")
    if exe:
        return [exe]
    return [sys.executable, "-m", "linktunnel.cli"]


def _format_version_line(ver: Any) -> str:
    if isinstance(ver, dict):
        meta = ver.get("Meta") or ver.get("meta")
        if isinstance(meta, dict) and meta.get("version"):
            return str(meta.get("version", ""))
        if ver.get("version"):
            return str(ver.get("version"))
    return str(ver) if ver is not None else ""


class LinktunnelClientApp:
    def __init__(
        self,
        root: Any,
        *,
        initial_api: str,
        initial_secret: str,
        start_from_profile: bool,
    ) -> None:
        self._root = root
        self._result_q: queue.Queue = queue.Queue()
        self._request_inflight = False
        self._auto_timer_id: str | None = None
        self._last_rows: list[tuple[str, str, list[str]]] = []
        self._filter_after_id: str | None = None

        import tkinter as tk
        from tkinter import ttk

        self._tk = tk
        self._ttk = ttk

        root.title("linktunnel 客户端")
        root.geometry("920x640")
        root.minsize(720, 480)

        self._status_var = tk.StringVar(
            value="就绪。在「代理」页连接 Mihomo；「其他工具」可运行常用 CLI。"
        )
        status_bar = ttk.Frame(root)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_bar, textvariable=self._status_var, foreground="#333").pack(
            fill=tk.X, padx=8, pady=4
        )

        nb = ttk.Notebook(root)
        nb.pack(fill=tk.BOTH, expand=True)
        proxy_tab = ttk.Frame(nb, padding=8)
        nb.add(proxy_tab, text="代理 (Mihomo)")
        tools_tab = ttk.Frame(nb, padding=8)
        nb.add(tools_tab, text="其他工具")

        row1 = ttk.Frame(proxy_tab)
        row1.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row1, text="API").pack(side=tk.LEFT)
        self._api_var = tk.StringVar(value=initial_api)
        self._api_entry = ttk.Entry(row1, textvariable=self._api_var, width=42)
        self._api_entry.pack(side=tk.LEFT, padx=(6, 8))
        self._copy_api_btn = ttk.Button(row1, text="复制 API", command=self._on_copy_api, width=10)
        self._copy_api_btn.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(row1, text="Secret").pack(side=tk.LEFT)
        self._secret_var = tk.StringVar(value=initial_secret)
        self._secret_entry = ttk.Entry(row1, textvariable=self._secret_var, width=22, show="*")
        self._secret_entry.pack(side=tk.LEFT, padx=(6, 0))

        row2 = ttk.Frame(proxy_tab)
        row2.pack(fill=tk.X, pady=(0, 6))
        self._from_profile_var = tk.BooleanVar(value=start_from_profile)
        ttk.Checkbutton(
            row2,
            text="从默认 profile 的 config.yaml 读取 API / Secret",
            variable=self._from_profile_var,
        ).pack(side=tk.LEFT)
        self._refresh_btn = ttk.Button(row2, text="连接 / 刷新", command=self._on_refresh)
        self._refresh_btn.pack(side=tk.LEFT, padx=(12, 0))
        self._auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            row2, text="自动刷新", variable=self._auto_var, command=self._on_toggle_auto
        ).pack(side=tk.LEFT, padx=(12, 0))
        self._auto_secs_var = tk.StringVar(value="5")
        self._auto_combo = ttk.Combobox(
            row2,
            textvariable=self._auto_secs_var,
            values=("3", "5", "10", "15"),
            state="readonly",
            width=4,
        )
        self._auto_combo.pack(side=tk.LEFT, padx=(6, 0))
        ttk.Label(row2, text="秒").pack(side=tk.LEFT, padx=(4, 0))
        ttk.Label(row2, text="（双击节点切换；自动刷新为轻量轮询）").pack(
            side=tk.LEFT, padx=(12, 0)
        )
        self._auto_combo.bind("<<ComboboxSelected>>", lambda _e: self._on_auto_interval_changed())

        row3 = ttk.Frame(proxy_tab)
        row3.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row3, text="内核:").pack(side=tk.LEFT)
        self._ver_var = tk.StringVar(value="—")
        ttk.Label(row3, textvariable=self._ver_var, width=36).pack(side=tk.LEFT, padx=(4, 16))
        ttk.Label(row3, text="模式:").pack(side=tk.LEFT)
        self._mode_var = tk.StringVar(value="rule")
        self._mode_combo = ttk.Combobox(
            row3,
            textvariable=self._mode_var,
            values=("rule", "global", "direct"),
            state="readonly",
            width=10,
        )
        self._mode_combo.pack(side=tk.LEFT, padx=(4, 8))
        self._mode_btn = ttk.Button(row3, text="应用模式", command=self._on_apply_mode)
        self._mode_btn.pack(side=tk.LEFT)
        self._close_on_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            row3,
            text="切换模式时关闭连接",
            variable=self._close_on_mode_var,
        ).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Label(row3, text="监听:").pack(side=tk.LEFT, padx=(8, 0))
        self._ports_var = tk.StringVar(value="—")
        ttk.Label(row3, textvariable=self._ports_var, width=28).pack(side=tk.LEFT, padx=(4, 8))
        ttk.Label(row3, text="连接数:").pack(side=tk.LEFT, padx=(8, 0))
        self._conn_var = tk.StringVar(value="—")
        ttk.Label(row3, textvariable=self._conn_var).pack(side=tk.LEFT, padx=(4, 0))

        row_filter = ttk.Frame(proxy_tab)
        row_filter.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(row_filter, text="筛选").pack(side=tk.LEFT)
        self._filter_var = tk.StringVar(value="")
        self._filter_var.trace_add("write", lambda *_a: self._schedule_filter_rebuild())
        ttk.Entry(row_filter, textvariable=self._filter_var, width=50).pack(
            side=tk.LEFT, padx=(6, 0), fill=tk.X, expand=True
        )

        row_tools = ttk.Frame(proxy_tab)
        row_tools.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(row_tools, text="延迟测试 URL").pack(side=tk.LEFT)
        self._delay_url_var = tk.StringVar(value="http://www.gstatic.com/generate_204")
        ttk.Entry(row_tools, textvariable=self._delay_url_var, width=44).pack(
            side=tk.LEFT, padx=(6, 8)
        )
        self._delay_btn = ttk.Button(
            row_tools, text="测延迟（选中节点）", command=self._on_delay_test
        )
        self._delay_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._close_all_btn = ttk.Button(
            row_tools, text="关闭全部连接", command=self._on_close_all_connections
        )
        self._close_all_btn.pack(side=tk.LEFT)

        row_tree_tools = ttk.Frame(proxy_tab)
        row_tree_tools.pack(fill=tk.X, pady=(0, 4))
        self._apply_node_btn = ttk.Button(
            row_tree_tools, text="应用节点（选中子项）", command=self._on_apply_selected_node
        )
        self._apply_node_btn.pack(side=tk.LEFT)
        ttk.Label(row_tree_tools, text="Enter=应用 · F5=全量刷新").pack(side=tk.LEFT, padx=(12, 0))

        tree_frame = ttk.Frame(proxy_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        self._tree = ttk.Treeview(
            tree_frame,
            columns=("kind", "group", "node"),
            show="tree headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode="browse",
        )
        scroll_y.config(command=self._tree.yview)
        scroll_x.config(command=self._tree.xview)
        self._tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        self._tree.heading("#0", text="策略组 / 节点")
        self._tree["displaycolumns"] = ()
        self._tree.column("#0", width=560, minwidth=120)
        self._tree.bind("<Double-1>", self._on_tree_double)
        self._tree.bind("<Return>", self._on_tree_return)

        ttk.Label(
            tools_tab,
            text="在下方运行 linktunnel 子命令（只读/短命令）。若 PATH 中无 linktunnel，将使用 python -m linktunnel.cli。",
            wraplength=860,
        ).pack(anchor=tk.W, pady=(0, 6))

        tool_btns = ttk.Frame(tools_tab)
        tool_btns.pack(fill=tk.X, pady=4)
        presets: list[tuple[str, list[str]]] = [
            ("版本", ["--version"]),
            ("串口列表", ["serial", "list"]),
            ("proxy doctor", ["proxy", "doctor"]),
            ("proxy status", ["proxy", "status"]),
            ("dashboard info", ["dashboard", "info"]),
        ]
        for label, args in presets:
            ttk.Button(
                tool_btns,
                text=label,
                command=lambda a=args: self._run_cli_preset(a),
            ).pack(side=tk.LEFT, padx=4, pady=2)

        custom_row = ttk.Frame(tools_tab)
        custom_row.pack(fill=tk.X, pady=6)
        ttk.Label(custom_row, text="自定义参数").pack(side=tk.LEFT)
        self._tool_custom_var = tk.StringVar(value="serial list")
        ttk.Entry(custom_row, textvariable=self._tool_custom_var, width=52).pack(
            side=tk.LEFT, padx=6, fill=tk.X, expand=True
        )
        ttk.Button(custom_row, text="运行", command=self._on_run_custom_cli).pack(side=tk.LEFT)

        out_fr = ttk.Frame(tools_tab)
        out_fr.pack(fill=tk.BOTH, expand=True, pady=4)
        tscroll = ttk.Scrollbar(out_fr)
        tscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._tool_text = tk.Text(out_fr, height=14, wrap="word", yscrollcommand=tscroll.set)
        tscroll.config(command=self._tool_text.yview)
        self._tool_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        root.bind("<F5>", lambda _e: self._on_refresh(full=True))
        root.bind("<Control-l>", lambda _e: self._clear_filter())
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._root.after(120, self._poll_queue)
        if start_from_profile:
            self._root.after(200, lambda: self._on_refresh(full=True))

    def _read_endpoints(self) -> tuple[str, str | None]:
        """Must run on Tk main thread only."""
        if self._from_profile_var.get():
            cfg = default_profile_dir() / "config.yaml"
            if not cfg.is_file():
                raise click.ClickException(
                    f"未找到 {cfg}。请先执行 linktunnel proxy init，或取消勾选「从 profile 读取」。"
                )
            api_u, sec_u = external_controller_hints_from_config(cfg)
            self._api_var.set(api_u)
            self._secret_var.set(sec_u)
            api = api_u.strip().rstrip("/")
            sec = sec_u.strip() or None
            self._validate_api_url(api)
            return api, sec
        api = self._api_var.get().strip().rstrip("/")
        self._validate_api_url(api)
        sec = self._secret_var.get().strip() or None
        return api, sec

    def _validate_api_url(self, api: str) -> None:
        if not api:
            raise click.ClickException("API 不能为空，例如 http://127.0.0.1:9090")
        p = urlparse(api)
        if p.scheme not in ("http", "https") or not p.netloc:
            raise click.ClickException("API 格式不正确，应为 http(s)://host:port")

    def _set_status(self, text: str) -> None:
        from datetime import datetime

        ts = datetime.now().strftime("%H:%M:%S")
        self._status_var.set(f"[{ts}] {text}")

    def _on_copy_api(self) -> None:
        try:
            self._root.clipboard_clear()
            self._root.clipboard_append(self._api_var.get().strip())
            self._set_status("已复制 API 到剪贴板。")
        except self._tk.TclError:
            self._set_status("复制失败（剪贴板不可用）。")

    def _clear_filter(self) -> None:
        self._filter_var.set("")
        self._set_status("已清空筛选。")

    def _set_busy(self, busy: bool) -> None:
        self._request_inflight = busy
        state = "disabled" if busy else "normal"
        self._refresh_btn.config(state=state)
        self._mode_btn.config(state=state)
        self._delay_btn.config(state=state)
        self._close_all_btn.config(state=state)
        self._apply_node_btn.config(state=state)
        self._copy_api_btn.config(state=state)

    def _on_refresh(self, *, full: bool = True) -> None:
        if self._request_inflight:
            self._set_status("上一次请求还在进行中，请稍候…")
            return
        try:
            api, sec = self._read_endpoints()
        except click.ClickException as e:
            self._set_status(str(e))
            return
        self._set_status("正在请求 External Controller…" if full else "正在轻量刷新…")
        self._set_busy(True)

        def job() -> None:
            try:
                if full:
                    snap = _fetch_snapshot(api, sec)
                    self._result_q.put(("ok", snap, "已更新。"))
                else:
                    snap = _fetch_light_snapshot(api, sec)
                    self._result_q.put(("ok", snap, "已自动刷新（轻量）。"))
            except Exception as e:
                self._result_q.put(("err", e))

        threading.Thread(target=job, daemon=True).start()

    def _on_toggle_auto(self) -> None:
        if self._auto_var.get():
            self._set_status(f"已开启自动刷新（每 {self._auto_secs_var.get()} 秒）。")
            self._schedule_auto_refresh(reset=True)
        else:
            if self._auto_timer_id is not None:
                self._root.after_cancel(self._auto_timer_id)
                self._auto_timer_id = None
            self._set_status("已关闭自动刷新。")

    def _on_auto_interval_changed(self) -> None:
        if self._auto_var.get():
            self._schedule_auto_refresh(reset=True)

    def _schedule_auto_refresh(self, *, reset: bool = False) -> None:
        if not self._auto_var.get():
            return
        if reset and self._auto_timer_id is not None:
            self._root.after_cancel(self._auto_timer_id)
            self._auto_timer_id = None
        try:
            interval_ms = max(1, int(self._auto_secs_var.get())) * 1000
        except ValueError:
            interval_ms = 5000
        self._auto_timer_id = self._root.after(interval_ms, self._auto_tick)

    def _auto_tick(self) -> None:
        self._auto_timer_id = None
        if not self._auto_var.get():
            return
        if not self._request_inflight:
            self._on_refresh(full=False)
        self._schedule_auto_refresh()

    def _schedule_filter_rebuild(self) -> None:
        if self._filter_after_id is not None:
            self._root.after_cancel(self._filter_after_id)
        self._filter_after_id = self._root.after(120, self._filter_rebuild_tick)

    def _filter_rebuild_tick(self) -> None:
        self._filter_after_id = None
        self._rebuild_tree()

    def _rebuild_tree(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        needle = self._filter_var.get().strip().lower()
        for group, now, nodes in self._last_rows:
            if needle:
                gmatch = needle in group.lower()
                show_nodes = nodes if gmatch else [n for n in nodes if needle in n.lower()]
                if not show_nodes:
                    continue
            else:
                show_nodes = nodes
            label = f"{group}  （当前: {now}）"
            gid = f"g:{group}"
            self._tree.insert("", "end", iid=gid, text=label, values=("group", group, ""))
            for i, node in enumerate(show_nodes):
                nid = f"n:{group}:{i}"
                self._tree.insert(gid, "end", iid=nid, text=node, values=("node", group, node))

    def _run_cli_preset(self, args: list[str]) -> None:
        self._run_cli_async(args)

    def _on_run_custom_cli(self) -> None:
        raw = self._tool_custom_var.get().strip()
        if not raw:
            self._set_status("请输入自定义参数。")
            return
        try:
            extra = shlex.split(raw)
        except ValueError as e:
            self._set_status(f"参数解析失败: {e}")
            return
        self._run_cli_async(extra)

    def _run_cli_async(self, args: list[str]) -> None:
        self._set_status("正在运行子命令…")

        def job() -> None:
            try:
                argv = linktunnel_cli_argv0() + args
                r = subprocess.run(
                    argv,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=os.environ.copy(),
                )
                parts: list[str] = []
                if r.stdout:
                    parts.append(r.stdout)
                if r.stderr:
                    parts.append(r.stderr)
                text = "\n".join(parts) if parts else "(无输出)"
                if r.returncode != 0:
                    text = f"[exit {r.returncode}]\n{text}"
                self._result_q.put(("tool", text))
            except Exception as e:
                self._result_q.put(("tool", f"错误: {e!s}"))

        threading.Thread(target=job, daemon=True).start()

    def _poll_queue(self) -> None:
        try:
            while True:
                item = self._result_q.get_nowait()
                if not isinstance(item, tuple) or not item:
                    continue
                kind = item[0]
                if kind == "ok":
                    snap = item[1] if len(item) > 1 else {}
                    msg = item[2] if len(item) > 2 else "已更新。"
                    self._apply_snapshot(snap)
                    self._set_status(msg)
                    self._set_busy(False)
                elif kind == "status":
                    self._set_status(str(item[1]) if len(item) > 1 else "")
                    self._set_busy(False)
                elif kind == "tool":
                    txt = item[1] if len(item) > 1 else ""
                    self._tool_text.delete("1.0", "end")
                    self._tool_text.insert("1.0", txt)
                    self._set_status("子命令已结束。")
                else:
                    payload = item[1] if len(item) > 1 else Exception("unknown error")
                    self._handle_err(payload)
                    self._set_busy(False)
        except queue.Empty:
            pass
        self._root.after(200, self._poll_queue)

    def _handle_err(self, e: BaseException) -> None:
        if isinstance(e, click.ClickException):
            self._set_status(str(e))
            return
        if isinstance(e, ClashApiError):
            self._set_status(f"API 错误: {e}")
            return
        if isinstance(e, urllib.error.URLError):
            self._set_status(f"网络错误: {e.reason!s}")
            return
        self._set_status(f"错误: {e!s}")

    def _apply_snapshot(self, snap: dict[str, Any]) -> None:
        if "version" in snap:
            ver = snap.get("version")
            self._ver_var.set(_format_version_line(ver) or "—")

        cfg = snap.get("configs")
        if isinstance(cfg, dict):
            if cfg.get("mode"):
                self._mode_var.set(str(cfg["mode"]).lower())
            self._ports_var.set(format_listen_line(cfg))

        if "connections" in snap:
            conns = snap.get("connections")
            if isinstance(conns, dict):
                clist = conns.get("connections")
                n = len(clist) if isinstance(clist, list) else 0
                self._conn_var.set(str(n))
            else:
                self._conn_var.set("—")

        prox = snap.get("proxies")
        if not isinstance(prox, dict):
            self._last_rows = []
            self._rebuild_tree()
            return
        self._last_rows = parse_selector_groups(prox)
        self._rebuild_tree()

    def _on_apply_mode(self) -> None:
        mode = self._mode_var.get().strip().lower()
        if mode not in ("rule", "global", "direct"):
            self._set_status("模式必须是 rule / global / direct")
            return
        try:
            api, sec = self._read_endpoints()
        except click.ClickException as e:
            self._set_status(str(e))
            return
        close_first = self._close_on_mode_var.get()

        def job() -> None:
            try:
                if close_first:
                    clash_delete(api, "/connections", secret=sec)
                clash_patch(api, "/configs", {"mode": mode}, secret=sec)
                self._result_q.put(("ok", _fetch_snapshot(api, sec), f"模式已切换到 {mode}。"))
            except Exception as e:
                self._result_q.put(("err", e))

        self._set_status(f"正在设置模式为 {mode}…")
        self._set_busy(True)
        threading.Thread(target=job, daemon=True).start()

    def _on_close_all_connections(self) -> None:
        if self._request_inflight:
            self._set_status("上一次请求还在进行中，请稍候…")
            return
        try:
            api, sec = self._read_endpoints()
        except click.ClickException as e:
            self._set_status(str(e))
            return

        def job() -> None:
            try:
                clash_delete(api, "/connections", secret=sec)
                self._result_q.put(("ok", _fetch_light_snapshot(api, sec), "已关闭全部连接。"))
            except Exception as e:
                self._result_q.put(("err", e))

        self._set_status("正在关闭全部连接…")
        self._set_busy(True)
        threading.Thread(target=job, daemon=True).start()

    def _on_delay_test(self) -> None:
        if self._request_inflight:
            self._set_status("上一次请求还在进行中，请稍候…")
            return
        sel = self._tree.selection()
        if not sel:
            self._set_status("请先在列表中选中一个节点。")
            return
        vals = self._tree.item(sel[0], "values")
        if not vals or vals[0] != "node":
            self._set_status("测延迟需要选中具体节点（子项），不是策略组。")
            return
        _group, node = vals[1], vals[2]
        url = self._delay_url_var.get().strip()
        if not url:
            self._set_status("请填写延迟测试 URL。")
            return
        try:
            api, sec = self._read_endpoints()
        except click.ClickException as e:
            self._set_status(str(e))
            return

        def job() -> None:
            try:
                path = proxy_delay_path(node, url, 5000)
                data = clash_get(api, path, secret=sec, timeout=25.0)
                delay_val: Any = None
                if isinstance(data, dict):
                    delay_val = data.get("delay")
                if delay_val is not None:
                    msg = f"节点「{node}」延迟: {delay_val} ms"
                else:
                    msg = f"节点「{node}」测试结果: {data!r}"
                self._result_q.put(("status", msg))
            except Exception as e:
                self._result_q.put(("err", e))

        self._set_status(f"正在测试节点「{node}」延迟…")
        self._set_busy(True)
        threading.Thread(target=job, daemon=True).start()

    def _enqueue_switch_proxy(self, group: str, node: str) -> None:
        try:
            api, sec = self._read_endpoints()
        except click.ClickException as e:
            self._set_status(str(e))
            return

        def job() -> None:
            try:
                path = f"/proxies/{proxy_path_segment(group)}"
                clash_put(api, path, {"name": node}, secret=sec)
                self._result_q.put(("ok", _fetch_snapshot(api, sec), f"已切换 {group} -> {node}"))
            except Exception as e:
                self._result_q.put(("err", e))

        self._set_status(f"正在切换 {group} → {node}…")
        self._set_busy(True)
        threading.Thread(target=job, daemon=True).start()

    def _on_apply_selected_node(self) -> None:
        sel = self._tree.selection()
        if not sel:
            self._set_status("请先选中一个节点（子项）。")
            return
        vals = self._tree.item(sel[0], "values")
        if not vals or vals[0] != "node":
            self._set_status("请选中子节点后再应用（策略组行不能应用）。")
            return
        self._enqueue_switch_proxy(vals[1], vals[2])

    def _on_tree_return(self, _event: Any) -> str:
        self._on_apply_selected_node()
        return "break"

    def _on_tree_double(self, _event: Any) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        vals = self._tree.item(sel[0], "values")
        if not vals or vals[0] != "node":
            return
        self._enqueue_switch_proxy(vals[1], vals[2])

    def _on_close(self) -> None:
        if self._auto_timer_id is not None:
            self._root.after_cancel(self._auto_timer_id)
            self._auto_timer_id = None
        if self._filter_after_id is not None:
            self._root.after_cancel(self._filter_after_id)
            self._filter_after_id = None
        self._root.destroy()


def run_client_app(
    *,
    from_profile: bool,
    api: str,
    secret: str,
) -> None:
    try:
        import tkinter as tk
    except ImportError as e:
        raise click.ClickException(
            "当前 Python 未包含 tkinter。macOS 请使用 python.org 安装包或 "
            "`brew install python-tk`；Linux 请安装 `python3-tk`。"
        ) from e

    root = tk.Tk()
    try:
        LinktunnelClientApp(
            root,
            initial_api=api.strip().rstrip("/"),
            initial_secret=secret,
            start_from_profile=from_profile,
        )
        root.mainloop()
    except tk.TclError as e:
        raise click.ClickException(
            "无法创建图形界面（常见于无 DISPLAY 的 SSH 会话）。请在带桌面的环境运行。"
        ) from e


def client_main() -> None:
    import sys

    sys.argv = [sys.argv[0], "client", *sys.argv[1:]]
    from linktunnel.cli import main

    main()
