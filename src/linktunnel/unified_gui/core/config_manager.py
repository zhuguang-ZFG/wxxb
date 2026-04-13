"""
配置管理器

负责加载、保存和管理应用程序及各模块的配置。
"""

from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any


def get_config_dir() -> Path:
    """获取跨平台配置目录"""
    system = platform.system()
    if system == "Windows":
        import os
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux
        base = Path.home() / ".config"
    
    config_dir = base / "linktunnel" / "unified-gui"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "window": {
            "width": 1280,
            "height": 800,
            "x": 100,
            "y": 100,
            "maximized": False
        },
        "theme": "light",
        "navigation_mode": "sidebar",
        "last_active_module": "serial",
        "log_level": "INFO",
        "auto_save_interval": 60,
        "modules": {}
    }
    
    def __init__(self, config_dir: Path | None = None):
        """初始化配置管理器
        
        Args:
            config_dir: 配置目录路径，默认使用系统标准路径
        """
        self.config_dir = config_dir or get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self._config: dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> dict[str, Any]:
        """加载配置文件
        
        Returns:
            配置字典
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # 合并默认配置和加载的配置
                    self._config = self._merge_config(self.DEFAULT_CONFIG.copy(), loaded)
            except (json.JSONDecodeError, OSError) as e:
                print(f"警告: 配置文件损坏，使用默认配置: {e}")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
        
        return self._config
    
    def save_config(self, config: dict[str, Any] | None = None) -> None:
        """保存配置到文件
        
        Args:
            config: 要保存的配置，默认保存当前配置
        """
        if config is not None:
            self._config = config
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"错误: 无法保存配置文件: {e}")
    
    def get_module_config(self, module_name: str) -> dict[str, Any]:
        """获取模块配置
        
        Args:
            module_name: 模块名称
            
        Returns:
            模块配置字典
        """
        return self._config.get("modules", {}).get(module_name, {})
    
    def set_module_config(self, module_name: str, config: dict[str, Any]) -> None:
        """设置模块配置
        
        Args:
            module_name: 模块名称
            config: 模块配置字典
        """
        if "modules" not in self._config:
            self._config["modules"] = {}
        self._config["modules"][module_name] = config
        self.save_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键（如 "window.width"）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键（如 "window.width"）
            value: 配置值
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def export_config(self, filepath: str) -> None:
        """导出配置到文件
        
        Args:
            filepath: 导出文件路径
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise Exception(f"无法导出配置: {e}")
    
    def import_config(self, filepath: str) -> None:
        """从文件导入配置
        
        Args:
            filepath: 导入文件路径
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                imported = json.load(f)
                self._config = self._merge_config(self.DEFAULT_CONFIG.copy(), imported)
                self.save_config()
        except (json.JSONDecodeError, OSError) as e:
            raise Exception(f"无法导入配置: {e}")
    
    def reset_to_default(self) -> None:
        """恢复默认配置"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save_config()
    
    @staticmethod
    def _merge_config(base: dict, override: dict) -> dict:
        """递归合并配置字典
        
        Args:
            base: 基础配置
            override: 覆盖配置
            
        Returns:
            合并后的配置
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_config(result[key], value)
            else:
                result[key] = value
        return result
