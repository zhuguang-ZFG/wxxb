"""测试浏览器控制台打开功能集成"""

from __future__ import annotations

import pytest


def test_dashboard_url_generation():
    """测试控制台 URL 生成功能"""
    from linktunnel.dashboard_open import (
        yacd_meta_browser_url,
        local_embedded_ui_url,
        host_port_from_api_base,
    )
    
    # 测试 host_port_from_api_base
    assert host_port_from_api_base("http://127.0.0.1:9090") == ("127.0.0.1", 9090)
    assert host_port_from_api_base("http://localhost:8080") == ("localhost", 8080)
    assert host_port_from_api_base("https://example.com") == ("example.com", 443)
    assert host_port_from_api_base("http://example.com") == ("example.com", 9090)
    
    # 测试 Yacd URL 生成
    yacd_url = yacd_meta_browser_url("http://127.0.0.1:9090", "my_secret")
    assert "yacd.metacubex.one" in yacd_url
    assert "hostname=127.0.0.1" in yacd_url
    assert "port=9090" in yacd_url
    assert "secret=my_secret" in yacd_url
    
    # 测试无 secret 的情况
    yacd_url_no_secret = yacd_meta_browser_url("http://127.0.0.1:9090", "")
    assert "yacd.metacubex.one" in yacd_url_no_secret
    assert "secret" not in yacd_url_no_secret
    
    # 测试本地 UI URL 生成
    local_url = local_embedded_ui_url("http://127.0.0.1:9090")
    assert local_url == "http://127.0.0.1:9090/ui"
    
    local_url_trailing = local_embedded_ui_url("http://127.0.0.1:9090/")
    assert local_url_trailing == "http://127.0.0.1:9090/ui"


def test_proxy_module_has_dashboard_button():
    """测试代理模块包含打开控制台按钮"""
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
            if not hasattr(module, '_open_dashboard_btn'):
                pytest.skip("tkinter version does not have dashboard button")
            
            # 验证按钮存在
            assert hasattr(module, '_open_dashboard_btn')
            assert module._open_dashboard_btn is not None
            
            # 验证按钮文本
            assert module._open_dashboard_btn.text() == "打开控制台"
            
            # 验证处理方法存在
            assert hasattr(module, '_on_open_dashboard')
            assert callable(module._on_open_dashboard)
            
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed")
        raise


def test_dashboard_open_integration():
    """测试控制台打开功能的完整集成"""
    from linktunnel.dashboard_open import (
        yacd_meta_browser_url,
        local_embedded_ui_url,
    )
    
    # 模拟真实场景
    api_base = "http://127.0.0.1:9090"
    secret = "test_secret_123"
    
    # 生成 Yacd URL
    yacd_url = yacd_meta_browser_url(api_base, secret)
    assert yacd_url.startswith("https://yacd.metacubex.one/")
    assert "hostname=127.0.0.1" in yacd_url
    assert "port=9090" in yacd_url
    assert "secret=test_secret_123" in yacd_url
    
    # 生成本地 UI URL
    local_url = local_embedded_ui_url(api_base)
    assert local_url == "http://127.0.0.1:9090/ui"
    
    # 验证 URL 格式正确
    from urllib.parse import urlparse, parse_qs
    
    parsed_yacd = urlparse(yacd_url)
    assert parsed_yacd.scheme == "https"
    assert parsed_yacd.netloc == "yacd.metacubex.one"
    
    query_params = parse_qs(parsed_yacd.query)
    assert query_params["hostname"] == ["127.0.0.1"]
    assert query_params["port"] == ["9090"]
    assert query_params["secret"] == ["test_secret_123"]
    
    parsed_local = urlparse(local_url)
    assert parsed_local.scheme == "http"
    assert parsed_local.netloc == "127.0.0.1:9090"
    assert parsed_local.path == "/ui"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
