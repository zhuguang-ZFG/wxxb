"""测试所有模块导入"""

import pytest


def test_all_modules_import():
    """测试所有功能模块可以正常导入"""
    try:
        from linktunnel.unified_gui.modules import (
            PlaceholderModule,
            SerialModule,
            NetworkModule,
            ProxyModule,
            GrblModule,
            BLEModule,
            I2CModule,
        )

        # 验证所有模块都已导入
        assert PlaceholderModule is not None
        assert SerialModule is not None
        assert NetworkModule is not None
        assert ProxyModule is not None
        assert GrblModule is not None
        assert BLEModule is not None
        assert I2CModule is not None

        print("✅ 所有模块导入成功")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_main_window_import():
    """测试主窗口可以正常导入"""
    try:
        from linktunnel.unified_gui.core.main_window import MainWindow

        assert MainWindow is not None
        print("✅ 主窗口导入成功")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_module_registration():
    """测试模块注册"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.main_window import MainWindow
        import sys

        app = QApplication.instance() or QApplication(sys.argv)
        window = MainWindow()

        # 验证所有模块都已注册
        registered_modules = window.module_container._modules.keys()
        expected_modules = {"serial", "network", "proxy", "grbl", "ble", "i2c"}

        assert expected_modules.issubset(registered_modules), (
            f"缺少模块: {expected_modules - registered_modules}"
        )

        print(f"✅ 已注册 {len(registered_modules)} 个模块")
        print(f"   模块列表: {', '.join(registered_modules)}")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


if __name__ == "__main__":
    # 直接运行测试
    test_all_modules_import()
    test_main_window_import()
    test_module_registration()
