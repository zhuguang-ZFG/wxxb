"""模块容器"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

from linktunnel.unified_gui.core.base_module import BaseModule

try:
    from PyQt6.QtWidgets import QStackedWidget, QWidget
    
    class ModuleContainer(QStackedWidget):
        """模块容器（PyQt6 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: QWidget | None = None
        ):
            super().__init__(parent)
            self.config_manager = config_manager
            self.log_manager = log_manager
            self._modules: dict[str, BaseModule] = {}
        
        def register_module(self, module: BaseModule) -> None:
            """注册功能模块"""
            name = module.get_module_name()
            self._modules[name] = module
            self.addWidget(module)
        
        def show_module(self, name: str) -> None:
            """显示指定模块（优化切换性能）"""
            if name in self._modules:
                # 获取当前模块
                current = self.get_active_module()
                target_module = self._modules[name]
                
                # 如果是同一个模块，不需要切换
                if current == target_module:
                    return
                
                # 使用 QTimer 延迟停用当前模块，避免阻塞 UI
                if current:
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, current.on_deactivate)
                
                # 立即切换显示
                self.setCurrentWidget(target_module)
                
                # 延迟激活新模块
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, target_module.on_activate)
        
        def get_active_module(self) -> BaseModule | None:
            """获取当前活动模块"""
            widget = self.currentWidget()
            if isinstance(widget, BaseModule):
                return widget
            return None
        
        def stop_all_modules(self) -> None:
            """停止所有运行中的模块"""
            for module in self._modules.values():
                if module.is_running():
                    module.stop()
        
        def get_all_occupied_resources(self) -> dict[str, list[str]]:
            """获取所有模块占用的资源"""
            resources = {}
            for name, module in self._modules.items():
                occupied = module.get_occupied_resources()
                if occupied:
                    resources[name] = occupied
            return resources

except ImportError:
    import tkinter as tk
    from tkinter import ttk
    
    class ModuleContainer(ttk.Frame):  # type: ignore
        """模块容器（tkinter 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: tk.Widget | None = None
        ):
            super().__init__(parent)
            self.config_manager = config_manager
            self.log_manager = log_manager
            self._modules: dict[str, BaseModule] = {}
            self._current_module: BaseModule | None = None
        
        def register_module(self, module: BaseModule) -> None:
            """注册功能模块"""
            name = module.get_module_name()
            self._modules[name] = module
        
        def show_module(self, name: str) -> None:
            """显示指定模块"""
            if name in self._modules:
                # 隐藏当前模块
                if self._current_module:
                    self._current_module.pack_forget()
                    self._current_module.on_deactivate()
                
                # 显示新模块
                module = self._modules[name]
                module.pack(fill=tk.BOTH, expand=True)
                module.on_activate()
                self._current_module = module
        
        def get_active_module(self) -> BaseModule | None:
            """获取当前活动模块"""
            return self._current_module
        
        def stop_all_modules(self) -> None:
            """停止所有运行中的模块"""
            for module in self._modules.values():
                if module.is_running():
                    module.stop()
