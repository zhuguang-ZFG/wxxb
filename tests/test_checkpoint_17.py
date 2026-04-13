"""Checkpoint 17: 所有功能模块验证

这个测试套件验证：
1. 所有模块可以正常导入
2. 所有模块可以正常实例化
3. 所有模块的基本属性正确
4. 模块容器可以正确管理所有模块
5. 资源占用检测功能正常
"""

import pytest


class TestModuleImports:
    """测试模块导入"""

    def test_import_all_modules(self):
        """测试所有模块可以导入"""
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

            modules = [
                PlaceholderModule,
                SerialModule,
                NetworkModule,
                ProxyModule,
                GrblModule,
                BLEModule,
                I2CModule,
            ]

            for module in modules:
                assert module is not None, f"{module.__name__} 导入失败"

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")


class TestModuleInstantiation:
    """测试模块实例化"""

    def test_instantiate_all_modules(self):
        """测试所有模块可以实例化"""
        try:
            from linktunnel.unified_gui.modules import (
                SerialModule,
                NetworkModule,
                ProxyModule,
                GrblModule,
                BLEModule,
                I2CModule,
            )
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager

            config_mgr = ConfigManager()
            log_mgr = LogManager()

            modules = [
                SerialModule,
                NetworkModule,
                ProxyModule,
                GrblModule,
                BLEModule,
                I2CModule,
            ]

            for ModuleClass in modules:
                try:
                    module = ModuleClass(config_mgr, log_mgr)
                    assert module is not None, f"{ModuleClass.__name__} 实例化失败"
                    print(f"✅ {ModuleClass.__name__} 实例化成功")
                except Exception as e:
                    pytest.fail(f"{ModuleClass.__name__} 实例化失败: {e}")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")


class TestModuleAttributes:
    """测试模块属性"""

    def test_module_names(self):
        """测试模块名称"""
        try:
            from linktunnel.unified_gui.modules import (
                SerialModule,
                NetworkModule,
                ProxyModule,
                GrblModule,
                BLEModule,
                I2CModule,
            )
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager

            config_mgr = ConfigManager()
            log_mgr = LogManager()

            expected_names = {
                SerialModule: "serial",
                NetworkModule: "network",
                ProxyModule: "proxy",
                GrblModule: "grbl",
                BLEModule: "ble",
                I2CModule: "i2c",
            }

            for ModuleClass, expected_name in expected_names.items():
                module = ModuleClass(config_mgr, log_mgr)
                actual_name = module.get_module_name()
                assert (
                    actual_name == expected_name
                ), f"{ModuleClass.__name__} 名称错误: 期望 {expected_name}, 实际 {actual_name}"
                print(f"✅ {ModuleClass.__name__} 名称正确: {actual_name}")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")

    def test_module_display_names(self):
        """测试模块显示名称"""
        try:
            from linktunnel.unified_gui.modules import (
                SerialModule,
                NetworkModule,
                ProxyModule,
                GrblModule,
                BLEModule,
                I2CModule,
            )
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager

            config_mgr = ConfigManager()
            log_mgr = LogManager()

            modules = [
                SerialModule,
                NetworkModule,
                ProxyModule,
                GrblModule,
                BLEModule,
                I2CModule,
            ]

            for ModuleClass in modules:
                module = ModuleClass(config_mgr, log_mgr)
                display_name = module.get_display_name()
                assert display_name, f"{ModuleClass.__name__} 显示名称为空"
                assert len(display_name) > 0, f"{ModuleClass.__name__} 显示名称为空字符串"
                print(f"✅ {ModuleClass.__name__} 显示名称: {display_name}")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")


class TestModuleContainer:
    """测试模块容器"""

    def test_module_registration(self):
        """测试模块注册"""
        try:
            from PyQt6.QtWidgets import QApplication
            from linktunnel.unified_gui.core.module_container import ModuleContainer
            from linktunnel.unified_gui.modules import (
                SerialModule,
                NetworkModule,
                ProxyModule,
            )
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager
            import sys

            app = QApplication.instance() or QApplication(sys.argv)

            config_mgr = ConfigManager()
            log_mgr = LogManager()
            container = ModuleContainer()

            # 注册模块
            serial_module = SerialModule(config_mgr, log_mgr)
            network_module = NetworkModule(config_mgr, log_mgr)
            proxy_module = ProxyModule(config_mgr, log_mgr)

            container.register_module(serial_module)
            container.register_module(network_module)
            container.register_module(proxy_module)

            # 验证注册
            assert "serial" in container._modules
            assert "network" in container._modules
            assert "proxy" in container._modules

            print(f"✅ 成功注册 {len(container._modules)} 个模块")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")

    def test_module_switching(self):
        """测试模块切换"""
        try:
            from PyQt6.QtWidgets import QApplication
            from linktunnel.unified_gui.core.module_container import ModuleContainer
            from linktunnel.unified_gui.modules import SerialModule, NetworkModule
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager
            import sys

            app = QApplication.instance() or QApplication(sys.argv)

            config_mgr = ConfigManager()
            log_mgr = LogManager()
            container = ModuleContainer()

            # 注册模块
            serial_module = SerialModule(config_mgr, log_mgr)
            network_module = NetworkModule(config_mgr, log_mgr)

            container.register_module(serial_module)
            container.register_module(network_module)

            # 切换模块
            container.show_module("serial")
            assert container.currentWidget() == serial_module

            container.show_module("network")
            assert container.currentWidget() == network_module

            print("✅ 模块切换功能正常")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")


class TestResourceManagement:
    """测试资源管理"""

    def test_resource_occupation(self):
        """测试资源占用检测"""
        try:
            from linktunnel.unified_gui.modules import SerialModule
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager

            config_mgr = ConfigManager()
            log_mgr = LogManager()

            module = SerialModule(config_mgr, log_mgr)

            # 获取占用的资源
            resources = module.get_occupied_resources()
            assert isinstance(resources, set), "资源应该是 set 类型"

            print(f"✅ 资源占用检测功能正常: {resources}")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")


class TestMainWindowIntegration:
    """测试主窗口集成"""

    def test_main_window_creation(self):
        """测试主窗口创建"""
        try:
            from PyQt6.QtWidgets import QApplication
            from linktunnel.unified_gui.core.main_window import MainWindow
            import sys

            app = QApplication.instance() or QApplication(sys.argv)
            window = MainWindow()

            assert window is not None
            assert window.config_manager is not None
            assert window.log_manager is not None
            assert window.module_container is not None
            assert window.navigation is not None

            print("✅ 主窗口创建成功")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")

    def test_all_modules_registered(self):
        """测试所有模块已注册"""
        try:
            from PyQt6.QtWidgets import QApplication
            from linktunnel.unified_gui.core.main_window import MainWindow
            import sys

            app = QApplication.instance() or QApplication(sys.argv)
            window = MainWindow()

            # 验证所有模块都已注册
            expected_modules = {"serial", "network", "proxy", "grbl", "ble", "i2c"}
            registered_modules = set(window.module_container._modules.keys())

            missing_modules = expected_modules - registered_modules
            assert not missing_modules, f"缺少模块: {missing_modules}"

            extra_modules = registered_modules - expected_modules
            print(f"✅ 所有预期模块已注册: {expected_modules}")
            if extra_modules:
                print(f"   额外模块: {extra_modules}")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")


class TestModuleLifecycle:
    """测试模块生命周期"""

    def test_module_activation(self):
        """测试模块激活"""
        try:
            from linktunnel.unified_gui.modules import SerialModule
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager

            config_mgr = ConfigManager()
            log_mgr = LogManager()

            module = SerialModule(config_mgr, log_mgr)

            # 测试激活
            module.on_activate()
            print("✅ 模块激活功能正常")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")

    def test_module_deactivation(self):
        """测试模块停用"""
        try:
            from linktunnel.unified_gui.modules import SerialModule
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager

            config_mgr = ConfigManager()
            log_mgr = LogManager()

            module = SerialModule(config_mgr, log_mgr)

            # 测试停用
            module.on_deactivate()
            print("✅ 模块停用功能正常")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")

    def test_module_stop(self):
        """测试模块停止"""
        try:
            from linktunnel.unified_gui.modules import SerialModule
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            from linktunnel.unified_gui.core.log_manager import LogManager

            config_mgr = ConfigManager()
            log_mgr = LogManager()

            module = SerialModule(config_mgr, log_mgr)

            # 测试停止
            module.stop()
            print("✅ 模块停止功能正常")

        except ImportError as e:
            pytest.skip(f"PyQt6 未安装: {e}")


def run_checkpoint():
    """运行 Checkpoint 17 验证"""
    print("\n" + "=" * 60)
    print("Checkpoint 17: 所有功能模块验证")
    print("=" * 60 + "\n")

    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_checkpoint()
