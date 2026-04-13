"""
日志管理器

负责日志的格式化、过滤、文件轮转和信号发射。
"""

from __future__ import annotations

import logging
import platform
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable


def get_log_dir() -> Path:
    """获取跨平台日志目录"""
    system = platform.system()
    if system == "Windows":
        import os
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        log_dir = base / "linktunnel" / "unified-gui" / "logs"
    elif system == "Darwin":  # macOS
        log_dir = Path.home() / "Library" / "Logs" / "linktunnel" / "unified-gui"
    else:  # Linux
        log_dir = Path.home() / ".local" / "share" / "linktunnel" / "unified-gui" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


class LogManager:
    """日志管理器"""
    
    def __init__(self, log_dir: Path | None = None, log_level: str = "INFO"):
        """初始化日志管理器
        
        Args:
            log_dir: 日志目录路径，默认使用系统标准路径
            log_level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        """
        self.log_dir = log_dir or get_log_dir()
        self.log_file = self.log_dir / "unified_gui.log"
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 日志回调函数列表
        self._callbacks: list[Callable[[str, str, str], None]] = []
        
        # 配置 Python logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """配置 Python logging 系统"""
        # 创建 logger
        self.logger = logging.getLogger("linktunnel.unified_gui")
        self.logger.setLevel(self.log_level)
        
        # 清除现有 handlers
        self.logger.handlers.clear()
        
        # 文件 handler（轮转）
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=7,  # 保留 7 个备份
            encoding="utf-8"
        )
        file_handler.setLevel(self.log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 自定义 handler（用于发送信号）
        custom_handler = CallbackHandler(self._emit_log)
        custom_handler.setLevel(self.log_level)
        self.logger.addHandler(custom_handler)
    
    def _emit_log(self, level: str, module: str, message: str) -> None:
        """发射日志信号到所有回调函数
        
        Args:
            level: 日志级别
            module: 模块名称
            message: 日志消息
        """
        for callback in self._callbacks:
            try:
                callback(level, module, message)
            except Exception as e:
                print(f"日志回调错误: {e}")
    
    def add_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """添加日志回调函数
        
        Args:
            callback: 回调函数，接收 (level, module, message) 参数
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """移除日志回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def log(self, level: str, module: str, message: str) -> None:
        """记录日志
        
        Args:
            level: 日志级别（DEBUG, INFO, WARNING, ERROR）
            module: 模块名称
            message: 日志消息
        """
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(f"[{module}] {message}")
    
    def debug(self, module: str, message: str) -> None:
        """记录 DEBUG 级别日志"""
        self.log("DEBUG", module, message)
    
    def info(self, module: str, message: str) -> None:
        """记录 INFO 级别日志"""
        self.log("INFO", module, message)
    
    def warning(self, module: str, message: str) -> None:
        """记录 WARNING 级别日志"""
        self.log("WARNING", module, message)
    
    def error(self, module: str, message: str) -> None:
        """记录 ERROR 级别日志"""
        self.log("ERROR", module, message)
    
    def set_log_level(self, level: str) -> None:
        """设置日志级别
        
        Args:
            level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        """
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)
    
    def format_log_entry(self, level: str, module: str, message: str) -> dict[str, str]:
        """格式化日志条目
        
        Args:
            level: 日志级别
            module: 模块名称
            message: 日志消息
            
        Returns:
            格式化的日志条目字典
        """
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "level": level,
            "module": module,
            "message": message
        }


class CallbackHandler(logging.Handler):
    """自定义日志 Handler，用于发送日志到回调函数"""
    
    def __init__(self, callback: Callable[[str, str, str], None]):
        super().__init__()
        self.callback = callback
    
    def emit(self, record: logging.LogRecord) -> None:
        """发射日志记录"""
        try:
            # 从 record.name 提取模块名称
            # 格式: linktunnel.unified_gui.modules.serial -> serial
            parts = record.name.split(".")
            module = parts[-1] if len(parts) > 0 else "unknown"
            
            # 提取消息中的模块名称（如果有）
            message = record.getMessage()
            if message.startswith("[") and "]" in message:
                bracket_end = message.index("]")
                module = message[1:bracket_end]
                message = message[bracket_end + 1:].strip()
            
            self.callback(record.levelname, module, message)
        except Exception:
            self.handleError(record)
