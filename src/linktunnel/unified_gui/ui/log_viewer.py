"""
日志查看器 UI 组件
"""

from __future__ import annotations

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
    from PyQt6.QtWidgets import (
        QComboBox,
        QHBoxLayout,
        QLineEdit,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    
    class LogViewer(QWidget):
        """日志查看器（PyQt6 版本）"""
        
        LEVEL_COLORS = {
            "DEBUG": QColor(128, 128, 128),
            "INFO": QColor(0, 0, 0),
            "WARNING": QColor(255, 140, 0),
            "ERROR": QColor(255, 0, 0),
        }
        
        def __init__(self, parent: QWidget | None = None):
            super().__init__(parent)
            self.max_lines = 5000  # 减少最大行数以提高性能
            self.current_filter_level = "DEBUG"
            self._log_buffer = []  # 日志缓冲区
            self._buffer_size = 100  # 批量处理大小
            self._update_timer = None  # 延迟更新定时器
            self._setup_ui()
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            
            # 工具栏
            toolbar = QHBoxLayout()
            
            # 日志级别过滤
            self.level_combo = QComboBox()
            self.level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
            self.level_combo.setCurrentText("DEBUG")
            self.level_combo.currentTextChanged.connect(self._on_filter_level_changed)
            toolbar.addWidget(self.level_combo)
            
            # 搜索框
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("搜索日志...")
            self.search_input.textChanged.connect(self._on_search)
            toolbar.addWidget(self.search_input)
            
            # 清空按钮
            clear_btn = QPushButton("清空")
            clear_btn.clicked.connect(self.clear)
            toolbar.addWidget(clear_btn)
            
            # 导出按钮
            export_btn = QPushButton("导出")
            export_btn.clicked.connect(self._on_export)
            toolbar.addWidget(clear_btn)
            export_btn.clicked.connect(self._on_export)
            toolbar.addWidget(export_btn)
            
            layout.addLayout(toolbar)
            
            # 日志显示区域
            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            layout.addWidget(self.log_text)
        
        def append_log(self, level: str, module: str, message: str) -> None:
            """添加日志条目（使用批量处理优化性能）"""
            # 检查级别过滤
            if not self._should_show_level(level):
                return
            
            # 添加到缓冲区
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self._log_buffer.append((timestamp, level, module, message))
            
            # 如果缓冲区达到阈值，立即刷新
            if len(self._log_buffer) >= self._buffer_size:
                self._flush_log_buffer()
            else:
                # 否则延迟刷新（100ms）
                if self._update_timer is None:
                    from PyQt6.QtCore import QTimer
                    self._update_timer = QTimer()
                    self._update_timer.setSingleShot(True)
                    self._update_timer.timeout.connect(self._flush_log_buffer)
                
                if not self._update_timer.isActive():
                    self._update_timer.start(100)
        
        def _flush_log_buffer(self) -> None:
            """刷新日志缓冲区到显示区域"""
            if not self._log_buffer:
                return
            
            # 检查行数限制（批量删除旧日志）
            current_lines = self.log_text.document().lineCount()
            if current_lines > self.max_lines:
                cursor = self.log_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                # 删除超出部分的一半，避免频繁删除
                lines_to_remove = min(current_lines - self.max_lines + 1000, current_lines // 2)
                cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor, lines_to_remove)
                cursor.removeSelectedText()
            
            # 批量插入日志
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            
            # 暂时禁用自动滚动以提高性能
            scrollbar = self.log_text.verticalScrollBar()
            at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
            
            for timestamp, level, module, message in self._log_buffer:
                log_line = f"[{timestamp}] [{level}] [{module}] {message}\n"
                
                fmt = QTextCharFormat()
                fmt.setForeground(self.LEVEL_COLORS.get(level, QColor(0, 0, 0)))
                cursor.setCharFormat(fmt)
                cursor.insertText(log_line)
            
            # 只有在底部时才自动滚动
            if at_bottom:
                self.log_text.setTextCursor(cursor)
                self.log_text.ensureCursorVisible()
            
            # 清空缓冲区
            self._log_buffer.clear()
        
        def _should_show_level(self, level: str) -> bool:
            """检查是否应该显示该级别的日志"""
            levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            try:
                current_idx = levels.index(self.current_filter_level)
                level_idx = levels.index(level)
                return level_idx >= current_idx
            except ValueError:
                return True
        
        def _on_filter_level_changed(self, level: str) -> None:
            """日志级别过滤变化"""
            self.current_filter_level = level
        
        def _on_search(self, keyword: str) -> None:
            """搜索日志"""
            if not keyword:
                # 清除高亮
                cursor = self.log_text.textCursor()
                cursor.clearSelection()
                self.log_text.setTextCursor(cursor)
                return
            
            # 高亮搜索结果
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.log_text.setTextCursor(cursor)
            self.log_text.find(keyword)
        
        def clear(self) -> None:
            """清空日志"""
            self._log_buffer.clear()
            if self._update_timer and self._update_timer.isActive():
                self._update_timer.stop()
            self.log_text.clear()
        
        def _on_export(self) -> None:
            """导出日志到文件"""
            from PyQt6.QtWidgets import QFileDialog
            filepath, _ = QFileDialog.getSaveFileName(
                self, "导出日志", "", "文本文件 (*.txt);;所有文件 (*)"
            )
            if filepath:
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(self.log_text.toPlainText())
                except Exception as e:
                    print(f"导出失败: {e}")

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import scrolledtext, ttk
    
    class LogViewer(ttk.Frame):  # type: ignore
        """日志查看器（tkinter 版本）"""
        
        def __init__(self, parent: tk.Widget | None = None):
            super().__init__(parent)
            self.max_lines = 10000
            self.current_filter_level = "DEBUG"
            self._setup_ui()
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            # 工具栏
            toolbar = ttk.Frame(self)
            toolbar.pack(fill=tk.X, padx=5, pady=5)
            
            # 日志级别过滤
            ttk.Label(toolbar, text="级别:").pack(side=tk.LEFT)
            self.level_var = tk.StringVar(value="DEBUG")
            level_combo = ttk.Combobox(
                toolbar,
                textvariable=self.level_var,
                values=["DEBUG", "INFO", "WARNING", "ERROR"],
                state="readonly",
                width=10
            )
            level_combo.pack(side=tk.LEFT, padx=5)
            
            # 清空按钮
            ttk.Button(toolbar, text="清空", command=self.clear).pack(side=tk.LEFT, padx=5)
            
            # 日志显示区域
            self.log_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.log_text.config(state=tk.DISABLED)
        
        def append_log(self, level: str, module: str, message: str) -> None:
            """添加日志条目"""
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_line = f"[{timestamp}] [{level}] [{module}] {message}\n"
            
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_line)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        def clear(self) -> None:
            """清空日志"""
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
