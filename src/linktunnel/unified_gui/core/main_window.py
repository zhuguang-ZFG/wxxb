"""主窗口"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QMainWindow,
        QStatusBar,
        QVBoxLayout,
        QWidget,
    )
    
    from linktunnel.unified_gui.core.log_manager import LogManager
    from linktunnel.unified_gui.core.module_container import ModuleContainer
    from linktunnel.unified_gui.ui.log_viewer import LogViewer
    from linktunnel.unified_gui.ui.navigation_system import NavigationSystem
    
    class MainWindow(QMainWindow):
        """主窗口（PyQt6 版本）"""
        
        def __init__(self, config_manager: ConfigManager):
            super().__init__()
            self.config_manager = config_manager
            self.log_manager = LogManager(log_level=config_manager.get("log_level", "INFO"))
            
            self._setup_ui()
            self._load_window_state()
            self._register_modules()
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            self.setWindowTitle("linktunnel Unified GUI")
            
            # 中央部件
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            
            # 上半部分：导航 + 模块容器
            top_layout = QHBoxLayout()
            
            # 导航系统
            self.navigation = NavigationSystem()
            self.navigation.setMaximumWidth(200)
            self.navigation.module_changed.connect(self._on_module_changed)
            top_layout.addWidget(self.navigation)
            
            # 模块容器
            self.module_container = ModuleContainer(
                self.config_manager,
                self.log_manager
            )
            top_layout.addWidget(self.module_container, stretch=1)
            
            main_layout.addLayout(top_layout, stretch=2)
            
            # 下半部分：日志查看器
            self.log_viewer = LogViewer()
            self.log_viewer.setMaximumHeight(200)
            main_layout.addWidget(self.log_viewer, stretch=1)
            
            # 连接日志管理器到日志查看器
            self.log_manager.add_callback(self.log_viewer.append_log)
            
            # 状态栏
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("就绪")
        
        def _register_modules(self) -> None:
            """注册所有功能模块"""
            from PyQt6.QtGui import QIcon
            
            # 导入真实模块
            from linktunnel.unified_gui.modules.serial_module import SerialModule
            from linktunnel.unified_gui.modules.network_module import NetworkModule
            from linktunnel.unified_gui.modules.proxy_module import ProxyModule
            from linktunnel.unified_gui.modules.grbl_module import GrblModule
            from linktunnel.unified_gui.modules.ble_module import BLEModule
            from linktunnel.unified_gui.modules.placeholder_module import PlaceholderModule
            
            # 注册串口模块
            serial_module = SerialModule(self.config_manager, self.log_manager)
            self.module_container.register_module(serial_module)
            self.navigation.add_module("serial", "串口工具", QIcon())
            
            # 注册网络模块
            network_module = NetworkModule(self.config_manager, self.log_manager)
            self.module_container.register_module(network_module)
            self.navigation.add_module("network", "网络中继", QIcon())
            
            # 注册代理模块
            proxy_module = ProxyModule(self.config_manager, self.log_manager)
            self.module_container.register_module(proxy_module)
            self.navigation.add_module("proxy", "代理管理", QIcon())
            
            # 注册 Grbl 模块
            grbl_module = GrblModule(self.config_manager, self.log_manager)
            self.module_container.register_module(grbl_module)
            self.navigation.add_module("grbl", "Grbl CNC", QIcon())
            
            # 注册 BLE 模块
            ble_module = BLEModule(self.config_manager, self.log_manager)
            self.module_container.register_module(ble_module)
            self.navigation.add_module("ble", "BLE 蓝牙扫描", QIcon())
            
            # 显示第一个模块
            last_module = self.config_manager.get("last_active_module", "serial")
            self.navigation.set_active_module(last_module)
        
        def _on_module_changed(self, module_name: str) -> None:
            """模块切换"""
            self.module_container.show_module(module_name)
            self.config_manager.set("last_active_module", module_name)
            self.status_bar.showMessage(f"切换到: {module_name}")
        
        def _load_window_state(self) -> None:
            """加载窗口状态"""
            width = self.config_manager.get("window.width", 1280)
            height = self.config_manager.get("window.height", 800)
            self.resize(width, height)
            
            if self.config_manager.get("window.maximized", False):
                self.showMaximized()
        
        def closeEvent(self, event) -> None:
            """窗口关闭事件"""
            # 保存窗口状态
            self.config_manager.set("window.width", self.width())
            self.config_manager.set("window.height", self.height())
            self.config_manager.set("window.maximized", self.isMaximized())
            
            # 停止所有模块
            self.module_container.stop_all_modules()
            
            event.accept()

except ImportError:
    import tkinter as tk
    from tkinter import ttk
    
    from linktunnel.unified_gui.core.log_manager import LogManager
    from linktunnel.unified_gui.core.module_container import ModuleContainer
    from linktunnel.unified_gui.ui.log_viewer import LogViewer
    from linktunnel.unified_gui.ui.navigation_system import NavigationSystem
    
    class MainWindow(tk.Tk):  # type: ignore
        """主窗口（tkinter 版本）"""
        
        def __init__(self, config_manager: ConfigManager):
            super().__init__()
            self.config_manager = config_manager
            self.log_manager = LogManager(log_level=config_manager.get("log_level", "INFO"))
            
            self.title("linktunnel Unified GUI")
            self._setup_ui()
            self._load_window_state()
            self._register_modules()
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            # 主布局
            main_frame = ttk.Frame(self)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 上半部分
            top_frame = ttk.Frame(main_frame)
            top_frame.pack(fill=tk.BOTH, expand=True)
            
            # 导航系统
            self.navigation = NavigationSystem(top_frame)
            self.navigation.pack(side=tk.LEFT, fill=tk.Y)
            self.navigation.add_callback(self._on_module_changed)
            
            # 模块容器
            self.module_container = ModuleContainer(
                self.config_manager,
                self.log_manager,
                top_frame
            )
            self.module_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # 日志查看器
            self.log_viewer = LogViewer(main_frame)
            self.log_viewer.pack(fill=tk.BOTH)
            
            # 连接日志管理器
            self.log_manager.add_callback(self.log_viewer.append_log)
        
        def _register_modules(self) -> None:
            """注册所有功能模块"""
            from linktunnel.unified_gui.modules.serial_module import SerialModule
            from linktunnel.unified_gui.modules.network_module import NetworkModule
            from linktunnel.unified_gui.modules.proxy_module import ProxyModule
            from linktunnel.unified_gui.modules.grbl_module import GrblModule
            from linktunnel.unified_gui.modules.placeholder_module import PlaceholderModule
            
            # 注册串口模块
            serial_module = SerialModule(
                self.config_manager,
                self.log_manager,
                self.module_container
            )
            self.module_container.register_module(serial_module)
            self.navigation.add_module("serial", "串口工具")
            
            # 注册网络模块
            network_module = NetworkModule(
                self.config_manager,
                self.log_manager,
                self.module_container
            )
            self.module_container.register_module(network_module)
            self.navigation.add_module("network", "网络中继")
            
            # 注册代理模块
            proxy_module = ProxyModule(
                self.config_manager,
                self.log_manager,
                self.module_container
            )
            self.module_container.register_module(proxy_module)
            self.navigation.add_module("proxy", "代理管理")
            
            # 注册 Grbl 模块
            grbl_module = GrblModule(
                self.config_manager,
                self.log_manager,
                self.module_container
            )
            self.module_container.register_module(grbl_module)
            self.navigation.add_module("grbl", "Grbl CNC")
            
            last_module = self.config_manager.get("last_active_module", "serial")
            self.navigation.set_active_module(last_module)
        
        def _on_module_changed(self, module_name: str) -> None:
            """模块切换"""
            self.module_container.show_module(module_name)
            self.config_manager.set("last_active_module", module_name)
        
        def _load_window_state(self) -> None:
            """加载窗口状态"""
            width = self.config_manager.get("window.width", 1280)
            height = self.config_manager.get("window.height", 800)
            self.geometry(f"{width}x{height}")
