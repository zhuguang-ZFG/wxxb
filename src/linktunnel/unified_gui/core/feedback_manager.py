"""用户反馈管理器 - 统一的错误处理和用户反馈"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    pass

try:
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import (
        QMessageBox,
        QProgressDialog,
        QWidget,
    )

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class FeedbackType(Enum):
    """反馈类型"""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


class FeedbackManager:
    """用户反馈管理器"""

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化反馈管理器

        Args:
            parent: 父窗口
        """
        self.parent = parent
        self._status_callback: Optional[Callable[[str, int], None]] = None

    def set_status_callback(self, callback: Callable[[str, int], None]) -> None:
        """设置状态栏回调

        Args:
            callback: 回调函数，接受 (message, timeout) 参数
        """
        self._status_callback = callback

    def show_info(self, title: str, message: str) -> None:
        """显示信息对话框

        Args:
            title: 标题
            message: 消息内容
        """
        if not PYQT_AVAILABLE:
            print(f"[INFO] {title}: {message}")
            return

        QMessageBox.information(self.parent, title, message)

    def show_success(self, title: str, message: str) -> None:
        """显示成功对话框

        Args:
            title: 标题
            message: 消息内容
        """
        if not PYQT_AVAILABLE:
            print(f"[SUCCESS] {title}: {message}")
            return

        QMessageBox.information(self.parent, title, f"✅ {message}")

    def show_warning(self, title: str, message: str) -> None:
        """显示警告对话框

        Args:
            title: 标题
            message: 消息内容
        """
        if not PYQT_AVAILABLE:
            print(f"[WARNING] {title}: {message}")
            return

        QMessageBox.warning(self.parent, title, message)

    def show_error(self, title: str, message: str, details: Optional[str] = None) -> None:
        """显示错误对话框

        Args:
            title: 标题
            message: 消息内容
            details: 详细错误信息（可选）
        """
        if not PYQT_AVAILABLE:
            print(f"[ERROR] {title}: {message}")
            if details:
                print(f"Details: {details}")
            return

        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if details:
            msg_box.setDetailedText(details)

        msg_box.exec()

    def show_question(
        self, title: str, message: str, default_yes: bool = False
    ) -> bool:
        """显示确认对话框

        Args:
            title: 标题
            message: 消息内容
            default_yes: 默认选择是否为"是"

        Returns:
            用户是否选择"是"
        """
        if not PYQT_AVAILABLE:
            print(f"[QUESTION] {title}: {message}")
            return default_yes

        default_button = (
            QMessageBox.StandardButton.Yes
            if default_yes
            else QMessageBox.StandardButton.No
        )

        reply = QMessageBox.question(
            self.parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default_button,
        )

        return reply == QMessageBox.StandardButton.Yes

    def show_status(self, message: str, timeout: int = 3000) -> None:
        """在状态栏显示消息

        Args:
            message: 消息内容
            timeout: 超时时间（毫秒），0 表示永久显示
        """
        if self._status_callback:
            self._status_callback(message, timeout)
        else:
            print(f"[STATUS] {message}")

    def show_dependency_missing(
        self, dependency: str, install_command: str, description: str = ""
    ) -> None:
        """显示依赖缺失提示

        Args:
            dependency: 依赖名称
            install_command: 安装命令
            description: 依赖描述
        """
        message = f"缺少依赖: {dependency}\n\n"

        if description:
            message += f"{description}\n\n"

        message += f"请运行以下命令安装：\n{install_command}"

        self.show_warning("依赖缺失", message)

    def show_platform_not_supported(
        self, feature: str, supported_platforms: list[str], current_platform: str
    ) -> None:
        """显示平台不支持提示

        Args:
            feature: 功能名称
            supported_platforms: 支持的平台列表
            current_platform: 当前平台
        """
        platforms_str = "、".join(supported_platforms)
        message = (
            f"{feature} 仅支持以下平台：{platforms_str}\n\n"
            f"当前平台：{current_platform}\n\n"
            f"抱歉，此功能在您的系统上不可用。"
        )

        self.show_warning("平台不支持", message)

    def show_validation_error(self, field: str, error: str) -> None:
        """显示输入验证错误

        Args:
            field: 字段名称
            error: 错误描述
        """
        message = f"输入验证失败：\n\n字段：{field}\n错误：{error}"
        self.show_error("输入错误", message)

    def show_operation_failed(
        self, operation: str, error: Exception, suggestion: str = ""
    ) -> None:
        """显示操作失败提示

        Args:
            operation: 操作名称
            error: 异常对象
            suggestion: 建议（可选）
        """
        message = f"操作失败：{operation}\n\n错误：{str(error)}"

        if suggestion:
            message += f"\n\n建议：{suggestion}"

        details = f"异常类型：{type(error).__name__}\n异常信息：{str(error)}"

        self.show_error("操作失败", message, details)

    def create_progress_dialog(
        self,
        title: str,
        message: str,
        maximum: int = 0,
        cancelable: bool = True,
    ) -> Optional["ProgressDialog"]:
        """创建进度对话框

        Args:
            title: 标题
            message: 消息
            maximum: 最大值（0 表示不确定进度）
            cancelable: 是否可取消

        Returns:
            进度对话框对象
        """
        if not PYQT_AVAILABLE:
            print(f"[PROGRESS] {title}: {message}")
            return None

        return ProgressDialog(self.parent, title, message, maximum, cancelable)


class ProgressDialog:
    """进度对话框包装器"""

    def __init__(
        self,
        parent: Optional[QWidget],
        title: str,
        message: str,
        maximum: int,
        cancelable: bool,
    ):
        """初始化进度对话框

        Args:
            parent: 父窗口
            title: 标题
            message: 消息
            maximum: 最大值
            cancelable: 是否可取消
        """
        if not PYQT_AVAILABLE:
            self._dialog = None
            return

        self._dialog = QProgressDialog(message, "取消" if cancelable else None, 0, maximum, parent)
        self._dialog.setWindowTitle(title)
        self._dialog.setMinimumDuration(500)  # 500ms 后才显示
        self._dialog.setAutoClose(True)
        self._dialog.setAutoReset(True)

        if not cancelable:
            self._dialog.setCancelButton(None)

    def set_value(self, value: int) -> None:
        """设置进度值

        Args:
            value: 进度值
        """
        if self._dialog:
            self._dialog.setValue(value)

    def set_message(self, message: str) -> None:
        """设置消息

        Args:
            message: 消息内容
        """
        if self._dialog:
            self._dialog.setLabelText(message)

    def was_canceled(self) -> bool:
        """检查是否被取消

        Returns:
            是否被取消
        """
        if self._dialog:
            return self._dialog.wasCanceled()
        return False

    def close(self) -> None:
        """关闭对话框"""
        if self._dialog:
            self._dialog.close()


class InputValidator:
    """输入验证器"""

    @staticmethod
    def validate_not_empty(value: str, field_name: str) -> tuple[bool, str]:
        """验证非空

        Args:
            value: 值
            field_name: 字段名称

        Returns:
            (是否有效, 错误消息)
        """
        if not value or not value.strip():
            return False, f"{field_name}不能为空"
        return True, ""

    @staticmethod
    def validate_port(value: str, field_name: str = "端口") -> tuple[bool, str]:
        """验证端口号

        Args:
            value: 值
            field_name: 字段名称

        Returns:
            (是否有效, 错误消息)
        """
        try:
            port = int(value)
            if port < 1 or port > 65535:
                return False, f"{field_name}必须在 1-65535 之间"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是数字"

    @staticmethod
    def validate_ip_address(value: str, field_name: str = "IP 地址") -> tuple[bool, str]:
        """验证 IP 地址

        Args:
            value: 值
            field_name: 字段名称

        Returns:
            (是否有效, 错误消息)
        """
        import re

        # 简单的 IPv4 验证
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if re.match(ipv4_pattern, value):
            parts = value.split(".")
            if all(0 <= int(part) <= 255 for part in parts):
                return True, ""

        # 简单的 IPv6 验证（基础检查）
        if ":" in value:
            return True, ""  # 简化处理，接受包含冒号的地址

        return False, f"{field_name}格式不正确"

    @staticmethod
    def validate_url(value: str, field_name: str = "URL") -> tuple[bool, str]:
        """验证 URL

        Args:
            value: 值
            field_name: 字段名称

        Returns:
            (是否有效, 错误消息)
        """
        import re

        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if re.match(url_pattern, value, re.IGNORECASE):
            return True, ""

        return False, f"{field_name}格式不正确（应以 http:// 或 https:// 开头）"

    @staticmethod
    def validate_file_exists(value: str, field_name: str = "文件") -> tuple[bool, str]:
        """验证文件存在

        Args:
            value: 文件路径
            field_name: 字段名称

        Returns:
            (是否有效, 错误消息)
        """
        from pathlib import Path

        if not value:
            return False, f"{field_name}路径不能为空"

        path = Path(value)
        if not path.exists():
            return False, f"{field_name}不存在：{value}"

        if not path.is_file():
            return False, f"{field_name}不是文件：{value}"

        return True, ""
