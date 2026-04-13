"""修复的主窗口 - 字体清晰，颜色正确"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager

try:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QStatusBar, QSplitter, QFrame, QPushButton, QScrollArea,
        QLineEdit, QMenuBar, QMenu
    )
    from PyQt6.QtGui import QAction, QKeySequence
    
    from linktunnel.unified_gui.core.log_manager import LogManager
    from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme
    from linktunnel.unified_gui.core.feedback_manager import FeedbackManager
    from linktunnel.unified_gui.core.help_manager import HelpManager
    from linktunnel.unified_gui.core.module_container import ModuleContainer
    from linktunnel.unified_gui.ui.log_viewer import LogViewer
    from linktunnel.unified_gui.utils.performance import MemoryOptimizer, CPUOptimizer
    
    class FixedMainWindow(QMainWindow):
        """修复的主窗口 - 字体清晰，颜色正确"""
        
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
            self.setMinimumSize(1200, 700)
            
            # 应用全局样式表（在创建 UI 之前）
            self._apply_global_stylesheet()
            
            # 设置 UI
            self._setup_ui()
            self._setup_menu()
            self._load_window_state()
            self._register_modules()
            
            # 应用主题
            self.theme_manager.apply_theme()
            
            # 显示欢迎消息
            self.feedback_manager.show_status("欢迎使用 linktunnel Unified GUI", 3000)
        
        def _apply_global_stylesheet(self):
            """应用全局样式表 - 修复字体和颜色"""
            stylesheet = """
                * {
                    font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
                    font-size: 11pt;
                    color: #000000;
                }
                
                QMainWindow {
                    background-color: #ffffff;
                }
                
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                
                QFrame {
                    background-color: #f8f9fa;
                    color: #000000;
                }
                
                QMenuBar {
                    background-color: #f5f5f5;
                    border-bottom: 1px solid #cccccc;
                    color: #000000;
                    font-size: 11pt;
                }
                
                QMenuBar::item:selected {
                    background-color: #0078d4;
                    color: #ffffff;
                }
                
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    color: #000000;
                    font-size: 11pt;
                }
                
                QMenu::item:selected {
                    background-color: #0078d4;
                    color: #ffffff;
                }
                
                QLineEdit {
                    border: 2px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 11pt;
                    background-color: #ffffff;
                    color: #000000;
                }
                
                QLineEdit:focus {
                    border: 2px solid #0078d4;
                    background-color: #ffffff;
                    color: #000000;
                }
                
                QLineEdit::placeholder {
                    color: #999999;
                }
                
                QPushButton {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px 16px;
                    background-color: #f0f0f0;
                    color: #000000;
                    font-size: 11pt;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border: 1px solid #0078d4;
                }
                
                QPushButton:pressed {
                    background-color: #0078d4;
                    color: #ffffff;
                    border: 1px solid #0078d4;
                }
                
                QLabel {
                    color: #000000;
                    font-size: 11pt;
                }
                
                QTextEdit {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    background-color: #ffffff;
                    color: #000000;
                    font-size: 10pt;
                    font-family: "Consolas", "Courier New", monospace;
                }
                
                QStatusBar {
                    background-color: #f5f5f5;
                    color: #000000;
                    border-top: 1px solid #cccccc;
                    font-size: 10pt;
                }
                
                QScrollArea {
                    background-color: #ffffff;
                    border: none;
                }
                
                QScrollBar:vertical {
                    background-color: #f5f5f5;
                    width: 12px;
                    border: 1px solid #cccccc;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #cccccc;
                    border-radius: 6px;
                    min-height: 20px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #0078d4;
                }
                
                QSplitter::handle {
                    background-color: #e0e0e0;
                    width: 2px;
                }
                
                QSplitter::handle:hover {
                    background-color: #0078d4;
                }
            """
            self.setStyleSheet(stylesheet)
        
        def _setup_ui(self):
            """设置 UI"""
            # 中央部件
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # 主内容区域（分割器）
            splitter = QSplitter(Qt.Orientation.Horizontal)
            
            # 左侧导航面板
            left_panel = self._create_left_panel()
            splitter.addWidget(left_panel)
            
            # 右侧内容区域
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
            self.log_viewer.setMaximumHeight(120)
            right_layout.addWidget(self.log_viewer)
            
            # 连接日志
            self.log_manager.add_callback(self.log_viewer.append_log)
            
            splitter.addWidget(right_widget)
            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)
            splitter.setSizes([250, 950])
            
            main_layout.addWidget(splitter, stretch=1)
            
            # 状态栏
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("就绪")
            
            # 设置反馈管理器的状态栏回调
            self.feedback_manager.set_status_callback(self._show_status_message)
        
        def _create_left_panel(self) -> QWidget:
            """创建左侧导航面板"""
            panel = QFrame()
            panel.setMaximumWidth(250)
            panel.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-right: 2px solid #cccccc;
                }
            """)
            
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(12)
            
            # 标题
            title = QLabel("功能模块")
            title_font = QFont()
            title_font.setPointSize(13)
            title_font.setBold(True)
            title.setFont(title_font)
            title.setStyleSheet("color: #000000; font-weight: bold;")
            layout.addWidget(title)
            
            # 搜索框
            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("搜索...")
            self.search_box.setMinimumHeight(36)
            self.search_box.textChanged.connect(self._on_search_changed)
            layout.addWidget(self.search_box)
            
            # 模块按钮容器
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background-color: #f8f9fa; }")
            
            self.modules_container = QWidget()
            self.modules_container.setStyleSheet("background-color: #f8f9fa;")
            self.modules_layout = QVBoxLayout(self.modules_container)
            self.modules_layout.setSpacing(8)
            self.modules_layout.setContentsMargins(0, 0, 0, 0)
            
            scroll.setWidget(self.modules_container)
            layout.addWidget(scroll, stretch=1)
            
            # 快速操作
            quick_label = QLabel("快速操作")
            quick_font = QFont()
            quick_font.setPointSize(12)
            quick_font.setBold(True)
            quick_label.setFont(quick_font)
            quick_label.setStyleSheet("color: #000000; font-weight: bold;")
            layout.addWidget(quick_label)
            
            refresh_btn = QPushButton("刷新")
            refresh_btn.setMinimumHeight(36)
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11pt;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
            layout.addWidget(refresh_btn)
            
            return panel
        
        def _setup_menu(self):
            """设置菜单栏"""
            menubar = self.menuBar()
            
            # 视图菜单
            view_menu = menubar.addMenu("视图(&V)")
            
            # 主题子菜单
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
            
            self._module_buttons = {}
            failed_modules = []
            
            for name, display_name, module_class in modules:
                try:
                    # 创建模块
                    module = module_class(self.config_manager, self.log_manager)
                    self.module_container.register_module(module)
                    
                    # 创建导航按钮
                    btn = QPushButton(display_name)
                    btn.setMinimumHeight(40)
                    btn.setStyleSheet("""
                        QPushButton {
                            text-align: left;
                            padding-left: 12px;
                            border: 1px solid #cccccc;
                            border-radius: 4px;
                            background-color: #ffffff;
                            color: #000000;
                            font-size: 11pt;
                        }
                        QPushButton:hover {
                            background-color: #f0f0f0;
                            border: 1px solid #0078d4;
                        }
                        QPushButton:pressed {
                            background-color: #0078d4;
                            color: #ffffff;
                        }
                    """)
                    btn.clicked.connect(lambda checked, n=name: self._on_module_clicked(n))
                    self.modules_layout.addWidget(btn)
                    self._module_buttons[name] = btn
                    
                except Exception as e:
                    self.log_manager.error("ModuleRegistration", f"模块 {name} 加载失败: {e}")
                    failed_modules.append(name)
            
            # 如果有模块加载失败，显示警告
            if failed_modules:
                self.feedback_manager.show_warning(
                    f"警告",
                    f"以下模块加载失败: {', '.join(failed_modules)}\n"
                    f"应用程序将继续运行，但这些模块不可用。"
                )
            
            self.modules_layout.addStretch()
            
            # 显示最后活动的模块
            last_module = self.config_manager.get("last_active_module", "serial")
            self._on_module_clicked(last_module)
        
        def _on_module_clicked(self, module_name: str):
            """模块被点击"""
            # 更新按钮状态
            for name, btn in self._module_buttons.items():
                if name == module_name:
                    btn.setStyleSheet("""
                        QPushButton {
                            text-align: left;
                            padding-left: 12px;
                            border: 1px solid #0078d4;
                            border-radius: 4px;
                            background-color: #0078d4;
                            color: #ffffff;
                            font-weight: bold;
                            font-size: 11pt;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            text-align: left;
                            padding-left: 12px;
                            border: 1px solid #cccccc;
                            border-radius: 4px;
                            background-color: #ffffff;
                            color: #000000;
                            font-size: 11pt;
                        }
                        QPushButton:hover {
                            background-color: #f0f0f0;
                            border: 1px solid #0078d4;
                        }
                    """)
            
            # 切换模块
            self.module_container.show_module(module_name)
            self.config_manager.set("last_active_module", module_name)
            self.status_bar.showMessage(f"已切换到: {module_name}")
            
            # 延迟垃圾回收
            QTimer.singleShot(1000, MemoryOptimizer.force_gc)
        
        def _on_search_changed(self, text: str):
            """搜索文本变化"""
            search_text = text.lower()
            for name, btn in self._module_buttons.items():
                visible = search_text in btn.text().lower()
                btn.setVisible(visible)
        
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
    
    class FixedMainWindow(tk.Tk):
        """修复的主窗口（tkinter 版本）"""
        
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
            
            # 左侧导航
            left_frame = ttk.Frame(main_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            ttk.Label(left_frame, text="功能模块", font=("Arial", 12, "bold")).pack(pady=10)
            
            # 右侧内容
            right_frame = ttk.Frame(main_frame)
            right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            from linktunnel.unified_gui.core.module_container import ModuleContainer
            self.module_container = ModuleContainer(
                self.config_manager,
                self.log_manager,
                right_frame
            )
            self.module_container.pack(fill=tk.BOTH, expand=True)
        
        def _load_window_state(self):
            """加载窗口状态"""
            width = self.config_manager.get("window.width", 1400)
            height = self.config_manager.get("window.height", 900)
            self.geometry(f"{width}x{height}")
