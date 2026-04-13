"""BLE 模块测试"""

import pytest
from pathlib import Path
import tempfile


def test_ble_module_import():
    """测试 BLE 模块可以导入"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        assert BLEModule is not None
    except ImportError as e:
        # PyQt6 未安装时跳过
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_basic_properties():
    """测试 BLE 模块基本属性"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            assert module.get_module_name() == "ble"
            assert module.get_display_name() == "BLE 蓝牙扫描"
            assert module.get_icon() is not None
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_dependency_detection():
    """测试 BLE 模块依赖检测"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            # 检查依赖检测是否正常工作
            # _bleak_available 应该是 True 或 False
            assert isinstance(module._bleak_available, bool)
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_ui_components():
    """测试 BLE 模块 UI 组件是否正确创建"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            try:
                from PyQt6.QtWidgets import QWidget
                
                # 如果 bleak 可用，应该有扫描控件
                if module._bleak_available:
                    assert hasattr(module, 'timeout_combo')
                    assert hasattr(module, 'start_btn')
                    assert hasattr(module, 'stop_btn')
                    assert hasattr(module, 'export_btn')
                    assert hasattr(module, 'results_table')
                    assert hasattr(module, 'status_label')
                # 如果 bleak 不可用，应该显示警告
                else:
                    # 应该有警告提示
                    pass
                    
            except ImportError:
                # tkinter 版本
                pass
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_parse_scan_output():
    """测试扫描输出解析"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            # 测试正常输出
            output = """ADDRESS            RSSI  NAME
------------------------------------------------------------
AA:BB:CC:DD:EE:FF  -45   iPhone 12
11:22:33:44:55:66  -60   Mi Band 5
77:88:99:AA:BB:CC  -75   
"""
            devices = module._parse_scan_output(output)
            assert len(devices) == 3
            assert devices[0]['address'] == 'AA:BB:CC:DD:EE:FF'
            assert devices[0]['rssi'] == '-45'
            assert devices[0]['name'] == 'iPhone 12'
            
            # 测试空输出
            output_empty = "(no BLE devices found)\n"
            devices_empty = module._parse_scan_output(output_empty)
            assert len(devices_empty) == 0
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_initial_state():
    """测试 BLE 模块初始状态"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            # 初始状态应该未运行
            assert not module.is_running()
            
            # 扫描结果应该为空
            assert module._scan_results == []
            
            # 扫描线程应该为 None
            assert module._scan_thread is None
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_config():
    """测试 BLE 模块配置保存和加载"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            # 保存配置
            test_config = {
                "timeout": 10,
                "last_export_path": "/tmp/test.txt"
            }
            module.save_config(test_config)
            
            # 加载配置
            loaded_config = module.load_config()
            assert loaded_config == test_config
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_resource_occupation():
    """测试资源占用检测"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            # BLE 模块不占用特定资源（如串口）
            resources = module.get_occupied_resources()
            assert resources == []
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_ble_module_stop():
    """测试停止模块"""
    try:
        from linktunnel.unified_gui.modules.ble_module import BLEModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_manager = ConfigManager(config_dir)
            log_manager = LogManager()
            
            module = BLEModule(config_manager, log_manager)
            
            # 停止模块
            module.stop()
            
            # 应该不再运行
            assert not module.is_running()
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise
