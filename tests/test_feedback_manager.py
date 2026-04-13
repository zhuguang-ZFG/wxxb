"""测试反馈管理器"""

import pytest


def test_feedback_manager_import():
    """测试反馈管理器导入"""
    try:
        from linktunnel.unified_gui.core.feedback_manager import (
            FeedbackManager,
            FeedbackType,
            InputValidator,
        )

        assert FeedbackManager is not None
        assert FeedbackType is not None
        assert InputValidator is not None

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_feedback_type_enum():
    """测试反馈类型枚举"""
    try:
        from linktunnel.unified_gui.core.feedback_manager import FeedbackType

        assert FeedbackType.INFO.value == "info"
        assert FeedbackType.SUCCESS.value == "success"
        assert FeedbackType.WARNING.value == "warning"
        assert FeedbackType.ERROR.value == "error"
        assert FeedbackType.QUESTION.value == "question"

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_feedback_manager_creation():
    """测试反馈管理器创建"""
    try:
        from linktunnel.unified_gui.core.feedback_manager import FeedbackManager

        manager = FeedbackManager()
        assert manager is not None

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")


def test_input_validator_not_empty():
    """测试非空验证"""
    from linktunnel.unified_gui.core.feedback_manager import InputValidator

    # 有效输入
    valid, error = InputValidator.validate_not_empty("test", "字段")
    assert valid is True
    assert error == ""

    # 无效输入 - 空字符串
    valid, error = InputValidator.validate_not_empty("", "字段")
    assert valid is False
    assert "不能为空" in error

    # 无效输入 - 只有空格
    valid, error = InputValidator.validate_not_empty("   ", "字段")
    assert valid is False
    assert "不能为空" in error


def test_input_validator_port():
    """测试端口验证"""
    from linktunnel.unified_gui.core.feedback_manager import InputValidator

    # 有效端口
    valid, error = InputValidator.validate_port("8080", "端口")
    assert valid is True
    assert error == ""

    valid, error = InputValidator.validate_port("1", "端口")
    assert valid is True

    valid, error = InputValidator.validate_port("65535", "端口")
    assert valid is True

    # 无效端口 - 超出范围
    valid, error = InputValidator.validate_port("0", "端口")
    assert valid is False
    assert "1-65535" in error

    valid, error = InputValidator.validate_port("65536", "端口")
    assert valid is False
    assert "1-65535" in error

    # 无效端口 - 非数字
    valid, error = InputValidator.validate_port("abc", "端口")
    assert valid is False
    assert "数字" in error


def test_input_validator_ip_address():
    """测试 IP 地址验证"""
    from linktunnel.unified_gui.core.feedback_manager import InputValidator

    # 有效 IPv4
    valid, error = InputValidator.validate_ip_address("192.168.1.1", "IP")
    assert valid is True
    assert error == ""

    valid, error = InputValidator.validate_ip_address("127.0.0.1", "IP")
    assert valid is True

    valid, error = InputValidator.validate_ip_address("0.0.0.0", "IP")
    assert valid is True

    # 有效 IPv6（简化检查）
    valid, error = InputValidator.validate_ip_address("::1", "IP")
    assert valid is True

    valid, error = InputValidator.validate_ip_address("2001:db8::1", "IP")
    assert valid is True

    # 无效 IP
    valid, error = InputValidator.validate_ip_address("256.1.1.1", "IP")
    assert valid is False

    valid, error = InputValidator.validate_ip_address("abc", "IP")
    assert valid is False


def test_input_validator_url():
    """测试 URL 验证"""
    from linktunnel.unified_gui.core.feedback_manager import InputValidator

    # 有效 URL
    valid, error = InputValidator.validate_url("http://example.com", "URL")
    assert valid is True
    assert error == ""

    valid, error = InputValidator.validate_url("https://example.com", "URL")
    assert valid is True

    valid, error = InputValidator.validate_url("http://127.0.0.1:8080", "URL")
    assert valid is True

    # 无效 URL
    valid, error = InputValidator.validate_url("example.com", "URL")
    assert valid is False
    assert "http" in error.lower()

    valid, error = InputValidator.validate_url("ftp://example.com", "URL")
    assert valid is False


def test_input_validator_file_exists():
    """测试文件存在验证"""
    from linktunnel.unified_gui.core.feedback_manager import InputValidator
    import tempfile
    import os

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_file = f.name

    try:
        # 有效文件
        valid, error = InputValidator.validate_file_exists(temp_file, "文件")
        assert valid is True
        assert error == ""

        # 无效文件 - 不存在
        valid, error = InputValidator.validate_file_exists(
            "/nonexistent/file.txt", "文件"
        )
        assert valid is False
        assert "不存在" in error

        # 无效文件 - 空路径
        valid, error = InputValidator.validate_file_exists("", "文件")
        assert valid is False
        assert "不能为空" in error

    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_feedback_manager_with_main_window():
    """测试反馈管理器与主窗口集成"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.main_window import MainWindow
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        config_mgr = ConfigManager()
        window = MainWindow(config_mgr)

        # 验证反馈管理器存在
        assert hasattr(window, "feedback_manager")
        assert window.feedback_manager is not None

        # 测试状态消息
        window.feedback_manager.show_status("测试消息", 1000)

        print("✅ 反馈管理器集成成功")

    except ImportError as e:
        pytest.skip(f"PyQt6 未安装: {e}")
