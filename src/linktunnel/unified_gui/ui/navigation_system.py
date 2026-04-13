"""导航系统 UI 组件"""

from __future__ import annotations

try:
    from PyQt6.QtCore import pyqtSignal, Qt
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
    
    class NavigationSystem(QWidget):
        """导航系统（PyQt6 侧边栏版本）"""
        
        module_changed = pyqtSignal(str)  # 模块切换信号
        
        def __init__(self, parent: QWidget | None = None):
            super().__init__(parent)
            self._setup_ui()
            self._modules: dict[str, QListWidgetItem] = {}
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.list_widget = QListWidget()
            self.list_widget.currentItemChanged.connect(self._on_item_changed)
            layout.addWidget(self.list_widget)
        
        def add_module(self, name: str, display_name: str, icon: QIcon) -> None:
            """添加模块到导航"""
            item = QListWidgetItem(icon, display_name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)
            self._modules[name] = item
        
        def set_active_module(self, name: str) -> None:
            """设置当前活动模块"""
            if name in self._modules:
                self.list_widget.setCurrentItem(self._modules[name])
        
        def _on_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
            """列表项变化"""
            if current:
                name = current.data(Qt.ItemDataRole.UserRole)
                self.module_changed.emit(name)

except ImportError:
    import tkinter as tk
    from tkinter import ttk
    
    class NavigationSystem(ttk.Frame):  # type: ignore
        """导航系统（tkinter 版本）"""
        
        def __init__(self, parent: tk.Widget | None = None):
            super().__init__(parent)
            self._setup_ui()
            self._modules: dict[str, int] = {}
            self._callbacks: list = []
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            self.listbox = tk.Listbox(self, width=20)
            self.listbox.pack(fill=tk.BOTH, expand=True)
            self.listbox.bind("<<ListboxSelect>>", self._on_select)
        
        def add_module(self, name: str, display_name: str, icon: str = "") -> None:
            """添加模块到导航"""
            idx = self.listbox.size()
            self.listbox.insert(tk.END, f"{icon} {display_name}")
            self._modules[name] = idx
        
        def set_active_module(self, name: str) -> None:
            """设置当前活动模块"""
            if name in self._modules:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(self._modules[name])
        
        def _on_select(self, event) -> None:
            """选择变化"""
            selection = self.listbox.curselection()
            if selection:
                idx = selection[0]
                for name, module_idx in self._modules.items():
                    if module_idx == idx:
                        for callback in self._callbacks:
                            callback(name)
                        break
        
        def add_callback(self, callback) -> None:
            """添加模块切换回调"""
            if callback not in self._callbacks:
                self._callbacks.append(callback)
