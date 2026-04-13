"""现代化导航系统 - 支持搜索、快速访问、动画效果"""

from __future__ import annotations

try:
    from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QPropertyAnimation, QEasingCurve
    from PyQt6.QtGui import QIcon, QColor, QFont, QPalette
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QScrollArea,
        QPushButton, QLabel, QFrame, QGridLayout
    )
    
    class ModuleCard(QFrame):
        """模块卡片 - 现代化设计"""
        
        clicked = pyqtSignal(str)
        
        def __init__(self, name: str, display_name: str, icon: QIcon, parent=None):
            super().__init__(parent)
            self.name = name
            self.display_name = display_name
            self.icon = icon
            self.is_active = False
            
            self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setMinimumHeight(80)
            
            self._setup_ui()
            self._setup_animation()
        
        def _setup_ui(self):
            """设置卡片 UI"""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(8)
            
            # 标题
            title = QLabel(self.display_name)
            title_font = QFont()
            title_font.setPointSize(11)
            title_font.setBold(True)
            title.setFont(title_font)
            layout.addWidget(title)
            
            # 描述
            desc = QLabel(f"模块: {self.name}")
            desc_font = QFont()
            desc_font.setPointSize(9)
            desc.setFont(desc_font)
            desc.setStyleSheet("color: gray;")
            layout.addWidget(desc)
            
            layout.addStretch()
        
        def _setup_animation(self):
            """设置动画"""
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(200)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        def set_active(self, active: bool):
            """设置活动状态"""
            self.is_active = active
            self._update_style()
        
        def _update_style(self):
            """更新样式"""
            if self.is_active:
                self.setStyleSheet("""
                    ModuleCard {
                        background-color: #2196F3;
                        border-radius: 8px;
                        border: 2px solid #1976D2;
                    }
                    QLabel {
                        color: white;
                    }
                """)
            else:
                self.setStyleSheet("""
                    ModuleCard {
                        background-color: #f5f5f5;
                        border-radius: 8px;
                        border: 1px solid #e0e0e0;
                    }
                    ModuleCard:hover {
                        background-color: #eeeeee;
                        border: 1px solid #bdbdbd;
                    }
                """)
        
        def mousePressEvent(self, event):
            """鼠标点击事件"""
            self.clicked.emit(self.name)
            super().mousePressEvent(event)
    
    class ModernNavigationSystem(QWidget):
        """现代化导航系统"""
        
        module_changed = pyqtSignal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setMinimumWidth(280)
            self.setMaximumWidth(400)
            
            self._modules: dict[str, ModuleCard] = {}
            self._active_module = None
            self._search_timer = QTimer()
            self._search_timer.timeout.connect(self._perform_search)
            
            self._setup_ui()
        
        def _setup_ui(self):
            """设置 UI"""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(12)
            
            # 标题
            title = QLabel("功能模块")
            title_font = QFont()
            title_font.setPointSize(14)
            title_font.setBold(True)
            title.setFont(title_font)
            layout.addWidget(title)
            
            # 搜索框
            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("搜索模块...")
            self.search_box.setMinimumHeight(36)
            self.search_box.textChanged.connect(self._on_search_text_changed)
            self.search_box.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
            layout.addWidget(self.search_box)
            
            # 模块列表（可滚动）
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; }")
            
            self.modules_container = QWidget()
            self.modules_layout = QGridLayout(self.modules_container)
            self.modules_layout.setSpacing(8)
            self.modules_layout.setContentsMargins(0, 0, 0, 0)
            
            scroll.setWidget(self.modules_container)
            layout.addWidget(scroll, stretch=1)
            
            # 快速操作按钮
            quick_actions_label = QLabel("快速操作")
            quick_actions_label.setFont(title_font)
            layout.addWidget(quick_actions_label)
            
            quick_layout = QHBoxLayout()
            
            refresh_btn = QPushButton("刷新")
            refresh_btn.setMinimumHeight(32)
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            quick_layout.addWidget(refresh_btn)
            
            settings_btn = QPushButton("设置")
            settings_btn.setMinimumHeight(32)
            settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e68900;
                }
            """)
            quick_layout.addWidget(settings_btn)
            
            layout.addLayout(quick_layout)
        
        def add_module(self, name: str, display_name: str, icon: QIcon = None):
            """添加模块"""
            card = ModuleCard(name, display_name, icon or QIcon())
            card.clicked.connect(self._on_module_clicked)
            
            row = len(self._modules) // 2
            col = len(self._modules) % 2
            self.modules_layout.addWidget(card, row, col)
            
            self._modules[name] = card
        
        def set_active_module(self, name: str):
            """设置活动模块"""
            if self._active_module and self._active_module in self._modules:
                self._modules[self._active_module].set_active(False)
            
            if name in self._modules:
                self._modules[name].set_active(True)
                self._active_module = name
        
        def _on_module_clicked(self, name: str):
            """模块被点击"""
            self.set_active_module(name)
            self.module_changed.emit(name)
        
        def _on_search_text_changed(self, text: str):
            """搜索文本变化"""
            self._search_timer.stop()
            self._search_timer.start(300)  # 300ms 延迟搜索
        
        def _perform_search(self):
            """执行搜索"""
            search_text = self.search_box.text().lower()
            
            for name, card in self._modules.items():
                visible = (
                    search_text in name.lower() or
                    search_text in card.display_name.lower()
                )
                card.setVisible(visible)

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk
    
    class ModernNavigationSystem(ttk.Frame):
        """现代化导航系统（tkinter 版本）"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._modules = {}
            self._callbacks = []
            self._setup_ui()
        
        def _setup_ui(self):
            """设置 UI"""
            # 标题
            title = ttk.Label(self, text="功能模块", font=("Arial", 14, "bold"))
            title.pack(pady=10)
            
            # 搜索框
            search_frame = ttk.Frame(self)
            search_frame.pack(fill=tk.X, padx=10, pady=5)
            
            self.search_var = tk.StringVar()
            self.search_box = ttk.Entry(search_frame, textvariable=self.search_var)
            self.search_box.pack(fill=tk.X)
            self.search_box.insert(0, "搜索模块...")
            
            # 模块列表
            self.listbox = tk.Listbox(self, height=15)
            self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.listbox.bind("<<ListboxSelect>>", self._on_select)
        
        def add_module(self, name: str, display_name: str, icon=None):
            """添加模块"""
            idx = self.listbox.size()
            self.listbox.insert(tk.END, f"  {display_name}")
            self._modules[name] = idx
        
        def set_active_module(self, name: str):
            """设置活动模块"""
            if name in self._modules:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(self._modules[name])
        
        def _on_select(self, event):
            """选择变化"""
            selection = self.listbox.curselection()
            if selection:
                idx = selection[0]
                for name, module_idx in self._modules.items():
                    if module_idx == idx:
                        for callback in self._callbacks:
                            callback(name)
                        break
        
        def add_callback(self, callback):
            """添加回调"""
            if callback not in self._callbacks:
                self._callbacks.append(callback)
