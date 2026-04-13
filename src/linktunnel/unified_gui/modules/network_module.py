"""网络中继模块"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

from linktunnel.unified_gui.core.base_module import BaseModule

try:
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QCheckBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    
    class NetworkModule(BaseModule):
        """网络中继模块（PyQt6 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: QWidget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            self._setup_ui()
        
        def get_module_name(self) -> str:
            return "network"
        
        def get_display_name(self) -> str:
            return "网络中继"
        
        def get_icon(self) -> QIcon:
            return QIcon()
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            
            # 标签页
            tabs = QTabWidget()
            
            # TCP 中继
            tcp_tab = QWidget()
            tcp_layout = QVBoxLayout(tcp_tab)
            
            # 监听地址
            listen_layout = QHBoxLayout()
            listen_layout.addWidget(QLabel("监听地址:"))
            self.tcp_listen_input = QLineEdit("127.0.0.1")
            listen_layout.addWidget(self.tcp_listen_input)
            listen_layout.addWidget(QLabel("端口:"))
            self.tcp_listen_port = QLineEdit("9000")
            listen_layout.addWidget(self.tcp_listen_port)
            tcp_layout.addLayout(listen_layout)
            
            # 目标地址
            target_layout = QHBoxLayout()
            target_layout.addWidget(QLabel("目标地址:"))
            self.tcp_target_input = QLineEdit("example.com")
            target_layout.addWidget(self.tcp_target_input)
            target_layout.addWidget(QLabel("端口:"))
            self.tcp_target_port = QLineEdit("80")
            target_layout.addWidget(self.tcp_target_port)
            tcp_layout.addLayout(target_layout)
            
            # 选项
            options_layout = QHBoxLayout()
            self.tcp_hex_check = QCheckBox("十六进制日志")
            options_layout.addWidget(self.tcp_hex_check)
            self.tcp_ipv6_check = QCheckBox("IPv6")
            options_layout.addWidget(self.tcp_ipv6_check)
            options_layout.addStretch()
            tcp_layout.addLayout(options_layout)
            
            # 控制按钮
            btn_layout = QHBoxLayout()
            self.tcp_start_btn = QPushButton("启动中继")
            self.tcp_start_btn.clicked.connect(self._on_start_tcp)
            btn_layout.addWidget(self.tcp_start_btn)
            
            self.tcp_stop_btn = QPushButton("停止")
            self.tcp_stop_btn.clicked.connect(self._on_stop_tcp)
            self.tcp_stop_btn.setEnabled(False)
            btn_layout.addWidget(self.tcp_stop_btn)
            btn_layout.addStretch()
            tcp_layout.addLayout(btn_layout)
            
            # 状态和日志
            self.tcp_status = QLabel("状态: 未运行")
            tcp_layout.addWidget(self.tcp_status)
            
            tcp_layout.addWidget(QLabel("数据流日志:"))
            self.tcp_log = QTextEdit()
            self.tcp_log.setReadOnly(True)
            tcp_layout.addWidget(self.tcp_log)
            
            tabs.addTab(tcp_tab, "TCP 中继")
            
            # UDP 中继（类似结构）
            udp_tab = QWidget()
            udp_layout = QVBoxLayout(udp_tab)
            udp_layout.addWidget(QLabel("UDP 中继功能（待完善）"))
            tabs.addTab(udp_tab, "UDP 中继")
            
            layout.addWidget(tabs)
        
        def _on_start_tcp(self) -> None:
            """启动 TCP 中继"""
            listen_addr = f"{self.tcp_listen_input.text()}:{self.tcp_listen_port.text()}"
            target_addr = f"{self.tcp_target_input.text()}:{self.tcp_target_port.text()}"
            
            self.log_info(f"启动 TCP 中继: {listen_addr} -> {target_addr}")
            
            # TODO: 调用 tcp_udp.py 实现
            
            self._is_running = True
            self.tcp_start_btn.setEnabled(False)
            self.tcp_stop_btn.setEnabled(True)
            self.tcp_status.setText("状态: 运行中")
            self.tcp_log.append(f"[INFO] TCP 中继已启动: {listen_addr} -> {target_addr}")
        
        def _on_stop_tcp(self) -> None:
            """停止 TCP 中继"""
            self.log_info("停止 TCP 中继")
            
            self._is_running = False
            self.tcp_start_btn.setEnabled(True)
            self.tcp_stop_btn.setEnabled(False)
            self.tcp_status.setText("状态: 未运行")
            self.tcp_log.append("[INFO] TCP 中继已停止")

except ImportError:
    import tkinter as tk
    from tkinter import ttk
    
    class NetworkModule(BaseModule):  # type: ignore
        """网络中继模块（tkinter 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: tk.Widget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            self._setup_ui()
        
        def get_module_name(self) -> str:
            return "network"
        
        def get_display_name(self) -> str:
            return "网络中继"
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            ttk.Label(self, text="网络中继功能（待实现）").pack(pady=20)
