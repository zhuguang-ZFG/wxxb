"""测试代理管理模块"""

from __future__ import annotations

import pytest


def test_proxy_module_import():
    """测试代理模块可以导入"""
    try:
        from linktunnel.unified_gui.modules.proxy_module import ProxyModule
        assert ProxyModule is not None
    except ImportError as e:
        # PyQt6 未安装时跳过
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_proxy_module_basic_attributes():
    """测试代理模块基本属性"""
    try:
        from linktunnel.unified_gui.modules.proxy_module import ProxyModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = ProxyModule(config_manager, log_manager)
            
            assert module.get_module_name() == "proxy"
            assert module.get_display_name() == "代理管理"
            assert module.get_icon() is not None
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_proxy_module_format_version():
    """测试版本格式化函数"""
    try:
        from linktunnel.unified_gui.modules.proxy_module import ProxyModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = ProxyModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试（tkinter 版本没有此方法）
            if not hasattr(module, '_format_version_line'):
                pytest.skip("tkinter version does not have _format_version_line")
            
            # 测试 Mihomo 版本格式
            ver1 = {"meta": {"version": "1.18.0"}}
            assert "Mihomo" in module._format_version_line(ver1)
            assert "1.18.0" in module._format_version_line(ver1)
            
            # 测试 Clash 版本格式
            ver2 = {"version": "1.10.0"}
            assert "Clash" in module._format_version_line(ver2)
            assert "1.10.0" in module._format_version_line(ver2)
            
            # 测试空版本
            assert module._format_version_line(None) == "—"
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_proxy_module_tree_rebuild():
    """测试策略组和节点树形列表重建"""
    try:
        from linktunnel.unified_gui.modules.proxy_module import ProxyModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = ProxyModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            if not hasattr(module, '_rebuild_tree'):
                pytest.skip("tkinter version does not have _rebuild_tree")
            
            # 设置测试数据
            module._last_rows = [
                ("GLOBAL", "香港节点01", ["香港节点01", "日本节点02", "美国节点03"]),
                ("Proxy", "自动选择", ["自动选择", "DIRECT"]),
            ]
            
            # 测试无筛选条件
            module._rebuild_tree()
            assert module._tree.topLevelItemCount() == 2
            
            # 测试筛选条件
            module._filter_entry.setText("香港")
            module._rebuild_tree()
            # 应该只显示包含"香港"的组或节点
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_proxy_module_ui_components():
    """测试代理模块 UI 组件是否正确创建"""
    try:
        from linktunnel.unified_gui.modules.proxy_module import ProxyModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = ProxyModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            if not hasattr(module, '_tree'):
                pytest.skip("tkinter version does not have tree widget")
            
            # 验证关键 UI 组件存在
            assert hasattr(module, '_tree')
            assert hasattr(module, '_filter_entry')
            assert hasattr(module, '_delay_url_entry')
            assert hasattr(module, '_delay_test_btn')
            assert hasattr(module, '_close_all_btn')
            assert hasattr(module, '_apply_node_btn')
            assert hasattr(module, '_open_dashboard_btn')  # 新增：验证打开控制台按钮
            
            # 验证树形控件配置
            assert module._tree.columnCount() == 3
            assert module._tree.isColumnHidden(1)  # 类型列隐藏
            assert module._tree.isColumnHidden(2)  # 组名列隐藏
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_proxy_module_dashboard_open():
    """测试打开浏览器控制台功能"""
    try:
        from linktunnel.unified_gui.modules.proxy_module import ProxyModule
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            log_manager = LogManager()
            
            module = ProxyModule(config_manager, log_manager)
            
            # 只在 PyQt6 版本测试
            if not hasattr(module, '_on_open_dashboard'):
                pytest.skip("tkinter version does not have _on_open_dashboard")
            
            # 验证方法存在
            assert hasattr(module, '_on_open_dashboard')
            assert callable(module._on_open_dashboard)
            
            # 验证 dashboard_open 模块的函数可以导入
            from linktunnel.dashboard_open import (
                yacd_meta_browser_url,
                local_embedded_ui_url,
                open_in_browser
            )
            
            # 测试 URL 生成
            api = "http://127.0.0.1:9090"
            secret = "test_secret"
            
            yacd_url = yacd_meta_browser_url(api, secret)
            assert "yacd.metacubex.one" in yacd_url
            assert "hostname=127.0.0.1" in yacd_url
            assert "port=9090" in yacd_url
            assert "secret=test_secret" in yacd_url
            
            local_url = local_embedded_ui_url(api)
            assert local_url == "http://127.0.0.1:9090/ui"
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
