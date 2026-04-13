"""串口工具模块"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

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
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    
    class SerialModule(BaseModule):
        """串口工具模块（PyQt6 版本）"""
        
        # 信号
        ports_refreshed = pyqtSignal(list)  # 串口列表刷新信号
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: QWidget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            self._bridge_thread: threading.Thread | None = None
            self._term_thread: threading.Thread | None = None
            self._occupied_ports: set[str] = set()
            self._setup_ui()
            
            # 自动刷新串口列表
            QTimer.singleShot(100, self.refresh_serial_list)
        
        def get_module_name(self) -> str:
            return "serial"
        
        def get_display_name(self) -> str:
            return "串口工具"
        
        def get_icon(self) -> QIcon:
            return QIcon()  # TODO: 添加图标
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            
            # 串口列表区域
            ports_group = QGroupBox("串口列表")
            ports_layout = QVBoxLayout(ports_group)
            
            # 刷新按钮
            refresh_btn = QPushButton("刷新串口列表")
            refresh_btn.clicked.connect(self.refresh_serial_list)
            ports_layout.addWidget(refresh_btn)
            
            # 串口列表显示
            self.ports_text = QTextEdit()
            self.ports_text.setReadOnly(True)
            self.ports_text.setMaximumHeight(100)
            ports_layout.addWidget(self.ports_text)
            
            layout.addWidget(ports_group)
            
            # 标签页
            self.tabs = QTabWidget()
            
            # 串口桥接标签页
            self.bridge_tab = self._create_bridge_tab()
            self.tabs.addTab(self.bridge_tab, "串口桥接")
            
            # 调试终端标签页
            self.terminal_tab = self._create_terminal_tab()
            self.tabs.addTab(self.terminal_tab, "调试终端")
            
            layout.addWidget(self.tabs)
        
        def _create_bridge_tab(self) -> QWidget:
            """创建串口桥接标签页"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # 配置区域
            config_layout = QHBoxLayout()
            
            # 端口 A
            config_layout.addWidget(QLabel("端口 A:"))
            self.port_a_combo = QComboBox()
            self.port_a_combo.setEditable(True)
            config_layout.addWidget(self.port_a_combo)
            
            # 端口 B
            config_layout.addWidget(QLabel("端口 B:"))
            self.port_b_combo = QComboBox()
            self.port_b_combo.setEditable(True)
            config_layout.addWidget(self.port_b_combo)
            
            # 波特率
            config_layout.addWidget(QLabel("波特率:"))
            self.baud_combo = QComboBox()
            self.baud_combo.addItems(["9600", "115200", "230400", "460800", "921600"])
            self.baud_combo.setCurrentText("115200")
            config_layout.addWidget(self.baud_combo)
            
            layout.addLayout(config_layout)
            
            # 选项
            options_layout = QHBoxLayout()
            self.hex_log_check = QCheckBox("十六进制日志")
            options_layout.addWidget(self.hex_log_check)
            options_layout.addStretch()
            layout.addLayout(options_layout)
            
            # 控制按钮
            btn_layout = QHBoxLayout()
            self.bridge_start_btn = QPushButton("启动桥接")
            self.bridge_start_btn.clicked.connect(self._on_start_bridge)
            btn_layout.addWidget(self.bridge_start_btn)
            
            self.bridge_stop_btn = QPushButton("停止")
            self.bridge_stop_btn.clicked.connect(self._on_stop_bridge)
            self.bridge_stop_btn.setEnabled(False)
            btn_layout.addWidget(self.bridge_stop_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            # 日志显示
            layout.addWidget(QLabel("桥接日志:"))
            self.bridge_log = QTextEdit()
            self.bridge_log.setReadOnly(True)
            layout.addWidget(self.bridge_log)
            
            # 统计信息
            self.bridge_stats = QLabel("RX: 0 bytes  TX: 0 bytes")
            layout.addWidget(self.bridge_stats)
            
            return widget
        
        def _create_terminal_tab(self) -> QWidget:
            """创建调试终端标签页"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # 配置区域
            config_layout = QHBoxLayout()
            
            # 端口
            config_layout.addWidget(QLabel("端口:"))
            self.term_port_combo = QComboBox()
            self.term_port_combo.setEditable(True)
            config_layout.addWidget(self.term_port_combo)
            
            # 波特率
            config_layout.addWidget(QLabel("波特率:"))
            self.term_baud_combo = QComboBox()
            self.term_baud_combo.addItems(["9600", "115200", "230400", "460800", "921600"])
            self.term_baud_combo.setCurrentText("115200")
            config_layout.addWidget(self.term_baud_combo)
            
            # 编码
            config_layout.addWidget(QLabel("编码:"))
            self.encoding_combo = QComboBox()
            self.encoding_combo.addItems(["UTF-8", "ASCII", "GBK"])
            config_layout.addWidget(self.encoding_combo)
            
            layout.addLayout(config_layout)
            
            # 选项
            options_layout = QHBoxLayout()
            self.hex_mode_check = QCheckBox("十六进制模式")
            options_layout.addWidget(self.hex_mode_check)
            
            self.timestamp_check = QCheckBox("时间戳")
            options_layout.addWidget(self.timestamp_check)
            
            options_layout.addStretch()
            layout.addLayout(options_layout)
            
            # 控制按钮
            btn_layout = QHBoxLayout()
            self.term_start_btn = QPushButton("打开串口")
            self.term_start_btn.clicked.connect(self._on_start_terminal)
            btn_layout.addWidget(self.term_start_btn)
            
            self.term_stop_btn = QPushButton("关闭")
            self.term_stop_btn.clicked.connect(self._on_stop_terminal)
            self.term_stop_btn.setEnabled(False)
            btn_layout.addWidget(self.term_stop_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            # 接收区域
            layout.addWidget(QLabel("接收:"))
            self.term_rx = QTextEdit()
            self.term_rx.setReadOnly(True)
            layout.addWidget(self.term_rx)
            
            # 发送区域
            send_layout = QHBoxLayout()
            send_layout.addWidget(QLabel("发送:"))
            self.term_tx = QLineEdit()
            self.term_tx.returnPressed.connect(self._on_send_data)
            send_layout.addWidget(self.term_tx)
            
            send_btn = QPushButton("发送")
            send_btn.clicked.connect(self._on_send_data)
            send_layout.addWidget(send_btn)
            
            layout.addLayout(send_layout)
            
            # 统计信息
            self.term_stats = QLabel("RX: 0 bytes  TX: 0 bytes")
            layout.addWidget(self.term_stats)
            
            return widget
        
        def refresh_serial_list(self) -> None:
            """刷新串口列表"""
            try:
                from linktunnel.serial_util import list_serial_ports, format_ports_table
                
                ports = list_serial_ports()
                self.ports_text.setText(format_ports_table(ports))
                
                # 更新下拉框
                port_names = [p.device for p in ports]
                self.port_a_combo.clear()
                self.port_a_combo.addItems(port_names)
                self.port_b_combo.clear()
                self.port_b_combo.addItems(port_names)
                self.term_port_combo.clear()
                self.term_port_combo.addItems(port_names)
                
                self.log_info(f"发现 {len(ports)} 个串口")
                self.ports_refreshed.emit(ports)
                
            except Exception as e:
                self.log_error(f"刷新串口列表失败: {e}")
        
        def _on_start_bridge(self) -> None:
            """启动串口桥接"""
            port_a = self.port_a_combo.currentText()
            port_b = self.port_b_combo.currentText()
            
            if not port_a or not port_b:
                self.log_error("请选择端口 A 和端口 B")
                return
            
            if port_a == port_b:
                self.log_error("端口 A 和端口 B 不能相同")
                return
            
            try:
                baudrate = int(self.baud_combo.currentText())
                hex_log = self.hex_log_check.isChecked()
                
                self.log_info(f"启动串口桥接: {port_a} <-> {port_b} @ {baudrate}")
                
                # TODO: 实际启动桥接线程
                # 这里需要调用 bridge.py 的功能
                
                self._occupied_ports.add(port_a)
                self._occupied_ports.add(port_b)
                self._is_running = True
                
                self.bridge_start_btn.setEnabled(False)
                self.bridge_stop_btn.setEnabled(True)
                
                self.bridge_log.append(f"[INFO] 桥接已启动: {port_a} <-> {port_b}")
                
            except Exception as e:
                self.log_error(f"启动桥接失败: {e}")
        
        def _on_stop_bridge(self) -> None:
            """停止串口桥接"""
            self.log_info("停止串口桥接")
            
            # TODO: 停止桥接线程
            
            self._occupied_ports.clear()
            self._is_running = False
            
            self.bridge_start_btn.setEnabled(True)
            self.bridge_stop_btn.setEnabled(False)
            
            self.bridge_log.append("[INFO] 桥接已停止")
        
        def _on_start_terminal(self) -> None:
            """打开串口终端"""
            port = self.term_port_combo.currentText()
            
            if not port:
                self.log_error("请选择串口")
                return
            
            try:
                baudrate = int(self.term_baud_combo.currentText())
                encoding = self.encoding_combo.currentText().lower()
                if encoding == "utf-8":
                    encoding = "utf8"
                
                self.log_info(f"打开串口终端: {port} @ {baudrate}")
                
                # TODO: 实际启动终端线程
                # 这里需要调用 serial_term.py 的功能
                
                self._occupied_ports.add(port)
                self._is_running = True
                
                self.term_start_btn.setEnabled(False)
                self.term_stop_btn.setEnabled(True)
                
                self.term_rx.append(f"[INFO] 串口已打开: {port} @ {baudrate}")
                
            except Exception as e:
                self.log_error(f"打开串口失败: {e}")
        
        def _on_stop_terminal(self) -> None:
            """关闭串口终端"""
            self.log_info("关闭串口终端")
            
            # TODO: 停止终端线程
            
            port = self.term_port_combo.currentText()
            if port in self._occupied_ports:
                self._occupied_ports.remove(port)
            self._is_running = False
            
            self.term_start_btn.setEnabled(True)
            self.term_stop_btn.setEnabled(False)
            
            self.term_rx.append("[INFO] 串口已关闭")
        
        def _on_send_data(self) -> None:
            """发送数据"""
            data = self.term_tx.text()
            if not data:
                return
            
            # TODO: 实际发送数据到串口
            
            self.term_rx.append(f"[TX] {data}")
            self.term_tx.clear()
        
        def get_occupied_resources(self) -> list[str]:
            """返回当前占用的串口"""
            return list(self._occupied_ports)
        
        def stop(self) -> None:
            """停止模块"""
            if self._is_running:
                self._on_stop_bridge()
                self._on_stop_terminal()
            super().stop()

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk
    
    class SerialModule(BaseModule):  # type: ignore
        """串口工具模块（tkinter 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: tk.Widget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            self._occupied_ports: set[str] = set()
            self._setup_ui()
            self.after(100, self.refresh_serial_list)
        
        def get_module_name(self) -> str:
            return "serial"
        
        def get_display_name(self) -> str:
            return "串口工具"
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            # 串口列表
            list_frame = ttk.LabelFrame(self, text="串口列表")
            list_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Button(list_frame, text="刷新", command=self.refresh_serial_list).pack(side=tk.LEFT, padx=5, pady=5)
            
            self.ports_text = tk.Text(list_frame, height=4)
            self.ports_text.pack(fill=tk.X, padx=5, pady=5)
            
            # 标签页
            self.notebook = ttk.Notebook(self)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 桥接标签页
            bridge_frame = ttk.Frame(self.notebook)
            self.notebook.add(bridge_frame, text="串口桥接")
            ttk.Label(bridge_frame, text="串口桥接功能（待实现）").pack(pady=20)
            
            # 终端标签页
            term_frame = ttk.Frame(self.notebook)
            self.notebook.add(term_frame, text="调试终端")
            ttk.Label(term_frame, text="调试终端功能（待实现）").pack(pady=20)
        
        def refresh_serial_list(self) -> None:
            """刷新串口列表"""
            try:
                from linktunnel.serial_util import list_serial_ports, format_ports_table
                
                ports = list_serial_ports()
                self.ports_text.delete(1.0, tk.END)
                self.ports_text.insert(1.0, format_ports_table(ports))
                
                self.log_info(f"发现 {len(ports)} 个串口")
                
            except Exception as e:
                self.log_error(f"刷新串口列表失败: {e}")
