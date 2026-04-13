"""
代理管理模块

整合 client_app.py 功能，提供 Mihomo/Clash 代理管理界面。
"""

from __future__ import annotations

import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

from linktunnel.unified_gui.core.base_module import BaseModule

try:
    from PyQt6.QtCore import QTimer, pyqtSignal
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
    )
    
    from linktunnel.clash.client import (
        ClashApiError,
        clash_delete,
        clash_get,
        clash_patch,
        clash_put,
        proxy_delay_path,
        proxy_path_segment,
    )
    from linktunnel.client_model import format_listen_line
    from linktunnel.proxy.mihomo_config import (
        default_profile_dir,
        external_controller_hints_from_config,
    )
    
    class ProxyModule(BaseModule):
        """代理管理模块（PyQt6 版本）"""
        
        # 自定义信号
        snapshot_ready = pyqtSignal(dict)  # 快照数据就绪信号
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent=None
        ):
            super().__init__(config_manager, log_manager, parent)
            
            # 状态变量
            self._result_queue: queue.Queue = queue.Queue()
            self._request_inflight = False
            self._auto_timer: QTimer | None = None
            
            # 连接快照数据就绪信号
            self.snapshot_ready.connect(self._apply_snapshot)
            
            # 设置 UI
            self._setup_ui()
            
            # 启动队列轮询
            self._poll_timer = QTimer(self)
            self._poll_timer.timeout.connect(self._poll_queue)
            self._poll_timer.start(200)
            
            # 加载配置
            self._load_saved_config()
            
            # 绑定快捷键
            from PyQt6.QtGui import QKeySequence, QShortcut
            refresh_shortcut = QShortcut(QKeySequence("F5"), self)
            refresh_shortcut.activated.connect(lambda: self._on_refresh(full=True))
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(6)
            
            # 第一行：API 和 Secret 配置
            row1 = QHBoxLayout()
            row1.addWidget(QLabel("API:"))
            self._api_entry = QLineEdit()
            self._api_entry.setPlaceholderText("http://127.0.0.1:9090")
            self._api_entry.setMinimumWidth(300)
            row1.addWidget(self._api_entry)
            
            self._copy_api_btn = QPushButton("复制 API")
            self._copy_api_btn.clicked.connect(self._on_copy_api)
            row1.addWidget(self._copy_api_btn)
            
            row1.addWidget(QLabel("Secret:"))
            self._secret_entry = QLineEdit()
            self._secret_entry.setEchoMode(QLineEdit.EchoMode.Password)
            self._secret_entry.setMinimumWidth(150)
            row1.addWidget(self._secret_entry)
            
            row1.addStretch()
            layout.addLayout(row1)
            
            # 第二行：从 profile 读取和刷新控制
            row2 = QHBoxLayout()
            self._from_profile_cb = QCheckBox("从默认 profile 的 config.yaml 读取 API / Secret")
            row2.addWidget(self._from_profile_cb)
            
            self._refresh_btn = QPushButton("连接 / 刷新")
            self._refresh_btn.clicked.connect(lambda: self._on_refresh(full=True))
            row2.addWidget(self._refresh_btn)
            
            self._auto_refresh_cb = QCheckBox("自动刷新")
            self._auto_refresh_cb.stateChanged.connect(self._on_toggle_auto_refresh)
            row2.addWidget(self._auto_refresh_cb)
            
            self._auto_interval_combo = QComboBox()
            self._auto_interval_combo.addItems(["3", "5", "10", "15"])
            self._auto_interval_combo.setCurrentText("5")
            self._auto_interval_combo.setMaximumWidth(60)
            self._auto_interval_combo.currentTextChanged.connect(self._on_auto_interval_changed)
            row2.addWidget(self._auto_interval_combo)
            row2.addWidget(QLabel("秒"))
            
            row2.addStretch()
            layout.addLayout(row2)
            
            # 分隔线
            line1 = QFrame()
            line1.setFrameShape(QFrame.Shape.HLine)
            line1.setFrameShadow(QFrame.Shadow.Sunken)
            layout.addWidget(line1)
            
            # 第三行：内核版本、运行模式、监听端口、连接数
            row3 = QHBoxLayout()
            
            # 内核版本
            row3.addWidget(QLabel("内核:"))
            self._version_label = QLabel("—")
            self._version_label.setMinimumWidth(200)
            row3.addWidget(self._version_label)
            
            row3.addSpacing(20)
            
            # 运行模式
            row3.addWidget(QLabel("模式:"))
            self._mode_combo = QComboBox()
            self._mode_combo.addItems(["rule", "global", "direct"])
            self._mode_combo.setMaximumWidth(100)
            row3.addWidget(self._mode_combo)
            
            self._apply_mode_btn = QPushButton("应用模式")
            self._apply_mode_btn.clicked.connect(self._on_apply_mode)
            row3.addWidget(self._apply_mode_btn)
            
            row3.addSpacing(20)
            
            # 监听端口
            row3.addWidget(QLabel("监听:"))
            self._ports_label = QLabel("—")
            self._ports_label.setMinimumWidth(200)
            row3.addWidget(self._ports_label)
            
            row3.addSpacing(20)
            
            # 连接数
            row3.addWidget(QLabel("连接数:"))
            self._conn_label = QLabel("—")
            self._conn_label.setMinimumWidth(50)
            row3.addWidget(self._conn_label)
            
            row3.addStretch()
            layout.addLayout(row3)
            
            # 第四行：模式切换选项
            row4 = QHBoxLayout()
            self._close_on_mode_cb = QCheckBox("切换模式时关闭连接")
            self._close_on_mode_cb.setChecked(True)
            row4.addWidget(self._close_on_mode_cb)
            row4.addStretch()
            layout.addLayout(row4)
            
            # 分隔线
            line2 = QFrame()
            line2.setFrameShape(QFrame.Shape.HLine)
            line2.setFrameShadow(QFrame.Shadow.Sunken)
            layout.addWidget(line2)
            
            # 第五行：筛选和工具按钮
            row5 = QHBoxLayout()
            row5.addWidget(QLabel("筛选:"))
            self._filter_entry = QLineEdit()
            self._filter_entry.setPlaceholderText("输入关键词筛选节点...")
            self._filter_entry.setMinimumWidth(300)
            self._filter_entry.textChanged.connect(self._on_filter_changed)
            row5.addWidget(self._filter_entry)
            
            row5.addSpacing(20)
            
            row5.addWidget(QLabel("延迟测试 URL:"))
            self._delay_url_entry = QLineEdit()
            self._delay_url_entry.setText("http://www.gstatic.com/generate_204")
            self._delay_url_entry.setMinimumWidth(250)
            row5.addWidget(self._delay_url_entry)
            
            self._delay_test_btn = QPushButton("测延迟（选中节点）")
            self._delay_test_btn.clicked.connect(self._on_delay_test)
            row5.addWidget(self._delay_test_btn)
            
            self._close_all_btn = QPushButton("关闭全部连接")
            self._close_all_btn.clicked.connect(self._on_close_all_connections)
            row5.addWidget(self._close_all_btn)
            
            self._open_dashboard_btn = QPushButton("打开控制台")
            self._open_dashboard_btn.clicked.connect(self._on_open_dashboard)
            row5.addWidget(self._open_dashboard_btn)
            
            row5.addStretch()
            layout.addLayout(row5)
            
            # 第六行：树形控件工具按钮
            row6 = QHBoxLayout()
            self._apply_node_btn = QPushButton("应用节点（选中子项）")
            self._apply_node_btn.clicked.connect(self._on_apply_selected_node)
            row6.addWidget(self._apply_node_btn)
            
            hint_label = QLabel("提示: 双击节点切换 · F5 全量刷新")
            hint_label.setStyleSheet("color: gray;")
            row6.addWidget(hint_label)
            
            row6.addStretch()
            layout.addLayout(row6)
            
            # 策略组和节点树形列表
            from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
            self._tree = QTreeWidget()
            self._tree.setHeaderLabels(["策略组 / 节点"])
            self._tree.setColumnCount(3)
            self._tree.setHeaderLabels(["策略组 / 节点", "类型", "组名"])
            self._tree.setColumnHidden(1, True)  # 隐藏类型列
            self._tree.setColumnHidden(2, True)  # 隐藏组名列
            self._tree.setMinimumHeight(300)
            self._tree.itemDoubleClicked.connect(self._on_tree_double_click)
            layout.addWidget(self._tree)
            
            # 存储原始数据用于筛选
            self._last_rows: list[tuple[str, str, list[str]]] = []
            self._filter_timer: QTimer | None = None
            
            layout.addStretch()
        
        def _load_saved_config(self) -> None:
            """加载保存的配置"""
            config = self.load_config()
            self._api_entry.setText(config.get("api", "http://127.0.0.1:9090"))
            self._secret_entry.setText(config.get("secret", ""))
            self._from_profile_cb.setChecked(config.get("from_profile", True))
            self._auto_refresh_cb.setChecked(config.get("auto_refresh", False))
            self._auto_interval_combo.setCurrentText(str(config.get("auto_refresh_interval", 5)))
            
            # 如果配置为从 profile 读取，则在启动后自动连接
            if config.get("from_profile", True):
                QTimer.singleShot(200, lambda: self._on_refresh(full=True))
        
        def _save_current_config(self) -> None:
            """保存当前配置"""
            config = {
                "api": self._api_entry.text().strip(),
                "secret": self._secret_entry.text(),
                "from_profile": self._from_profile_cb.isChecked(),
                "auto_refresh": self._auto_refresh_cb.isChecked(),
                "auto_refresh_interval": int(self._auto_interval_combo.currentText()),
            }
            self.save_config(config)
        
        def _read_endpoints(self) -> tuple[str, str | None]:
            """读取 API 端点配置"""
            if self._from_profile_cb.isChecked():
                cfg = default_profile_dir() / "config.yaml"
                if not cfg.is_file():
                    raise ValueError(
                        f"未找到 {cfg}。请先执行 linktunnel proxy init，或取消勾选「从 profile 读取」。"
                    )
                api_u, sec_u = external_controller_hints_from_config(cfg)
                self._api_entry.setText(api_u)
                self._secret_entry.setText(sec_u)
                api = api_u.strip().rstrip("/")
                sec = sec_u.strip() or None
                return api, sec
            
            api = self._api_entry.text().strip().rstrip("/")
            if not api:
                raise ValueError("API 不能为空，例如 http://127.0.0.1:9090")
            sec = self._secret_entry.text().strip() or None
            return api, sec
        
        def _on_copy_api(self) -> None:
            """复制 API 到剪贴板"""
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(self._api_entry.text().strip())
                self.log_info("已复制 API 到剪贴板")
        
        def _on_refresh(self, *, full: bool = True) -> None:
            """刷新代理信息"""
            if self._request_inflight:
                self.log_warning("上一次请求还在进行中，请稍候…")
                return
            
            try:
                api, sec = self._read_endpoints()
            except ValueError as e:
                self.log_error(str(e))
                return
            
            self.log_info("正在请求 External Controller…" if full else "正在轻量刷新…")
            self._set_busy(True)
            
            def job() -> None:
                try:
                    if full:
                        snap = self._fetch_snapshot(api, sec)
                        self._result_queue.put(("ok", snap, "已更新"))
                    else:
                        snap = self._fetch_light_snapshot(api, sec)
                        self._result_queue.put(("ok", snap, "已自动刷新（轻量）"))
                except Exception as e:
                    self._result_queue.put(("err", e))
            
            threading.Thread(target=job, daemon=True).start()
        
        def _fetch_snapshot(self, api: str, secret: str | None) -> dict[str, Any]:
            """并行请求完整快照"""
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
        
        def _fetch_light_snapshot(self, api: str, secret: str | None) -> dict[str, Any]:
            """并行请求轻量快照（不包含版本信息）"""
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
        
        def _on_toggle_auto_refresh(self, state: int) -> None:
            """切换自动刷新"""
            if self._auto_refresh_cb.isChecked():
                interval = int(self._auto_interval_combo.currentText())
                self.log_info(f"已开启自动刷新（每 {interval} 秒）")
                self._schedule_auto_refresh(reset=True)
            else:
                if self._auto_timer:
                    self._auto_timer.stop()
                    self._auto_timer = None
                self.log_info("已关闭自动刷新")
            
            self._save_current_config()
        
        def _on_auto_interval_changed(self, text: str) -> None:
            """自动刷新间隔改变"""
            if self._auto_refresh_cb.isChecked():
                self._schedule_auto_refresh(reset=True)
            self._save_current_config()
        
        def _schedule_auto_refresh(self, *, reset: bool = False) -> None:
            """调度自动刷新"""
            if not self._auto_refresh_cb.isChecked():
                return
            
            if reset and self._auto_timer:
                self._auto_timer.stop()
                self._auto_timer = None
            
            try:
                interval_ms = max(1, int(self._auto_interval_combo.currentText())) * 1000
            except ValueError:
                interval_ms = 5000
            
            if not self._auto_timer:
                self._auto_timer = QTimer(self)
                self._auto_timer.timeout.connect(self._auto_tick)
            
            self._auto_timer.start(interval_ms)
        
        def _auto_tick(self) -> None:
            """自动刷新定时器触发"""
            if not self._auto_refresh_cb.isChecked():
                return
            
            if not self._request_inflight:
                self._on_refresh(full=False)
        
        def _on_apply_mode(self) -> None:
            """应用代理模式"""
            mode = self._mode_combo.currentText().strip().lower()
            if mode not in ("rule", "global", "direct"):
                self.log_error("模式必须是 rule / global / direct")
                return
            
            try:
                api, sec = self._read_endpoints()
            except ValueError as e:
                self.log_error(str(e))
                return
            
            close_first = self._close_on_mode_cb.isChecked()
            
            def job() -> None:
                try:
                    if close_first:
                        clash_delete(api, "/connections", secret=sec)
                    clash_patch(api, "/configs", {"mode": mode}, secret=sec)
                    snap = self._fetch_snapshot(api, sec)
                    self._result_queue.put(("ok", snap, f"模式已切换到 {mode}"))
                except Exception as e:
                    self._result_queue.put(("err", e))
            
            self.log_info(f"正在设置模式为 {mode}…")
            self._set_busy(True)
            threading.Thread(target=job, daemon=True).start()
        
        def _set_busy(self, busy: bool) -> None:
            """设置忙碌状态"""
            self._request_inflight = busy
            self._refresh_btn.setEnabled(not busy)
            self._apply_mode_btn.setEnabled(not busy)
            self._copy_api_btn.setEnabled(not busy)
            self._delay_test_btn.setEnabled(not busy)
            self._close_all_btn.setEnabled(not busy)
            self._apply_node_btn.setEnabled(not busy)
        
        def _poll_queue(self) -> None:
            """轮询结果队列"""
            try:
                while True:
                    item = self._result_queue.get_nowait()
                    if not isinstance(item, tuple) or not item:
                        continue
                    
                    kind = item[0]
                    if kind == "ok":
                        snap = item[1] if len(item) > 1 else {}
                        msg = item[2] if len(item) > 2 else "已更新"
                        self.snapshot_ready.emit(snap)
                        self.log_info(msg)
                        self._set_busy(False)
                    elif kind == "status":
                        msg = item[1] if len(item) > 1 else ""
                        self.log_info(msg)
                        self._set_busy(False)
                    elif kind == "err":
                        error = item[1] if len(item) > 1 else Exception("unknown error")
                        self._handle_error(error)
                        self._set_busy(False)
            except queue.Empty:
                pass
        
        def _handle_error(self, e: BaseException) -> None:
            """处理错误"""
            if isinstance(e, ClashApiError):
                self.log_error(f"API 错误: {e}")
            elif isinstance(e, ValueError):
                self.log_error(str(e))
            else:
                self.log_error(f"错误: {e!s}")
        
        def _apply_snapshot(self, snap: dict[str, Any]) -> None:
            """应用快照数据到 UI"""
            # 更新内核版本
            if "version" in snap:
                ver = snap.get("version")
                self._version_label.setText(self._format_version_line(ver))
            
            # 更新配置信息
            cfg = snap.get("configs")
            if isinstance(cfg, dict):
                # 更新运行模式
                if cfg.get("mode"):
                    mode = str(cfg["mode"]).lower()
                    index = self._mode_combo.findText(mode)
                    if index >= 0:
                        self._mode_combo.setCurrentIndex(index)
                
                # 更新监听端口
                self._ports_label.setText(format_listen_line(cfg))
            
            # 更新连接数
            if "connections" in snap:
                conns = snap.get("connections")
                if isinstance(conns, dict):
                    clist = conns.get("connections")
                    n = len(clist) if isinstance(clist, list) else 0
                    self._conn_label.setText(str(n))
                else:
                    self._conn_label.setText("—")
            
            # TODO: Task 13.3 - 更新策略组和节点列表
            # 更新策略组和节点列表
            prox = snap.get("proxies")
            if isinstance(prox, dict):
                from linktunnel.client_model import parse_selector_groups
                self._last_rows = parse_selector_groups(prox)
                self._rebuild_tree()
            else:
                self._last_rows = []
                self._rebuild_tree()
        
        def _on_filter_changed(self, text: str) -> None:
            """筛选文本改变时调度重建树"""
            if self._filter_timer:
                self._filter_timer.stop()
            
            self._filter_timer = QTimer(self)
            self._filter_timer.setSingleShot(True)
            self._filter_timer.timeout.connect(self._rebuild_tree)
            self._filter_timer.start(200)  # 200ms 防抖
        
        def _rebuild_tree(self) -> None:
            """根据筛选条件重建树形列表"""
            self._tree.clear()
            
            needle = self._filter_entry.text().strip().lower()
            
            for group, now, nodes in self._last_rows:
                # 如果有筛选条件
                if needle:
                    # 检查组名是否匹配
                    group_match = needle in group.lower()
                    # 筛选匹配的节点
                    show_nodes = nodes if group_match else [n for n in nodes if needle in n.lower()]
                    if not show_nodes:
                        continue
                else:
                    show_nodes = nodes
                
                # 创建策略组节点
                label = f"{group}  （当前: {now}）"
                group_item = QTreeWidgetItem([label, "group", group])
                self._tree.addTopLevelItem(group_item)
                
                # 添加子节点
                for node in show_nodes:
                    node_item = QTreeWidgetItem([node, "node", group])
                    group_item.addChild(node_item)
                
                # 默认展开
                group_item.setExpanded(True)
        
        def _on_delay_test(self) -> None:
            """测试选中节点的延迟"""
            if self._request_inflight:
                self.log_warning("上一次请求还在进行中，请稍候…")
                return
            
            selected = self._tree.selectedItems()
            if not selected:
                self.log_warning("请先在列表中选中一个节点")
                return
            
            item = selected[0]
            item_type = item.text(1)
            
            if item_type != "node":
                self.log_warning("测延迟需要选中具体节点（子项），不是策略组")
                return
            
            node = item.text(0)
            url = self._delay_url_entry.text().strip()
            
            if not url:
                self.log_warning("请填写延迟测试 URL")
                return
            
            try:
                api, sec = self._read_endpoints()
            except ValueError as e:
                self.log_error(str(e))
                return
            
            self.log_info(f"正在测试节点「{node}」延迟…")
            self._set_busy(True)
            
            def job() -> None:
                try:
                    path = proxy_delay_path(node, url, 5000)
                    data = clash_get(api, path, secret=sec, timeout=25.0)
                    delay_val = None
                    if isinstance(data, dict):
                        delay_val = data.get("delay")
                    
                    if delay_val is not None:
                        msg = f"节点「{node}」延迟: {delay_val} ms"
                    else:
                        msg = f"节点「{node}」测试结果: {data!r}"
                    
                    self._result_queue.put(("status", msg))
                except Exception as e:
                    self._result_queue.put(("err", e))
            
            threading.Thread(target=job, daemon=True).start()
        
        def _on_close_all_connections(self) -> None:
            """关闭全部连接"""
            if self._request_inflight:
                self.log_warning("上一次请求还在进行中，请稍候…")
                return
            
            try:
                api, sec = self._read_endpoints()
            except ValueError as e:
                self.log_error(str(e))
                return
            
            self.log_info("正在关闭全部连接…")
            self._set_busy(True)
            
            def job() -> None:
                try:
                    clash_delete(api, "/connections", secret=sec)
                    snap = self._fetch_light_snapshot(api, sec)
                    self._result_queue.put(("ok", snap, "已关闭全部连接"))
                except Exception as e:
                    self._result_queue.put(("err", e))
            
            threading.Thread(target=job, daemon=True).start()
        
        def _on_open_dashboard(self) -> None:
            """打开浏览器控制台"""
            try:
                api, sec = self._read_endpoints()
            except ValueError as e:
                self.log_error(str(e))
                return
            
            # 显示选择对话框
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("选择控制台类型")
            msg_box.setText("请选择要打开的控制台类型：")
            
            yacd_btn = msg_box.addButton("Yacd (在线)", QMessageBox.ButtonRole.ActionRole)
            local_btn = msg_box.addButton("本地 UI", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = msg_box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.exec()
            
            clicked = msg_box.clickedButton()
            
            if clicked == yacd_btn:
                # 打开 Yacd 在线面板
                from linktunnel.dashboard_open import yacd_meta_browser_url, open_in_browser
                url = yacd_meta_browser_url(api, sec or "")
                self.log_info(f"正在打开 Yacd 控制台: {url}")
                open_in_browser(url)
            elif clicked == local_btn:
                # 打开本地 UI
                from linktunnel.dashboard_open import local_embedded_ui_url, open_in_browser
                url = local_embedded_ui_url(api)
                self.log_info(f"正在打开本地 UI: {url}")
                open_in_browser(url)
            else:
                # 取消
                return
        
        def _on_apply_selected_node(self) -> None:
            """应用选中的节点"""
            selected = self._tree.selectedItems()
            if not selected:
                self.log_warning("请先选中一个节点（子项）")
                return
            
            item = selected[0]
            item_type = item.text(1)
            
            if item_type != "node":
                self.log_warning("请选中子节点后再应用（策略组行不能应用）")
                return
            
            group = item.text(2)
            node = item.text(0)
            self._enqueue_switch_proxy(group, node)
        
        def _on_tree_double_click(self, item: QTreeWidgetItem, column: int) -> None:
            """树形控件双击事件"""
            item_type = item.text(1)
            
            if item_type != "node":
                return
            
            group = item.text(2)
            node = item.text(0)
            self._enqueue_switch_proxy(group, node)
        
        def _enqueue_switch_proxy(self, group: str, node: str) -> None:
            """切换代理节点"""
            if self._request_inflight:
                self.log_warning("上一次请求还在进行中，请稍候…")
                return
            
            try:
                api, sec = self._read_endpoints()
            except ValueError as e:
                self.log_error(str(e))
                return
            
            self.log_info(f"正在切换 {group} → {node}…")
            self._set_busy(True)
            
            def job() -> None:
                try:
                    path = f"/proxies/{proxy_path_segment(group)}"
                    clash_put(api, path, {"name": node}, secret=sec)
                    snap = self._fetch_snapshot(api, sec)
                    self._result_queue.put(("ok", snap, f"已切换 {group} -> {node}"))
                except Exception as e:
                    self._result_queue.put(("err", e))
            
            threading.Thread(target=job, daemon=True).start()
        
        def _format_version_line(self, ver: Any) -> str:
            """格式化版本信息"""
            if isinstance(ver, dict):
                meta = ver.get("Meta") or ver.get("meta")
                if isinstance(meta, dict) and meta.get("version"):
                    return f"Mihomo {meta.get('version', '')}"
                if ver.get("version"):
                    return f"Clash {ver.get('version')}"
            return str(ver) if ver is not None else "—"
        
        def get_module_name(self) -> str:
            return "proxy"
        
        def get_display_name(self) -> str:
            return "代理管理"
        
        def get_icon(self) -> QIcon:
            return QIcon()
        
        def stop(self) -> None:
            """停止模块"""
            super().stop()
            if self._auto_timer:
                self._auto_timer.stop()
                self._auto_timer = None
            if self._poll_timer:
                self._poll_timer.stop()
            self._save_current_config()

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk
    
    class ProxyModule(BaseModule):  # type: ignore
        """代理管理模块（tkinter 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent=None
        ):
            super().__init__(config_manager, log_manager, parent)
            self.log_info("代理管理模块（tkinter 版本）- 功能有限")
            
            label = ttk.Label(self, text="代理管理模块（tkinter 版本）")
            label.pack(pady=20)
        
        def get_module_name(self) -> str:
            return "proxy"
        
        def get_display_name(self) -> str:
            return "代理管理"
