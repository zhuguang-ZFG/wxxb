"""测试帮助管理器"""

import pytest


def test_help_manager_import():
    """测试帮助管理器导入"""
    try:
        from linktunnel.unified_gui.core.help_manager import HelpManager

        assert HelpManager is not None

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_help_manager_creation():
    """测试帮助管理器创建"""
    try:
        from linktunnel.unified_gui.core.help_manager import HelpManager

        manager = HelpManager()
        assert manager is not None

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_shortcuts_dialog():
    """测试快捷键对话框"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.help_manager import ShortcutsDialog
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        dialog = ShortcutsDialog()
        assert dialog is not None
        assert dialog.windowTitle() == "快捷键列表"

        print("✅ 快捷键对话框创建成功")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_user_manual_dialog():
    """测试用户手册对话框"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.help_manager import UserManualDialog
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        dialog = UserManualDialog()
        assert dialog is not None
        assert dialog.windowTitle() == "用户手册"

        print("✅ 用户手册对话框创建成功")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_module_help_dialog():
    """测试模块帮助对话框"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.help_manager import ModuleHelpDialog
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        # 测试不同模块的帮助
        modules = ["serial", "network", "proxy", "grbl", "ble", "i2c"]

        for module in modules:
            dialog = ModuleHelpDialog(None, module)
            assert dialog is not None
            assert module in dialog.windowTitle()

        print(f"✅ 模块帮助对话框创建成功（测试了 {len(modules)} 个模块）")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_help_manager_with_main_window():
    """测试帮助管理器与主窗口集成"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.main_window import MainWindow
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        config_mgr = ConfigManager()
        window = MainWindow(config_mgr)

        # 验证帮助管理器存在
        assert hasattr(window, "help_manager")
        assert window.help_manager is not None

        print("✅ 帮助管理器集成成功")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_tooltip_helper():
    """测试工具提示助手"""
    from linktunnel.unified_gui.utils.tooltip_helper import TooltipHelper

    # 测试通用工具提示
    assert "refresh" in TooltipHelper.TOOLTIPS
    assert "start" in TooltipHelper.TOOLTIPS
    assert "stop" in TooltipHelper.TOOLTIPS

    # 测试模块特定工具提示
    assert "serial" in TooltipHelper.MODULE_TOOLTIPS
    assert "network" in TooltipHelper.MODULE_TOOLTIPS
    assert "proxy" in TooltipHelper.MODULE_TOOLTIPS

    print("✅ 工具提示助手测试通过")


def test_tooltip_helper_set_tooltip():
    """测试设置工具提示"""
    try:
        from PyQt6.QtWidgets import QApplication, QPushButton
        from linktunnel.unified_gui.utils.tooltip_helper import TooltipHelper
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        # 创建按钮
        button = QPushButton("测试")

        # 设置通用工具提示
        TooltipHelper.set_tooltip(button, "refresh")
        assert button.toolTip() != ""

        # 设置模块特定工具提示
        button2 = QPushButton("测试2")
        TooltipHelper.set_tooltip(button2, "port_combo", "serial")
        assert button2.toolTip() != ""

        # 设置自定义工具提示
        button3 = QPushButton("测试3")
        TooltipHelper.set_custom_tooltip(button3, "自定义提示")
        assert button3.toolTip() == "自定义提示"

        print("✅ 工具提示设置功能正常")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")
