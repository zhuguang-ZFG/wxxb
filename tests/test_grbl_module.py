"""测试 Grbl CNC 控制模块"""

from __future__ import annotations

import pytest


def test_grbl_module_import():
    """测试 Grbl 模块可以导入"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        assert GrblModule is not None
    except ImportError as e:
        # PyQt6 未安装时跳过
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_grbl_module_basic_attributes():
    """测试 Grbl 模块基本属性"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = GrblModule(config_manager, log_manager)
            
            assert module.get_module_name() == "grbl"
            assert module.get_display_name() == "Grbl CNC 控制"
            assert module.get_icon() is not None
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_grbl_module_ui_components():
    """测试 Grbl 模块 UI 组件是否正确创建"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = GrblModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            if not hasattr(module, 'tabs'):
                pytest.skip("tkinter version does not have tabs widget")
            
            # 验证关键 UI 组件存在
            # 连接配置
            assert hasattr(module, 'serial_radio')
            assert hasattr(module, 'wifi_radio')
            assert hasattr(module, 'port_combo')
            assert hasattr(module, 'baud_combo')
            assert hasattr(module, 'wifi_address')
            assert hasattr(module, 'connect_btn')
            assert hasattr(module, 'disconnect_btn')
            assert hasattr(module, 'reset_btn')
            
            # 状态显示
            assert hasattr(module, 'state_label')
            assert hasattr(module, 'position_label')
            assert hasattr(module, 'buffer_label')
            
            # 标签页
            assert hasattr(module, 'tabs')
            assert module.tabs.count() == 3  # 3 个标签页
            
            # G 代码流式传输
            assert hasattr(module, 'gcode_file_entry')
            assert hasattr(module, 'stream_start_btn')
            assert hasattr(module, 'stream_pause_btn')
            assert hasattr(module, 'stream_resume_btn')
            assert hasattr(module, 'stream_stop_btn')
            assert hasattr(module, 'progress_bar')
            assert hasattr(module, 'stream_log')
            
            # 手动控制
            assert hasattr(module, 'manual_cmd_entry')
            assert hasattr(module, 'manual_log')
            
            # 设置
            assert hasattr(module, 'settings_text')
            assert hasattr(module, 'setting_key')
            assert hasattr(module, 'setting_value')
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_grbl_module_connection_type_toggle():
    """测试连接类型切换"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = GrblModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            if not hasattr(module, 'serial_radio'):
                pytest.skip("tkinter version does not have radio buttons")
            
            # 默认应该是串口模式
            assert module.serial_radio.isChecked()
            assert module.serial_config_widget.isVisible()
            assert not module.wifi_config_widget.isVisible()
            
            # 切换到 WiFi 模式
            module.wifi_radio.setChecked(True)
            assert not module.serial_config_widget.isVisible()
            assert module.wifi_config_widget.isVisible()
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_grbl_module_initial_state():
    """测试 Grbl 模块初始状态"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = GrblModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            if not hasattr(module, 'connect_btn'):
                pytest.skip("tkinter version does not have connect button")
            
            # 初始状态应该是未连接
            assert not module._connected
            assert not module._streaming
            assert module._grbl_serial is None
            
            # 按钮状态
            assert module.connect_btn.isEnabled()
            assert not module.disconnect_btn.isEnabled()
            assert not module.reset_btn.isEnabled()
            assert not module.stream_start_btn.isEnabled()
            
            # 状态显示
            assert module.state_label.text() == "未连接"
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_grbl_module_config_save_load():
    """测试 Grbl 模块配置保存和加载"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = GrblModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            if not hasattr(module, '_save_current_config'):
                pytest.skip("tkinter version does not have config save")
            
            # 设置一些配置
            module.wifi_radio.setChecked(True)
            module.wifi_address.setText("socket://192.168.1.100:23")
            module.baud_combo.setCurrentText("230400")
            
            # 保存配置
            module._save_current_config()
            
            # 创建新模块实例，应该加载保存的配置
            module2 = GrblModule(config_manager, log_manager)
            
            # 验证配置已加载（注意：_load_saved_config 在 __init__ 中调用）
            config = module2.load_config()
            assert config.get("connection_type") == "wifi"
            assert config.get("wifi_address") == "socket://192.168.1.100:23"
            assert config.get("baudrate") == 230400
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_grbl_module_backend_integration():
    """测试 Grbl 模块与后端代码的集成"""
    try:
        # 验证可以导入所需的后端模块
        from linktunnel.grbl.client import open_grbl_serial
        from linktunnel.grbl.protocol import (
            REALTIME_STATUS,
            REALTIME_RESET,
            REALTIME_HOLD,
            REALTIME_RESUME,
            send_line,
            read_until_ok,
        )
        from linktunnel.grbl.status import parse_status_report
        from linktunnel.grbl.stream_job import iter_gcode_lines
        from linktunnel.grbl.report import dump_settings, dump_build_info
        
        # 验证所有必需的函数都存在
        assert callable(open_grbl_serial)
        assert callable(send_line)
        assert callable(read_until_ok)
        assert callable(parse_status_report)
        assert callable(iter_gcode_lines)
        assert callable(dump_settings)
        assert callable(dump_build_info)
        
        # 验证实时命令常量
        assert REALTIME_STATUS == b"?"
        assert REALTIME_RESET == b"\x18"
        assert REALTIME_HOLD == b"!"
        assert REALTIME_RESUME == b"~"
        
    except ImportError as e:
        pytest.fail(f"Failed to import required backend modules: {e}")


def test_grbl_module_status_parsing():
    """测试状态报告解析"""
    from linktunnel.grbl.status import parse_status_report
    
    # 测试典型的状态报告
    report = parse_status_report("<Idle|MPos:0.000,0.000,0.000|FS:0,0>")
    assert report is not None
    assert report.state == "Idle"
    assert "MPos" in report.fields
    assert report.fields["MPos"] == "0.000,0.000,0.000"
    
    # 测试带缓冲区的状态报告
    report2 = parse_status_report("<Run|WPos:10.5,20.3,5.0|Bf:15,127|FS:500,8000>")
    assert report2 is not None
    assert report2.state == "Run"
    assert "WPos" in report2.fields
    assert "Bf" in report2.fields
    assert report2.fields["Bf"] == "15,127"


def test_grbl_module_occupied_resources():
    """测试资源占用检测"""
    try:
        from linktunnel.unified_gui.modules.grbl_module import GrblModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = GrblModule(config_manager, log_manager)
            
            # 未连接时不应占用资源
            assert module.get_occupied_resources() == []
            
            # 模拟连接状态（不实际连接）
            if hasattr(module, 'port_combo'):
                module._connected = True
                module.serial_radio.setChecked(True)
                module.port_combo.addItem("COM1")
                module.port_combo.setCurrentText("COM1")
                
                # 应该报告占用 COM1
                resources = module.get_occupied_resources()
                assert "COM1" in resources
                
                # WiFi 模式不应占用串口资源
                module.wifi_radio.setChecked(True)
                assert module.get_occupied_resources() == []
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
