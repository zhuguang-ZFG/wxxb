"""测试 I2C 模块"""

import pytest
import platform


def test_i2c_module_import():
    """测试 I2C 模块导入"""
    try:
        from linktunnel.unified_gui.modules.i2c_module import I2CModule

        assert I2CModule is not None
    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_i2c_module_basic_attributes():
    """测试 I2C 模块基本属性"""
    try:
        from linktunnel.unified_gui.modules.i2c_module import I2CModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager

        config_mgr = ConfigManager()
        log_mgr = LogManager()

        module = I2CModule(config_mgr, log_mgr)

        assert module.get_module_name() == "i2c"
        assert module.get_display_name() == "I2C 扫描"
        assert module.get_icon() is not None

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_i2c_module_platform_detection():
    """测试 I2C 模块平台检测"""
    try:
        from linktunnel.unified_gui.modules.i2c_module import I2CModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager

        config_mgr = ConfigManager()
        log_mgr = LogManager()

        module = I2CModule(config_mgr, log_mgr)

        # 验证平台检测
        is_linux = platform.system() == "Linux"
        assert module._is_linux == is_linux

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


@pytest.mark.skipif(platform.system() != "Linux", reason="I2C 仅支持 Linux")
def test_i2c_module_ui_components():
    """测试 I2C 模块 UI 组件（仅 Linux）"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.modules.i2c_module import I2CModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        config_mgr = ConfigManager()
        log_mgr = LogManager()

        module = I2CModule(config_mgr, log_mgr)

        # 如果 smbus2 可用，验证关键组件存在
        if module._smbus_available:
            assert hasattr(module, "bus_combo")
            assert hasattr(module, "scan_btn")
            assert hasattr(module, "address_labels")
            assert hasattr(module, "scan_log")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")
