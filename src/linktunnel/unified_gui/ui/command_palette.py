"""智能命令面板 - 快速访问所有功能"""

from __future__ import annotations

try:
    from PyQt6.QtCore import pyqtSignal, Qt, QTimer
    from PyQt6.QtGui import QFont, QIcon
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
        QLabel, QAbstractItemView
    )
    
    class CommandPalette(QDialog):
        """智能命令面板"""
        
        command_executed = pyqtSignal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("命令面板")
            self.setMinimumWidth(600)
            self.setMinimumHeight(400)
            self.setModal(True)
            
            self.commands = {}
            self.recent_commands = []
            self._setup_ui()
            self._register_default_commands()
        
        def _setup_ui(self):
            """设置 UI"""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(12)
            
            # 搜索框
            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("输入命令或功能名称... (Ctrl+K)")
            self.search_box.setMinimumHeight(40)
            self.search_box.textChanged.connect(self._on_search_changed)
            self.search_box.returnPressed.connect(self._execute_selected)
            
            search_font = QFont()
            search_font.setPointSize(12)
            self.search_box.setFont(search_font)
            
            self.search_box.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #2196F3;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 2px solid #1976D2;
                }
            """)
            layout.addWidget(self.search_box)
            
            # 命令列表
            self.command_list = QListWidget()
            self.command_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.command_list.itemDoubleClicked.connect(self._execute_selected)
            self.command_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                }
                QListWidget::item:selected {
                    background-color: #2196F3;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #e3f2fd;
                }
            """)
            layout.addWidget(self.command_list, stretch=1)
            
            # 提示文本
            hint = QLabel("按 Enter 执行选中命令，按 Esc 关闭")
            hint.setStyleSheet("color: gray; font-size: 11px;")
            layout.addWidget(hint)
            
            # 搜索延迟定时器
            self._search_timer = QTimer()
            self._search_timer.timeout.connect(self._perform_search)
        
        def register_command(self, name: str, description: str, callback, category: str = "通用"):
            """注册命令"""
            self.commands[name] = {
                "description": description,
                "callback": callback,
                "category": category,
                "usage_count": 0
            }
        
        def _register_default_commands(self):
            """注册默认命令"""
            self.register_command(
                "切换主题",
                "在浅色和深色主题之间切换",
                lambda: self.command_executed.emit("toggle_theme"),
                "视图"
            )
            
            self.register_command(
                "打开设置",
                "打开应用程序设置",
                lambda: self.command_executed.emit("open_settings"),
                "工具"
            )
            
            self.register_command(
                "显示帮助",
                "显示用户手册和快捷键",
                lambda: self.command_executed.emit("show_help"),
                "帮助"
            )
            
            self.register_command(
                "清空日志",
                "清空日志查看器中的所有日志",
                lambda: self.command_executed.emit("clear_logs"),
                "工具"
            )
            
            self.register_command(
                "刷新模块",
                "刷新当前模块",
                lambda: self.command_executed.emit("refresh_module"),
                "模块"
            )
            
            self.register_command(
                "关于",
                "显示关于对话框",
                lambda: self.command_executed.emit("show_about"),
                "帮助"
            )
        
        def _on_search_changed(self, text: str):
            """搜索文本变化"""
            self._search_timer.stop()
            if text:
                self._search_timer.start(200)  # 200ms 延迟
            else:
                self._show_recent_commands()
        
        def _perform_search(self):
            """执行搜索"""
            search_text = self.search_box.text().lower()
            self.command_list.clear()
            
            # 搜索匹配的命令
            matches = []
            for name, cmd_info in self.commands.items():
                if (search_text in name.lower() or
                    search_text in cmd_info["description"].lower()):
                    matches.append((name, cmd_info))
            
            # 按使用频率排序
            matches.sort(key=lambda x: x[1]["usage_count"], reverse=True)
            
            # 显示匹配的命令
            for name, cmd_info in matches:
                item = QListWidgetItem()
                item.setText(f"{name}\n{cmd_info['description']}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.command_list.addItem(item)
            
            # 选中第一项
            if self.command_list.count() > 0:
                self.command_list.setCurrentRow(0)
        
        def _show_recent_commands(self):
            """显示最近使用的命令"""
            self.command_list.clear()
            
            # 显示最近使用的命令
            recent = sorted(
                self.commands.items(),
                key=lambda x: x[1]["usage_count"],
                reverse=True
            )[:10]
            
            for name, cmd_info in recent:
                item = QListWidgetItem()
                item.setText(f"{name}\n{cmd_info['description']}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.command_list.addItem(item)
        
        def _execute_selected(self):
            """执行选中的命令"""
            current_item = self.command_list.currentItem()
            if current_item:
                command_name = current_item.data(Qt.ItemDataRole.UserRole)
                if command_name in self.commands:
                    cmd_info = self.commands[command_name]
                    cmd_info["usage_count"] += 1
                    cmd_info["callback"]()
                    self.close()
        
        def keyPressEvent(self, event):
            """键盘事件"""
            if event.key() == Qt.Key.Key_Escape:
                self.close()
            elif event.key() == Qt.Key.Key_Up:
                current_row = self.command_list.currentRow()
                if current_row > 0:
                    self.command_list.setCurrentRow(current_row - 1)
            elif event.key() == Qt.Key.Key_Down:
                current_row = self.command_list.currentRow()
                if current_row < self.command_list.count() - 1:
                    self.command_list.setCurrentRow(current_row + 1)
            else:
                super().keyPressEvent(event)

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk
    
    class CommandPalette(tk.Toplevel):
        """智能命令面板（tkinter 版本）"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.title("命令面板")
            self.geometry("600x400")
            self.commands = {}
            self._setup_ui()
        
        def _setup_ui(self):
            """设置 UI"""
            # 搜索框
            search_frame = ttk.Frame(self)
            search_frame.pack(fill=tk.X, padx=10, pady=10)
            
            self.search_var = tk.StringVar()
            self.search_box = ttk.Entry(search_frame, textvariable=self.search_var)
            self.search_box.pack(fill=tk.X)
            self.search_box.insert(0, "输入命令...")
            
            # 命令列表
            self.command_list = tk.Listbox(self)
            self.command_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def register_command(self, name: str, description: str, callback, category: str = "通用"):
            """注册命令"""
            self.commands[name] = {
                "description": description,
                "callback": callback,
                "category": category
            }
