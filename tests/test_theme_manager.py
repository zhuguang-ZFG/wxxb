"""测试主题管理器"""

import pytest


def test_theme_manager_import():
    """测试主题管理器导入"""
    try:
        from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme

        assert ThemeManager is not None
        assert Theme is not None

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_theme_enum():
    """测试主题枚举"""
    try:
        from linktunnel.unified_gui.core.theme_manager import Theme

        assert Theme.LIGHT.value == "light"
        assert Theme.DARK.value == "dark"
        assert Theme.SYSTEM.value == "system"

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_theme_manager_creation():
    """测试主题管理器创建"""
    try:
        from linktunnel.unified_gui.core.theme_manager import ThemeManager
        from linktunnel.unified_gui.core.config_manager import ConfigManager

        config_mgr = ConfigManager()
        theme_mgr = ThemeManager(config_mgr)

        assert theme_mgr is not None
        assert theme_mgr.config_manager == config_mgr

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_theme_manager_get_current_theme():
    """测试获取当前主题"""
    try:
        from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme
        from linktunnel.unified_gui.core.config_manager import ConfigManager

        config_mgr = ConfigManager()
        theme_mgr = ThemeManager(config_mgr)

        current_theme = theme_mgr.get_current_theme()
        assert isinstance(current_theme, Theme)

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_theme_manager_set_theme():
    """测试设置主题"""
    try:
        from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme
        from linktunnel.unified_gui.core.config_manager import ConfigManager

        config_mgr = ConfigManager()
        theme_mgr = ThemeManager(config_mgr)

        # 设置浅色主题
        theme_mgr.set_theme(Theme.LIGHT)
        assert theme_mgr.get_current_theme() == Theme.LIGHT

        # 设置深色主题
        theme_mgr.set_theme(Theme.DARK)
        assert theme_mgr.get_current_theme() == Theme.DARK

        # 设置系统主题
        theme_mgr.set_theme(Theme.SYSTEM)
        assert theme_mgr.get_current_theme() == Theme.SYSTEM

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_theme_manager_toggle():
    """测试切换主题"""
    try:
        from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme
        from linktunnel.unified_gui.core.config_manager import ConfigManager

        config_mgr = ConfigManager()
        theme_mgr = ThemeManager(config_mgr)

        # 设置为浅色
        theme_mgr.set_theme(Theme.LIGHT)
        assert theme_mgr.get_current_theme() == Theme.LIGHT

        # 切换到深色
        theme_mgr.toggle_theme()
        assert theme_mgr.get_current_theme() == Theme.DARK

        # 切换回浅色
        theme_mgr.toggle_theme()
        assert theme_mgr.get_current_theme() == Theme.LIGHT

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_theme_manager_apply_theme():
    """测试应用主题"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.theme_manager import ThemeManager, Theme
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        config_mgr = ConfigManager()
        theme_mgr = ThemeManager(config_mgr)

        # 应用浅色主题
        theme_mgr.set_theme(Theme.LIGHT)
        theme_mgr.apply_theme()

        # 应用深色主题
        theme_mgr.set_theme(Theme.DARK)
        theme_mgr.apply_theme()

        print("✅ 主题应用功能正常")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_main_window_with_theme():
    """测试主窗口集成主题管理器"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.main_window import MainWindow
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        config_mgr = ConfigManager()
        window = MainWindow(config_mgr)

        # 验证主题管理器存在
        assert hasattr(window, "theme_manager")
        assert window.theme_manager is not None

        print("✅ 主窗口主题管理器集成成功")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")
