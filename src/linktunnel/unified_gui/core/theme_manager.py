"""主题管理器 - 支持浅色和深色主题"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager

try:
    from PyQt6.QtGui import QPalette, QColor
    from PyQt6.QtWidgets import QApplication

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class Theme(Enum):
    """主题枚举"""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ThemeManager:
    """主题管理器"""

    def __init__(self, config_manager: ConfigManager):
        """初始化主题管理器

        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self._current_theme = self._load_theme()

    def _load_theme(self) -> Theme:
        """从配置加载主题"""
        theme_str = self.config_manager.get("theme", "system")
        try:
            return Theme(theme_str)
        except ValueError:
            return Theme.SYSTEM

    def get_current_theme(self) -> Theme:
        """获取当前主题"""
        return self._current_theme

    def set_theme(self, theme: Theme) -> None:
        """设置主题

        Args:
            theme: 主题类型
        """
        self._current_theme = theme
        self.config_manager.set("theme", theme.value)
        self.apply_theme()

    def apply_theme(self) -> None:
        """应用主题到应用程序"""
        if not PYQT_AVAILABLE:
            return

        app = QApplication.instance()
        if not app:
            return

        theme = self._current_theme

        # 如果是系统主题，检测系统主题
        if theme == Theme.SYSTEM:
            theme = self._detect_system_theme()

        if theme == Theme.DARK:
            self._apply_dark_theme(app)
        else:
            self._apply_light_theme(app)

    def _detect_system_theme(self) -> Theme:
        """检测系统主题

        Returns:
            检测到的主题
        """
        if not PYQT_AVAILABLE:
            return Theme.LIGHT

        # 尝试检测系统主题
        # 这里使用简单的方法：检查默认调色板的背景色
        app = QApplication.instance()
        if app:
            palette = app.palette()
            bg_color = palette.color(QPalette.ColorRole.Window)
            # 如果背景色较暗，认为是深色主题
            if bg_color.lightness() < 128:
                return Theme.DARK

        return Theme.LIGHT

    def _apply_light_theme(self, app: QApplication) -> None:
        """应用浅色主题

        Args:
            app: Qt 应用程序实例
        """
        # 重置为默认样式
        app.setStyleSheet("")

        # 创建浅色调色板
        palette = QPalette()

        # 基础颜色
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        app.setPalette(palette)

        # 应用样式表
        stylesheet = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
        }
        
        QTextEdit, QPlainTextEdit, QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 2px;
        }
        
        QPushButton {
            background-color: #e0e0e0;
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 5px 15px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        
        QPushButton:disabled {
            background-color: #f0f0f0;
            color: #999999;
        }
        
        QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 3px;
        }
        
        QComboBox:hover {
            border: 1px solid #0078d7;
        }
        
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #000000;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 5px 10px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 1px solid #ffffff;
        }
        
        QTabBar::tab:hover {
            background-color: #d0d0d0;
        }
        
        QTableWidget, QTreeWidget {
            background-color: #ffffff;
            alternate-background-color: #f5f5f5;
            color: #000000;
            border: 1px solid #cccccc;
        }
        
        QHeaderView::section {
            background-color: #e0e0e0;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 4px;
        }
        
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #c0c0c0;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #a0a0a0;
        }
        
        QScrollBar:horizontal {
            background-color: #f0f0f0;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #c0c0c0;
            min-width: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #a0a0a0;
        }
        
        QStatusBar {
            background-color: #e0e0e0;
            color: #000000;
        }
        """

        app.setStyleSheet(stylesheet)

    def _apply_dark_theme(self, app: QApplication) -> None:
        """应用深色主题

        Args:
            app: Qt 应用程序实例
        """
        # 创建深色调色板
        palette = QPalette()

        # 基础颜色
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        # 禁用状态
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.HighlightedText,
            QColor(127, 127, 127),
        )

        app.setPalette(palette)

        # 应用样式表
        stylesheet = """
        QMainWindow {
            background-color: #353535;
        }
        
        QWidget {
            background-color: #353535;
            color: #ffffff;
        }
        
        QTextEdit, QPlainTextEdit, QLineEdit {
            background-color: #232323;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 2px;
            selection-background-color: #2a82da;
        }
        
        QPushButton {
            background-color: #454545;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px 15px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #555555;
        }
        
        QPushButton:pressed {
            background-color: #656565;
        }
        
        QPushButton:disabled {
            background-color: #353535;
            color: #7f7f7f;
        }
        
        QComboBox {
            background-color: #232323;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
        }
        
        QComboBox:hover {
            border: 1px solid #2a82da;
        }
        
        QComboBox QAbstractItemView {
            background-color: #232323;
            color: #ffffff;
            selection-background-color: #2a82da;
        }
        
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #ffffff;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #232323;
        }
        
        QTabBar::tab {
            background-color: #454545;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 5px 10px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #232323;
            border-bottom: 1px solid #232323;
        }
        
        QTabBar::tab:hover {
            background-color: #555555;
        }
        
        QTableWidget, QTreeWidget {
            background-color: #232323;
            alternate-background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #555555;
        }
        
        QHeaderView::section {
            background-color: #454545;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
        }
        
        QScrollBar:vertical {
            background-color: #353535;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #656565;
        }
        
        QScrollBar:horizontal {
            background-color: #353535;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            min-width: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #656565;
        }
        
        QStatusBar {
            background-color: #454545;
            color: #ffffff;
        }
        
        QLabel {
            color: #ffffff;
        }
        """

        app.setStyleSheet(stylesheet)

    def toggle_theme(self) -> None:
        """切换主题（浅色 <-> 深色）"""
        if self._current_theme == Theme.LIGHT:
            self.set_theme(Theme.DARK)
        elif self._current_theme == Theme.DARK:
            self.set_theme(Theme.LIGHT)
        else:
            # 如果是系统主题，切换到深色
            self.set_theme(Theme.DARK)
