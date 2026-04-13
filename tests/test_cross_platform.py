"""
跨平台兼容性测试
"""

import sys
import platform
import pytest
from pathlib import Path


class TestPlatformDetection:
    """平台检测测试"""
    
    def test_platform_detection(self):
        """测试平台检测"""
        system = platform.system()
        assert system in ["Windows", "Darwin", "Linux"]
    
    def test_python_version(self):
        """测试 Python 版本"""
        version = sys.version_info
        assert version.major == 3
        assert version.minor >= 8


class TestConfigPaths:
    """配置路径测试"""
    
    def test_config_directory_creation(self):
        """测试配置目录创建"""
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config_dir = config_manager._get_config_dir()
        
        assert config_dir.exists()
        assert config_dir.is_dir()
    
    def test_config_file_path(self):
        """测试配置文件路径"""
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config_file = config_manager._get_config_file()
        
        assert config_file.parent.exists()
        assert config_file.suffix == ".json"
    
    def test_platform_specific_paths(self):
        """测试平台特定路径"""
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config_dir = config_manager._get_config_dir()
        
        system = platform.system()
        
        if system == "Windows":
            # Windows: %LOCALAPPDATA%\linktunnel\unified-gui
            assert "linktunnel" in str(config_dir).lower()
        elif system == "Darwin":
            # macOS: ~/Library/Application Support/linktunnel/unified-gui
            assert "Library" in str(config_dir)
            assert "Application Support" in str(config_dir)
        elif system == "Linux":
            # Linux: ~/.config/linktunnel/unified-gui
            assert ".config" in str(config_dir)


class TestLogPaths:
    """日志路径测试"""
    
    def test_log_directory_creation(self):
        """测试日志目录创建"""
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        log_manager = LogManager()
        log_dir = log_manager._get_log_dir()
        
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_platform_specific_log_paths(self):
        """测试平台特定日志路径"""
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        log_manager = LogManager()
        log_dir = log_manager._get_log_dir()
        
        system = platform.system()
        
        if system == "Windows":
            # Windows: %LOCALAPPDATA%\linktunnel\unified-gui\logs
            assert "linktunnel" in str(log_dir).lower()
        elif system == "Darwin":
            # macOS: ~/Library/Logs/linktunnel/unified-gui
            assert "Library" in str(log_dir)
            assert "Logs" in str(log_dir)
        elif system == "Linux":
            # Linux: ~/.local/share/linktunnel/unified-gui/logs
            assert ".local" in str(log_dir)
            assert "share" in str(log_dir)


class TestImports:
    """导入测试"""
    
    def test_core_imports(self):
        """测试核心模块导入"""
        from linktunnel.unified_gui.core import config_manager
        from linktunnel.unified_gui.core import log_manager
        from linktunnel.unified_gui.core import base_module
        from linktunnel.unified_gui.core import module_container
        from linktunnel.unified_gui.core import theme_manager
        from linktunnel.unified_gui.core import feedback_manager
        from linktunnel.unified_gui.core import help_manager
        
        assert config_manager is not None
        assert log_manager is not None
        assert base_module is not None
        assert module_container is not None
        assert theme_manager is not None
        assert feedback_manager is not None
        assert help_manager is not None
    
    def test_module_imports(self):
        """测试功能模块导入"""
        from linktunnel.unified_gui.modules import serial_module
        from linktunnel.unified_gui.modules import network_module
        from linktunnel.unified_gui.modules import proxy_module
        from linktunnel.unified_gui.modules import grbl_module
        from linktunnel.unified_gui.modules import ble_module
        from linktunnel.unified_gui.modules import i2c_module
        
        assert serial_module is not None
        assert network_module is not None
        assert proxy_module is not None
        assert grbl_module is not None
        assert ble_module is not None
        assert i2c_module is not None
    
    def test_ui_imports(self):
        """测试 UI 组件导入"""
        from linktunnel.unified_gui.ui import log_viewer
        from linktunnel.unified_gui.ui import navigation_system
        
        assert log_viewer is not None
        assert navigation_system is not None
    
    def test_utils_imports(self):
        """测试工具模块导入"""
        from linktunnel.unified_gui.utils import tooltip_helper
        from linktunnel.unified_gui.utils import performance
        
        assert tooltip_helper is not None
        assert performance is not None


class TestPyQt6Availability:
    """PyQt6 可用性测试"""
    
    def test_pyqt6_import(self):
        """测试 PyQt6 导入"""
        try:
            import PyQt6
            from PyQt6 import QtCore, QtGui, QtWidgets
            assert True
        except ImportError:
            pytest.skip("PyQt6 not installed")
    
    def test_pyqt6_version(self):
        """测试 PyQt6 版本"""
        try:
            from PyQt6 import QtCore
            version = QtCore.PYQT_VERSION_STR
            assert version >= "6.4.0"
        except ImportError:
            pytest.skip("PyQt6 not installed")


class TestOptionalDependencies:
    """可选依赖测试"""
    
    def test_bleak_availability(self):
        """测试 bleak 可用性"""
        try:
            import bleak
            assert bleak is not None
        except ImportError:
            pytest.skip("bleak not installed (optional)")
    
    def test_smbus2_availability(self):
        """测试 smbus2 可用性"""
        if platform.system() != "Linux":
            pytest.skip("smbus2 only for Linux")
        
        try:
            import smbus2
            assert smbus2 is not None
        except ImportError:
            pytest.skip("smbus2 not installed (optional)")
    
    def test_psutil_availability(self):
        """测试 psutil 可用性"""
        try:
            import psutil
            assert psutil is not None
        except ImportError:
            pytest.skip("psutil not installed (optional)")


class TestFileOperations:
    """文件操作测试"""
    
    def test_config_read_write(self):
        """测试配置读写"""
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # 写入测试
        config_manager.set("test.key", "test_value")
        config_manager.save()
        
        # 读取测试
        value = config_manager.get("test.key")
        assert value == "test_value"
        
        # 清理
        config_manager.set("test.key", None)
        config_manager.save()
    
    def test_log_file_creation(self):
        """测试日志文件创建"""
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        log_manager = LogManager()
        log_manager.info("test", "Test message")
        
        log_dir = log_manager._get_log_dir()
        log_files = list(log_dir.glob("*.log"))
        
        assert len(log_files) > 0


class TestPerformance:
    """性能测试"""
    
    def test_memory_usage(self):
        """测试内存使用"""
        try:
            from linktunnel.unified_gui.utils.performance import MemoryOptimizer
            
            info = MemoryOptimizer.get_memory_usage()
            
            assert info["rss_mb"] >= 0
            assert info["vms_mb"] >= 0
            assert info["percent"] >= 0
        except ImportError:
            pytest.skip("psutil not installed")
    
    def test_cpu_usage(self):
        """测试 CPU 使用率"""
        try:
            from linktunnel.unified_gui.utils.performance import CPUOptimizer
            
            cpu = CPUOptimizer.get_cpu_usage()
            
            assert cpu >= 0
            assert cpu <= 100
        except ImportError:
            pytest.skip("psutil not installed")


class TestModuleCreation:
    """模块创建测试"""
    
    def test_serial_module_creation(self):
        """测试串口模块创建"""
        from linktunnel.unified_gui.modules.serial_module import SerialModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        config_manager = ConfigManager()
        log_manager = LogManager()
        
        module = SerialModule(config_manager, log_manager)
        assert module is not None
        assert module.get_module_name() == "serial"
    
    def test_network_module_creation(self):
        """测试网络模块创建"""
        from linktunnel.unified_gui.modules.network_module import NetworkModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        config_manager = ConfigManager()
        log_manager = LogManager()
        
        module = NetworkModule(config_manager, log_manager)
        assert module is not None
        assert module.get_module_name() == "network"
    
    def test_all_modules_creation(self):
        """测试所有模块创建"""
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from linktunnel.unified_gui.modules.serial_module import SerialModule
        from linktunnel.unified_gui.modules.network_module import NetworkModule
        from linktunnel.unified_gui.modules.proxy_module import ProxyModule
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.modules.i2c_module import I2CModule
        
        config_manager = ConfigManager()
        log_manager = LogManager()
        
        modules = [
            SerialModule(config_manager, log_manager),
            NetworkModule(config_manager, log_manager),
            ProxyModule(config_manager, log_manager),
            GrblModule(config_manager, log_manager),
            BLEModule(config_manager, log_manager),
            I2CModule(config_manager, log_manager),
        ]
        
        assert len(modules) == 6
        for module in modules:
            assert module is not None
            assert module.get_module_name() is not None
            assert module.get_display_name() is not None


class TestPlatformSpecific:
    """平台特定测试"""
    
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
    def test_windows_specific(self):
        """Windows 特定测试"""
        # 测试 Windows 特定功能
        assert platform.system() == "Windows"
    
    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
    def test_macos_specific(self):
        """macOS 特定测试"""
        # 测试 macOS 特定功能
        assert platform.system() == "Darwin"
    
    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_linux_specific(self):
        """Linux 特定测试"""
        # 测试 Linux 特定功能
        assert platform.system() == "Linux"
        
        # 测试 I2C 模块（仅 Linux）
        from linktunnel.unified_gui.modules.i2c_module import I2CModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        config_manager = ConfigManager()
        log_manager = LogManager()
        
        module = I2CModule(config_manager, log_manager)
        assert module is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
