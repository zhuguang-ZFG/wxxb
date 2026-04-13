"""
模块基类

所有功能模块必须继承此基类。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

try:
    from PyQt6.QtCore import pyqtSignal
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import QWidget
    
    # 创建兼容的元类，结合 QWidget 的元类和 ABCMeta
    from abc import ABCMeta
    
    class BaseModuleMeta(type(QWidget), ABCMeta):
        """组合 PyQt 和 ABC 的元类"""
        pass
    
    class BaseModule(QWidget, ABC, metaclass=BaseModuleMeta):
        """模块基类（PyQt6 版本）"""
        
        # 信号定义
        status_changed = pyqtSignal(str)  # 状态变化信号
        log_message = pyqtSignal(str, str)  # 日志消息信号 (level, message)
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: QWidget | None = None
        ):
            """初始化模块
            
            Args:
                config_manager: 配置管理器
                log_manager: 日志管理器
                parent: 父窗口
            """
            super().__init__(parent)
            self.config_manager = config_manager
            self.log_manager = log_manager
            self._is_running = False
        
        @abstractmethod
        def get_module_name(self) -> str:
            """返回模块名称（用于内部标识）"""
            pass
        
        @abstractmethod
        def get_display_name(self) -> str:
            """返回显示名称（用于 UI 显示）"""
            pass
        
        @abstractmethod
        def get_icon(self) -> QIcon:
            """返回模块图标"""
            pass
        
        def on_activate(self) -> None:
            """模块被激活时调用（切换到此模块）"""
            pass
        
        def on_deactivate(self) -> None:
            """模块被停用时调用（切换到其他模块）"""
            pass
        
        def load_config(self) -> dict:
            """加载模块配置
            
            Returns:
                模块配置字典
            """
            return self.config_manager.get_module_config(self.get_module_name())
        
        def save_config(self, config: dict) -> None:
            """保存模块配置
            
            Args:
                config: 模块配置字典
            """
            self.config_manager.set_module_config(self.get_module_name(), config)
        
        def get_occupied_resources(self) -> list[str]:
            """返回当前占用的资源列表
            
            Returns:
                资源标识符列表（如串口路径、网络端口等）
            """
            return []
        
        def stop(self) -> None:
            """停止模块运行"""
            self._is_running = False
        
        def is_running(self) -> bool:
            """返回模块是否正在运行"""
            return self._is_running
        
        def log(self, level: str, message: str) -> None:
            """记录日志
            
            Args:
                level: 日志级别（DEBUG, INFO, WARNING, ERROR）
                message: 日志消息
            """
            self.log_manager.log(level, self.get_module_name(), message)
            self.log_message.emit(level, message)
        
        def log_info(self, message: str) -> None:
            """记录 INFO 级别日志"""
            self.log("INFO", message)
        
        def log_warning(self, message: str) -> None:
            """记录 WARNING 级别日志"""
            self.log("WARNING", message)
        
        def log_error(self, message: str) -> None:
            """记录 ERROR 级别日志"""
            self.log("ERROR", message)
        
        def log_debug(self, message: str) -> None:
            """记录 DEBUG 级别日志"""
            self.log("DEBUG", message)

except ImportError:
    # tkinter 备选实现（仅在 PyQt6 不可用时使用）
    try:
        import tkinter as tk
        from tkinter import ttk
        
        class BaseModule(ttk.Frame, ABC):  # type: ignore
            """模块基类（tkinter 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: tk.Widget | None = None
        ):
            """初始化模块
            
            Args:
                config_manager: 配置管理器
                log_manager: 日志管理器
                parent: 父窗口
            """
            super().__init__(parent)
            self.config_manager = config_manager
            self.log_manager = log_manager
            self._is_running = False
            self._status_callbacks: list = []
            self._log_callbacks: list = []
        
        @abstractmethod
        def get_module_name(self) -> str:
            """返回模块名称（用于内部标识）"""
            pass
        
        @abstractmethod
        def get_display_name(self) -> str:
            """返回显示名称（用于 UI 显示）"""
            pass
        
        def get_icon(self) -> str:
            """返回模块图标（tkinter 使用文本）"""
            return "📦"
        
        def on_activate(self) -> None:
            """模块被激活时调用（切换到此模块）"""
            pass
        
        def on_deactivate(self) -> None:
            """模块被停用时调用（切换到其他模块）"""
            pass
        
        def load_config(self) -> dict:
            """加载模块配置"""
            return self.config_manager.get_module_config(self.get_module_name())
        
        def save_config(self, config: dict) -> None:
            """保存模块配置"""
            self.config_manager.set_module_config(self.get_module_name(), config)
        
        def get_occupied_resources(self) -> list[str]:
            """返回当前占用的资源列表"""
            return []
        
        def stop(self) -> None:
            """停止模块运行"""
            self._is_running = False
        
        def is_running(self) -> bool:
            """返回模块是否正在运行"""
            return self._is_running
        
        def log(self, level: str, message: str) -> None:
            """记录日志"""
            self.log_manager.log(level, self.get_module_name(), message)
            for callback in self._log_callbacks:
                callback(level, message)
        
        def log_info(self, message: str) -> None:
            """记录 INFO 级别日志"""
            self.log("INFO", message)
        
        def log_warning(self, message: str) -> None:
            """记录 WARNING 级别日志"""
            self.log("WARNING", message)
        
        def log_error(self, message: str) -> None:
            """记录 ERROR 级别日志"""
            self.log("ERROR", message)
        
        def log_debug(self, message: str) -> None:
            """记录 DEBUG 级别日志"""
            self.log("DEBUG", message)
        
        def add_status_callback(self, callback) -> None:
            """添加状态变化回调"""
            if callback not in self._status_callbacks:
                self._status_callbacks.append(callback)
        
        def add_log_callback(self, callback) -> None:
            """添加日志回调"""
            if callback not in self._log_callbacks:
                self._log_callbacks.append(callback)
    
    except ImportError as e:
        # 如果 tkinter 也不可用，抛出错误
        raise ImportError(
            "Neither PyQt6 nor tkinter is available. "
            "Please install PyQt6: pip install PyQt6"
        ) from e
