"""现代化主窗口 - 美观、智能、响应式"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager

try:
    from PyQt6.QtCore import Qt, QTimer, QSize
    from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QStatusBar, QSplitter, QFrame, QStackedWidget
    )
    
    from linktunnel.unified_gui.core.log_manager import LogManager
    from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme
    from linktunnel.unified_gui.core.feedback_manager import FeedbackManager
    from linktunnel.unified_gui.core.help_manager import HelpManager
    from linktunnel.unified_gui.ui.modern_navigation import ModernNavigationSystem
    from linktunnel.unified_gui.ui.log_viewer import LogViewer
    from linktunnel.unified_gui.core.module_container import ModuleContainer
    from linktunnel.unified_gui.utils.performance import MemoryOptimizer, CPUOptimizer
    
    class ModernMainWindow(QMainWindow):
        """现代化主窗口"""
        
        def __init__(self, config_manager: ConfigManager):
            super().__init__()
            self.config_manager = config_manager
            self.log_manager = LogManager(log_level=config_manager.get("log_level", "INFO"))
            self.theme_manager = ThemeManager(config_manager)
            self.feedback_manager = FeedbackManager(self)
            self.help_manager = HelpManager(self)
            
            # 性能监控
            self._performance_timer = None
            self._setup_performance_monitoring()
            
            # 设置窗口
            self.setWindowTitle("linktunnel Unified GUI")
            self.setWindowIcon(QIcon())
            
            # 设置 UI
            self._setup_ui()
            self._setup_menu()
            self._load_window_state()
            self._register_modules()
            
            # 应用主题
            self.theme_manager.apply_theme()
            self._apply_modern_stylesheet()
            
            # 显示欢迎消息
            self.feedback_manager.show_status("欢迎使用 linktunnel Unified GUI", 5000)
        
        def _setup_ui(self):
            """设置现代化 UI"""
            # 中央部件
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # 顶部标题栏
            title_bar = self._create_title_bar()
            main_layout.addWidget(title_bar)
            
            # 主内容区域（分割器）
            splitter = QSplitter(Qt.Orientation.Horizontal)
            
            # 左侧导航
            self.navigation = ModernNavigationSystem()
            self.navigation.module_changed.connect(self._on_module_changed)
            splitter.addWidget(self.navigation)
            
            # 右侧内容
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)
            
            # 模块容器
            self.module_container = ModuleContainer(
                self.config_manager,
                self.log_manager
            )
            right_layout.addWidget(self.module_container, stretch=1)
            
            # 日志查看器
            self.log_viewer = LogViewer()
            self.log_viewer.setMaximumHeight(150)
            right_layout.addWidget(self.log_viewer)
            
            # 连接日志
            self.log_manager.add_callback(self.log_viewer.append_log)
            
            splitter.addWidget(right_widget)
            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)
            splitter.setSizes([300, 900])
            
            main_layout.addWidget(splitter, stretch=1)
            
            # 状态栏
            self.status_bar = QStatusBar()
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #f5f5f5;
                    border-top: 1px solid #e0e0e0;
                    padding: 4px;
                }
            """)
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("就绪")
            
            # 设置反馈管理器的状态栏回调
            self.feedback_manager.set_status_callback(self._show_status_message)
        
        def _create_title_bar(self) -> QFrame:
            """创建标题栏"""
            title_bar = QFrame()
            title_bar.setStyleSheet("""
                QFrame {
                    background-color: #2196F3;
                    border-bottom: 2px solid #1976D2;
                }
            """)
            title_bar.setMaximumHeight(60)
            
            layout = QHBoxLayout(title_bar)
            layout.setContentsMargins(20, 10, 20, 10)
            layout.setSpacing(10)
            
            # 应用标题
            title = QLabel("linktunnel Unified GUI")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title.setFont(title_font)
            title.setStyleSheet("color: white;")
            layout.addWidget(title)
            
            # 版本信息
            version = QLabel("v0.3.0")
            version_font = QFont()
            version_font.setPointSize(10)
            version.setFont(version_font)
            version.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            layout.addWidget(version)
            
            layout.addStretch()
            
            # 状态指示器
            status_indicator = QLabel("●")
            status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
            layout.addWidget(status_indicator)
            
            status_text = QLabel("在线")
            status_text.setStyleSheet("color: white;")
            layout.addWidget(status_text)
            
            return title_bar
        
        def _setup_menu(self):
            """设置菜单栏"""
            menubar = self.menuBar()
            
            # 视图菜单
            view_menu = menubar.addMenu("视图(&V)")
            
            # 主题子菜单
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction
            from PyQt6.QtGui import QKeySequence
            
            theme_menu = QMenu("主题", self)
            view_menu.addMenu(theme_menu)
            
            light_action = QAction("浅色", self)
            light_action.triggered.connect(lambda: self._on_theme_changed(Theme.LIGHT))
            theme_menu.addAction(light_action)
            
            dark_action = QAction("深色", self)
            dark_action.triggered.connect(lambda: self._on_theme_changed(Theme.DARK))
            theme_menu.addAction(dark_action)
            
            system_action = QAction("跟随系统", self)
            system_action.triggered.connect(lambda: self._on_theme_changed(Theme.SYSTEM))
            theme_menu.addAction(system_action)
            
            theme_menu.addSeparator()
            
            toggle_action = QAction("切换主题", self)
            toggle_action.setShortcut(QKeySequence("Ctrl+T"))
            toggle_action.triggered.connect(self._on_toggle_theme)
            theme_menu.addAction(toggle_action)
            
            # 帮助菜单
            help_menu = menubar.addMenu("帮助(&H)")
            
            manual_action = QAction("用户手册", self)
            manual_action.setShortcut(QKeySequence("F1"))
            manual_action.triggered.connect(self._on_show_manual)
            help_menu.addAction(manual_action)
            
            shortcuts_action = QAction("快捷键列表", self)
            shortcuts_action.triggered.connect(self._on_show_shortcuts)
            help_menu.addAction(shortcuts_action)
            
            help_menu.addSeparator()
            
            online_docs_action = QAction("在线文档", self)
            online_docs_action.triggered.connect(self._on_open_online_docs)
            help_menu.addAction(online_docs_action)
            
            github_action = QAction("GitHub 仓库", self)
            github_action.triggered.connect(self._on_open_github)
            help_menu.addAction(github_action)
            
            help_menu.addSeparator()
            
            about_action = QAction("关于", self)
            about_action.triggered.connect(self._on_about)
            help_menu.addAction(about_action)
        
        def _apply_modern_stylesheet(self):
            """应用现代化样式表"""
            stylesheet = """
                QMainWindow {
                    background-color: #ffffff;
                }
                
                QWidget {
                    background-color: #ffffff;
                }
                
                QMenuBar {
                    background-color: #f5f5f5;
                    border-bottom: 1px solid #e0e0e0;
                }
                
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                }
                
                QMenu::item:selected {
                    background-color: #2196F3;
                    color: white;
                }
                
                QSplitter::handle {
                    background-color: #e0e0e0;
                    width: 1px;
                }
                
                QSplitter::handle:hover {
                    background-color: #2196F3;
                }
            """
            self.setStyleSheet(stylesheet)
        
        def _on_theme_changed(self, theme: Theme):
            """主题改变"""
            self.theme_manager.set_theme(theme)
            self.status_bar.showMessage(f"已切换到{theme.value}主题", 3000)
        
        def _on_toggle_theme(self):
            """切换主题"""
            self.theme_manager.toggle_theme()
            current_theme = self.theme_manager.get_current_theme()
            self.status_bar.showMessage(f"已切换到{current_theme.value}主题", 3000)
        
        def _on_about(self):
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
        
        def _on_show_manual(self):
            """显示用户手册"""
            self.help_manager.show_user_manual()
        
        def _on_show_shortcuts(self):
            """显示快捷键"""
            self.help_manager.show_shortcuts()
        
        def _on_open_online_docs(self):
            """打开在线文档"""
            self.help_manager.open_online_docs()
            self.feedback_manager.show_status("已在浏览器中打开在线文档", 3000)
        
        def _on_open_github(self):
            """打开 GitHub"""
            self.help_manager.open_github_repo()
            self.feedback_manager.show_status("已在浏览器中打开 GitHub 仓库", 3000)
        
        def _register_modules(self):
            """注册所有模块"""
            from linktunnel.unified_gui.modules.serial_module import SerialModule
            from linktunnel.unified_gui.modules.network_module import NetworkModule
            from linktunnel.unified_gui.modules.proxy_module import ProxyModule
            from linktunnel.unified_gui.modules.grbl_module import GrblModule
            from linktunnel.unified_gui.modules.ble_module import BLEModule
            from linktunnel.unified_gui.modules.i2c_module import I2CModule
            
            modules = [
                ("serial", "串口工具", SerialModule),
                ("network", "网络中继", NetworkModule),
                ("proxy", "代理管理", ProxyModule),
                ("grbl", "Grbl CNC", GrblModule),
                ("ble", "BLE 蓝牙扫描", BLEModule),
                ("i2c", "I2C 扫描", I2CModule),
            ]
            
            for name, display_name, module_class in modules:
                module = module_class(self.config_manager, self.log_manager)
                self.module_container.register_module(module)
                self.navigation.add_module(name, display_name)
            
            # 显示最后活动的模块
            last_module = self.config_manager.get("last_active_module", "serial")
            self.navigation.set_active_module(last_module)
        
        def _on_module_changed(self, module_name: str):
            """模块切换"""
            self.module_container.show_module(module_name)
            self.config_manager.set("last_active_module", module_name)
            self.status_bar.showMessage(f"已切换到: {module_name}")
            
            # 延迟垃圾回收
            QTimer.singleShot(1000, MemoryOptimizer.force_gc)
        
        def _setup_performance_monitoring(self):
            """设置性能监控"""
            self._performance_timer = QTimer()
            self._performance_timer.timeout.connect(self._check_performance)
            self._performance_timer.start(30000)  # 30 秒
        
        def _check_performance(self):
            """检查性能"""
            cpu_usage = CPUOptimizer.get_cpu_usage()
            memory_info = MemoryOptimizer.get_memory_usage()
            
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
                MemoryOptimizer.optimize_memory()
        
        def _show_status_message(self, message: str, timeout: int):
            """显示状态消息"""
            self.status_bar.showMessage(message, timeout)
        
        def _load_window_state(self):
            """加载窗口状态"""
            width = self.config_manager.get("window.width", 1400)
            height = self.config_manager.get("window.height", 900)
            self.resize(width, height)
            
            if self.config_manager.get("window.maximized", False):
                self.showMaximized()
        
        def closeEvent(self, event):
            """窗口关闭"""
            if self._performance_timer:
                self._performance_timer.stop()
            
            self.config_manager.set("window.width", self.width())
            self.config_manager.set("window.height", self.height())
            self.config_manager.set("window.maximized", self.isMaximized())
            
            self.module_container.stop_all_modules()
            MemoryOptimizer.optimize_memory()
            
            event.accept()

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk
    
    class ModernMainWindow(tk.Tk):
        """现代化主窗口（tkinter 版本）"""
        
        def __init__(self, config_manager: ConfigManager):
            super().__init__()
            self.config_manager = config_manager
            self.log_manager = LogManager(log_level=config_manager.get("log_level", "INFO"))
            
            self.title("linktunnel Unified GUI")
            self._setup_ui()
            self._load_window_state()
        
        def _setup_ui(self):
            """设置 UI"""
            main_frame = ttk.Frame(self)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题栏
            title_frame = ttk.Frame(main_frame)
            title_frame.pack(fill=tk.X)
            
            title = ttk.Label(title_frame, text="linktunnel Unified GUI", font=("Arial", 14, "bold"))
            title.pack(pady=10)
            
            # 主内容
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # 导航
            from linktunnel.unified_gui.ui.modern_navigation import ModernNavigationSystem
            self.navigation = ModernNavigationSystem(content_frame)
            self.navigation.pack(side=tk.LEFT, fill=tk.Y)
            
            # 模块容器
            from linktunnel.unified_gui.core.module_container import ModuleContainer
            self.module_container = ModuleContainer(
                self.config_manager,
                self.log_manager,
                content_frame
            )
            self.module_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        def _load_window_state(self):
            """加载窗口状态"""
            width = self.config_manager.get("window.width", 1400)
            height = self.config_manager.get("window.height", 900)
            self.geometry(f"{width}x{height}")
