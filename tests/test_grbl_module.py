"""测试 Grbl 模块"""

import pytest


def test_grbl_module_import():
    """测试 Grbl 模块导入"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule

        assert GrblModule is not None
    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_grbl_module_basic_attributes():
    """测试 Grbl 模块基本属性"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager

        config_mgr = ConfigManager()
        log_mgr = LogManager()

        module = GrblModule(config_mgr, log_mgr)

        assert module.get_module_name() == "grbl"
        assert module.get_display_name() == "Grbl CNC"
        assert module.get_icon() is not None

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_grbl_module_ui_components():
    """测试 Grbl 模块 UI 组件"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        config_mgr = ConfigManager()
        log_mgr = LogManager()

        module = GrblModule(config_mgr, log_mgr)

        # 验证关键组件存在
        assert hasattr(module, "_port_combo")
        assert hasattr(module, "_connect_btn")
        assert hasattr(module, "_disconnect_btn")
        assert hasattr(module, "_machine_state")
        assert hasattr(module, "_gcode_file")
        assert hasattr(module, "_progress_bar")
        assert hasattr(module, "_manual_cmd")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_grbl_module_connection_types():
    """测试 Grbl 模块连接类型切换"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        config_mgr = ConfigManager()
        log_mgr = LogManager()

        module = GrblModule(config_mgr, log_mgr)

        # 测试串口模式（默认）
        assert module._serial_group.isVisible()
        assert not module._wifi_group.isVisible()

        # 切换到 WiFi 模式
        module._conn_type.setCurrentIndex(1)
        assert not module._serial_group.isVisible()
        assert module._wifi_group.isVisible()

        # 切换回串口模式
        module._conn_type.setCurrentIndex(0)
        assert module._serial_group.isVisible()
        assert not module._wifi_group.isVisible()

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")
