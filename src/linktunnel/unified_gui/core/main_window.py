"""主窗口"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QAction, QKeySequence
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QMainWindow,
        QMenu,
        QStatusBar,
        QVBoxLayout,
        QWidget,
    )
    
    from linktunnel.unified_gui.core.log_manager import LogManager
    from linktunnel.unified_gui.core.module_container import ModuleContainer
    from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme
    from linktunnel.unified_gui.core.feedback_manager import FeedbackManager
    from linktunnel.unified_gui.core.help_manager import HelpManager
    from linktunnel.unified_gui.ui.log_viewer import LogViewer
    from linktunnel.unified_gui.ui.navigation_system import NavigationSystem
    from linktunnel.unified_gui.utils.performance import MemoryOptimizer, CPUOptimizer
    
    class MainWindow(QMainWindow):
        """主窗口（PyQt6 版本）"""
        
        def __init__(self, config_manager: ConfigManager):
            super().__init__()
            self.config_manager = config_manager
            self.log_manager = LogManager(log_level=config_manager.get("log_level", "INFO"))
            self.theme_manager = ThemeManager(config_manager)
            self.feedback_manager = FeedbackManager(self)
            self.help_manager = HelpManager(self)
            
            # 性能监控定时器
            self._performance_timer = None
            self._setup_performance_monitoring()
            
            # 设置状态栏回调
            self._setup_ui()
            self._setup_menu()
            self.feedback_manager.set_status_callback(self._show_status_message)
            self._load_window_state()
            self._register_modules()
            
            # 应用主题
            self.theme_manager.apply_theme()
            
            # 显示欢迎消息
            self.feedback_manager.show_status("欢迎使用 linktunnel Unified GUI", 5000)
        
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
        
        def _setup_menu(self) -> None:
            """设置菜单栏"""
            menubar = self.menuBar()
            
            # 视图菜单
            view_menu = menubar.addMenu("视图(&V)")
            
            # 主题子菜单
            theme_menu = QMenu("主题", self)
            view_menu.addMenu(theme_menu)
            
            # 浅色主题
            light_action = QAction("浅色", self)
            light_action.triggered.connect(lambda: self._on_theme_changed(Theme.LIGHT))
            theme_menu.addAction(light_action)
            
            # 深色主题
            dark_action = QAction("深色", self)
            dark_action.triggered.connect(lambda: self._on_theme_changed(Theme.DARK))
            theme_menu.addAction(dark_action)
            
            # 系统主题
            system_action = QAction("跟随系统", self)
            system_action.triggered.connect(lambda: self._on_theme_changed(Theme.SYSTEM))
            theme_menu.addAction(system_action)
            
            theme_menu.addSeparator()
            
            # 切换主题（快捷键）
            toggle_action = QAction("切换主题", self)
            toggle_action.setShortcut(QKeySequence("Ctrl+T"))
            toggle_action.triggered.connect(self._on_toggle_theme)
            theme_menu.addAction(toggle_action)
            
            # 帮助菜单
            help_menu = menubar.addMenu("帮助(&H)")
            
            # 用户手册
            manual_action = QAction("用户手册", self)
            manual_action.setShortcut(QKeySequence("F1"))
            manual_action.triggered.connect(self._on_show_manual)
            help_menu.addAction(manual_action)
            
            # 快捷键列表
            shortcuts_action = QAction("快捷键列表", self)
            shortcuts_action.triggered.connect(self._on_show_shortcuts)
            help_menu.addAction(shortcuts_action)
            
            help_menu.addSeparator()
            
            # 在线文档
            online_docs_action = QAction("在线文档", self)
            online_docs_action.triggered.connect(self._on_open_online_docs)
            help_menu.addAction(online_docs_action)
            
            # GitHub 仓库
            github_action = QAction("GitHub 仓库", self)
            github_action.triggered.connect(self._on_open_github)
            help_menu.addAction(github_action)
            
            help_menu.addSeparator()
            
            # 关于
            about_action = QAction("关于", self)
            about_action.triggered.connect(self._on_about)
            help_menu.addAction(about_action)
        
        def _on_theme_changed(self, theme: Theme) -> None:
            """主题改变事件"""
            self.theme_manager.set_theme(theme)
            self.status_bar.showMessage(f"已切换到{theme.value}主题", 3000)
        
        def _on_toggle_theme(self) -> None:
            """切换主题"""
            self.theme_manager.toggle_theme()
            current_theme = self.theme_manager.get_current_theme()
            self.status_bar.showMessage(f"已切换到{current_theme.value}主题", 3000)
        
        def _on_about(self) -> None:
            """关于对话框"""
            from PyQt6.QtWidgets import QMessageBox
            
            QMessageBox.about(
                self,
                "关于 linktunnel Unified GUI",
                "<h3>linktunnel Unified GUI</h3>"
                "<p>版本: 0.3.0</p>"
                "<p>统一图形界面 - 整合所有 linktunnel 功能</p>"
                "<p><b>功能模块:</b></p>"
                "<ul>"
                "<li>串口工具 - 串口桥接和调试终端</li>"
                "<li>网络中继 - TCP/UDP 透明中继</li>"
                "<li>代理管理 - Mihomo/Clash 代理控制</li>"
                "<li>Grbl CNC - CNC 设备控制</li>"
                "<li>BLE 扫描 - 蓝牙设备发现</li>"
                "<li>I2C 扫描 - I2C 总线扫描（Linux）</li>"
                "</ul>"
                "<p>© 2026 linktunnel Project</p>"
            )
        
        def _on_show_manual(self) -> None:
            """显示用户手册"""
            self.help_manager.show_user_manual()
        
        def _on_show_shortcuts(self) -> None:
            """显示快捷键列表"""
            self.help_manager.show_shortcuts()
        
        def _on_open_online_docs(self) -> None:
            """打开在线文档"""
            self.help_manager.open_online_docs()
            self.feedback_manager.show_status("已在浏览器中打开在线文档", 3000)
        
        def _on_open_github(self) -> None:
            """打开 GitHub 仓库"""
            self.help_manager.open_github_repo()
            self.feedback_manager.show_status("已在浏览器中打开 GitHub 仓库", 3000)
        
        def _register_modules(self) -> None:
            """注册所有功能模块"""
            from PyQt6.QtGui import QIcon
            
            # 导入真实模块
            from linktunnel.unified_gui.modules.serial_module import SerialModule
            from linktunnel.unified_gui.modules.network_module import NetworkModule
            from linktunnel.unified_gui.modules.proxy_module import ProxyModule
            from linktunnel.unified_gui.modules.grbl_module import GrblModule
            from linktunnel.unified_gui.modules.ble_module import BLEModule
            from linktunnel.unified_gui.modules.i2c_module import I2CModule
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
            
            # 注册 I2C 模块
            i2c_module = I2CModule(self.config_manager, self.log_manager)
            self.module_container.register_module(i2c_module)
            self.navigation.add_module("i2c", "I2C 扫描", QIcon())
            
            # 显示第一个模块
            last_module = self.config_manager.get("last_active_module", "serial")
            self.navigation.set_active_module(last_module)
        
        def _on_module_changed(self, module_name: str) -> None:
            """模块切换"""
            self.module_container.show_module(module_name)
            self.config_manager.set("last_active_module", module_name)
            self.status_bar.showMessage(f"切换到: {module_name}")
            
            # 模块切换后执行内存优化
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, MemoryOptimizer.force_gc)
        
        def _setup_performance_monitoring(self) -> None:
            """设置性能监控"""
            # 每 30 秒检查一次性能
            from PyQt6.QtCore import QTimer
            
            self._performance_timer = QTimer()
            self._performance_timer.timeout.connect(self._check_performance)
            self._performance_timer.start(30000)  # 30 秒
        
        def _check_performance(self) -> None:
            """检查性能指标"""
            # 检查 CPU 使用率
            cpu_usage = CPUOptimizer.get_cpu_usage()
            
            # 检查内存使用
            memory_info = MemoryOptimizer.get_memory_usage()
            
            # 如果 CPU 或内存使用过高，记录警告
            if cpu_usage > 50:
                self.log_manager.warning(
                    "Performance",
                    f"CPU 使用率较高: {cpu_usage:.1f}%"
                )
            
            if memory_info.get("rss_mb", 0) > 500:
                self.log_manager.warning(
                    "Performance",
                    f"内存使用较高: {memory_info['rss_mb']:.1f} MB"
                )
                # 尝试优化内存
                MemoryOptimizer.optimize_memory()
        
        def _show_status_message(self, message: str, timeout: int) -> None:
            """在状态栏显示消息
            
            Args:
                message: 消息内容
                timeout: 超时时间（毫秒）
            """
            self.status_bar.showMessage(message, timeout)
        
        def _load_window_state(self) -> None:
            """加载窗口状态"""
            width = self.config_manager.get("window.width", 1280)
            height = self.config_manager.get("window.height", 800)
            self.resize(width, height)
            
            if self.config_manager.get("window.maximized", False):
                self.showMaximized()
        
        def closeEvent(self, event) -> None:
            """窗口关闭事件"""
            # 停止性能监控
            if self._performance_timer:
                self._performance_timer.stop()
            
            # 保存窗口状态
            self.config_manager.set("window.width", self.width())
            self.config_manager.set("window.height", self.height())
            self.config_manager.set("window.maximized", self.isMaximized())
            
            # 停止所有模块
            self.module_container.stop_all_modules()
            
            # 最后的内存清理
            MemoryOptimizer.optimize_memory()
            
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
            from linktunnel.unified_gui.modules.ble_module import BLEModule
            from linktunnel.unified_gui.modules.i2c_module import I2CModule
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
            
            # 注册 BLE 模块
            ble_module = BLEModule(
                self.config_manager,
                self.log_manager,
                self.module_container
            )
            self.module_container.register_module(ble_module)
            self.navigation.add_module("ble", "BLE 蓝牙扫描")
            
            # 注册 I2C 模块
            i2c_module = I2CModule(
                self.config_manager,
                self.log_manager,
                self.module_container
            )
            self.module_container.register_module(i2c_module)
            self.navigation.add_module("i2c", "I2C 扫描")
            
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
