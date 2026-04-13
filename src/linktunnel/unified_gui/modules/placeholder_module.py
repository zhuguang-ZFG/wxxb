"""占位符模块 - 用于测试框架"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

from linktunnel.unified_gui.core.base_module import BaseModule

try:
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout
    
    class PlaceholderModule(BaseModule):
        """占位符模块（PyQt6 版本）"""
        
        def __init__(
            self,
            name: str,
            display_name: str,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent=None
        ):
            self._name = name
            self._display_name = display_name
            super().__init__(config_manager, log_manager, parent)
            self._setup_ui()
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            
            label = QLabel(f"这是 {self._display_name} 模块")
            layout.addWidget(label)
            
            btn = QPushButton("测试日志")
            btn.clicked.connect(self._on_test_log)
            layout.addWidget(btn)
            
            layout.addStretch()
        
        def _on_test_log(self) -> None:
            """测试日志功能"""
            self.log_info(f"{self._display_name} 模块测试日志")
        
        def get_module_name(self) -> str:
            return self._name
        
        def get_display_name(self) -> str:
            return self._display_name
        
        def get_icon(self) -> QIcon:
            return QIcon()

except ImportError:
    import tkinter as tk
    from tkinter import ttk
    
    class PlaceholderModule(BaseModule):  # type: ignore
        """占位符模块（tkinter 版本）"""
        
        def __init__(
            self,
            name: str,
            display_name: str,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent=None
        ):
            self._name = name
            self._display_name = display_name
            super().__init__(config_manager, log_manager, parent)
            self._setup_ui()
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            label = ttk.Label(self, text=f"这是 {self._display_name} 模块")
            label.pack(pady=20)
            
            btn = ttk.Button(self, text="测试日志", command=self._on_test_log)
            btn.pack()
        
        def _on_test_log(self) -> None:
            """测试日志功能"""
            self.log_info(f"{self._display_name} 模块测试日志")
        
        def get_module_name(self) -> str:
            return self._name
        
        def get_display_name(self) -> str:
            return self._display_name
