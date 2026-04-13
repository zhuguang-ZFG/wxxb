"""增强的代理管理模块 - 支持节点验证和自动更新"""

from __future__ import annotations

import queue
import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

from linktunnel.unified_gui.core.base_module import BaseModule

try:
    from PyQt6.QtCore import QTimer, pyqtSignal
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QMessageBox,
    )
    
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

if PYQT_AVAILABLE:
    from linktunnel.proxy.node_manager import ProxyNodeManager


class NodeManagementDialog(QDialog):
    """节点管理对话框"""
    
    def __init__(self, node_manager: ProxyNodeManager, parent=None):
        super().__init__(parent)
        self.node_manager = node_manager
        self.setWindowTitle("节点管理")
        self.setGeometry(100, 100, 800, 600)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 添加节点
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("节点名称:"))
        self._name_entry = QLineEdit()
        add_layout.addWidget(self._name_entry)
        
        add_layout.addWidget(QLabel("订阅 URL:"))
        self._url_entry = QLineEdit()
        add_layout.addWidget(self._url_entry)
        
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self._on_add_node)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # 从 GitHub 拉取
        github_layout = QHBoxLayout()
        github_layout.addWidget(QLabel("GitHub 仓库 (owner/repo):"))
        self._github_entry = QLineEdit()
        self._github_entry.setPlaceholderText("例如: user/proxy-nodes")
        github_layout.addWidget(self._github_entry)
        
        github_btn = QPushButton("从 GitHub 拉取")
        github_btn.clicked.connect(self._on_fetch_github)
        github_layout.addWidget(github_btn)
        
        layout.addLayout(github_layout)
        
        # 从订阅 URL 拉取
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(QLabel("订阅 URL:"))
        self._sub_url_entry = QLineEdit()
        self._sub_url_entry.setPlaceholderText("例如: https://...")
        sub_layout.addWidget(self._sub_url_entry)
        
        sub_btn = QPushButton("从订阅拉取")
        sub_btn.clicked.connect(self._on_fetch_subscription)
        sub_layout.addWidget(sub_btn)
        
        layout.addLayout(sub_layout)
        
        # 从 GitHub 热点拉取
        hotspot_layout = QHBoxLayout()
        hotspot_layout.addWidget(QLabel("搜索关键词:"))
        self._hotspot_keyword = QLineEdit()
        self._hotspot_keyword.setText("proxy")
        self._hotspot_keyword.setMaximumWidth(100)
        hotspot_layout.addWidget(self._hotspot_keyword)
        
        hotspot_layout.addWidget(QLabel("语言:"))
        self._hotspot_lang = QComboBox()
        self._hotspot_lang.addItems(["python", "go", "rust", "javascript", "all"])
        self._hotspot_lang.setMaximumWidth(100)
        hotspot_layout.addWidget(self._hotspot_lang)
        
        hotspot_btn = QPushButton("从 GitHub 热点拉取")
        hotspot_btn.clicked.connect(self._on_fetch_hotspot)
        hotspot_layout.addWidget(hotspot_btn)
        
        hotspot_layout.addStretch()
        layout.addLayout(hotspot_layout)
        
        # 节点列表
        layout.addWidget(QLabel("节点列表:"))
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["节点名称", "来源", "状态", "最后检查"])
        self._tree.setColumnCount(4)
        layout.addWidget(self._tree)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        verify_btn = QPushButton("验证选中节点")
        verify_btn.clicked.connect(self._on_verify_selected)
        btn_layout.addWidget(verify_btn)
        
        verify_all_btn = QPushButton("验证所有节点")
        verify_all_btn.clicked.connect(self._on_verify_all)
        btn_layout.addWidget(verify_all_btn)
        
        cleanup_btn = QPushButton("清除失效节点")
        cleanup_btn.clicked.connect(self._on_cleanup)
        btn_layout.addWidget(cleanup_btn)
        
        remove_btn = QPushButton("删除选中节点")
        remove_btn.clicked.connect(self._on_remove_selected)
        btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 刷新列表
        self._refresh_tree()
    
    def _refresh_tree(self) -> None:
        """刷新节点列表"""
        self._tree.clear()
        
        nodes = self.node_manager.get_nodes()
        status = self.node_manager.get_status()
        
        for name, info in nodes.items():
            node_status = status.get(name, {})
            valid = node_status.get("valid")
            last_check = node_status.get("last_check", "—")
            
            status_text = "✓ 有效" if valid is True else ("✗ 失效" if valid is False else "? 未检查")
            
            item = QTreeWidgetItem([
                name,
                info.get("source", "—"),
                status_text,
                last_check[:10] if last_check != "—" else "—",
            ])
            self._tree.addTopLevelItem(item)
        
        # 调整列宽
        for i in range(4):
            self._tree.resizeColumnToContents(i)
    
    def _on_add_node(self) -> None:
        """添加节点"""
        name = self._name_entry.text().strip()
        url = self._url_entry.text().strip()
        
        if not name or not url:
            QMessageBox.warning(self, "错误", "请填写节点名称和 URL")
            return
        
        if self.node_manager.add_node(name, url):
            QMessageBox.information(self, "成功", f"已添加节点: {name}")
            self._name_entry.clear()
            self._url_entry.clear()
            self._refresh_tree()
        else:
            QMessageBox.warning(self, "错误", f"节点 {name} 已存在")
    
    def _on_fetch_github(self) -> None:
        """从 GitHub 拉取"""
        repo = self._github_entry.text().strip()
        
        if not repo:
            QMessageBox.warning(self, "错误", "请填写 GitHub 仓库")
            return
        
        new_nodes = self.node_manager.fetch_from_github(repo)
        QMessageBox.information(self, "成功", f"已拉取 {len(new_nodes)} 个新节点")
        self._refresh_tree()
    
    def _on_fetch_subscription(self) -> None:
        """从订阅拉取"""
        url = self._sub_url_entry.text().strip()
        
        if not url:
            QMessageBox.warning(self, "错误", "请填写订阅 URL")
            return
        
        new_nodes = self.node_manager.fetch_from_subscription(url)
        QMessageBox.information(self, "成功", f"已拉取 {len(new_nodes)} 个新节点")
        self._refresh_tree()
    
    def _on_fetch_hotspot(self) -> None:
        """从 GitHub 热点拉取"""
        keyword = self._hotspot_keyword.text().strip() or "proxy"
        language = self._hotspot_lang.currentText()
        
        def fetch_worker() -> None:
            new_nodes = self.node_manager.fetch_from_github_hotspot(keyword, language)
            QMessageBox.information(self, "成功", f"已拉取 {len(new_nodes)} 个新节点")
            self._refresh_tree()
        
        threading.Thread(target=fetch_worker, daemon=True).start()
        QMessageBox.information(self, "提示", "正在后台拉取 GitHub 热点节点...")
    
    def _on_verify_selected(self) -> None:
        """验证选中节点"""
        selected = self._tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "错误", "请先选中一个节点")
            return
        
        item = selected[0]
        name = item.text(0)
        
        def verify_worker() -> None:
            self.node_manager.verify_node(name)
            self._refresh_tree()
        
        threading.Thread(target=verify_worker, daemon=True).start()
    
    def _on_verify_all(self) -> None:
        """验证所有节点"""
        def verify_worker() -> None:
            self.node_manager.verify_all_nodes()
            self._refresh_tree()
        
        threading.Thread(target=verify_worker, daemon=True).start()
        QMessageBox.information(self, "提示", "正在后台验证所有节点...")
    
    def _on_cleanup(self) -> None:
        """清除失效节点"""
        removed = self.node_manager.cleanup_invalid_nodes()
        QMessageBox.information(self, "成功", f"已清除 {len(removed)} 个失效节点")
        self._refresh_tree()
    
    def _on_remove_selected(self) -> None:
        """删除选中节点"""
        selected = self._tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "错误", "请先选中一个节点")
            return
        
        item = selected[0]
        name = item.text(0)
        
        reply = QMessageBox.question(self, "确认", f"确定要删除节点 {name} 吗?")
        if reply == QMessageBox.StandardButton.Yes:
            self.node_manager.remove_node(name)
            self._refresh_tree()


if PYQT_AVAILABLE:
    class ProxyModuleEnhanced(BaseModule):
        """增强的代理管理模块"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent=None
        ):
            super().__init__(config_manager, log_manager, parent)
            
            # 初始化节点管理器
            self.node_manager = ProxyNodeManager()
            
            # 创建 UI
            self._setup_ui()
            
            # 启动每日更新任务
            self.node_manager.schedule_daily_update(self._on_update_complete)
        
        def _setup_ui(self) -> None:
            """设置 UI"""
            layout = QVBoxLayout(self)
            
            # 节点管理按钮
            btn_layout = QHBoxLayout()
            
            manage_btn = QPushButton("节点管理")
            manage_btn.clicked.connect(self._on_manage_nodes)
            btn_layout.addWidget(manage_btn)
            
            verify_btn = QPushButton("验证所有节点")
            verify_btn.clicked.connect(self._on_verify_all)
            btn_layout.addWidget(verify_btn)
            
            cleanup_btn = QPushButton("清除失效节点")
            cleanup_btn.clicked.connect(self._on_cleanup)
            btn_layout.addWidget(cleanup_btn)
            
            hotspot_btn = QPushButton("拉取 GitHub 热点节点")
            hotspot_btn.clicked.connect(self._on_fetch_hotspot_nodes)
            btn_layout.addWidget(hotspot_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            # 自动更新选项
            auto_layout = QHBoxLayout()
            self._auto_update_cb = QCheckBox("启用每日自动更新")
            self._auto_update_cb.setChecked(True)
            auto_layout.addWidget(self._auto_update_cb)
            
            auto_layout.addWidget(QLabel("更新时间:"))
            self._update_time_combo = QComboBox()
            self._update_time_combo.addItems(["02:00", "03:00", "04:00", "05:00"])
            self._update_time_combo.setCurrentText("02:00")
            auto_layout.addWidget(self._update_time_combo)
            
            self._auto_hotspot_cb = QCheckBox("启用每日自动拉取热点节点")
            self._auto_hotspot_cb.setChecked(True)
            auto_layout.addWidget(self._auto_hotspot_cb)
            
            auto_layout.addStretch()
            layout.addLayout(auto_layout)
            
            # 节点统计
            stats_layout = QHBoxLayout()
            stats_layout.addWidget(QLabel("节点统计:"))
            
            self._total_label = QLabel("总数: 0")
            stats_layout.addWidget(self._total_label)
            
            self._valid_label = QLabel("有效: 0")
            stats_layout.addWidget(self._valid_label)
            
            self._invalid_label = QLabel("失效: 0")
            stats_layout.addWidget(self._invalid_label)
            
            stats_layout.addStretch()
            layout.addLayout(stats_layout)
            
            # 日志
            layout.addWidget(QLabel("更新日志:"))
            self._log_text = QTextEdit()
            self._log_text.setReadOnly(True)
            self._log_text.setMaximumHeight(200)
            layout.addWidget(self._log_text)
            
            layout.addStretch()
            
            # 更新统计
            self._update_stats()
        
        def _update_stats(self) -> None:
            """更新统计信息"""
            nodes = self.node_manager.get_nodes()
            valid_nodes = self.node_manager.get_valid_nodes()
            invalid_nodes = self.node_manager.get_invalid_nodes()
            
            self._total_label.setText(f"总数: {len(nodes)}")
            self._valid_label.setText(f"有效: {len(valid_nodes)}")
            self._invalid_label.setText(f"失效: {len(invalid_nodes)}")
        
        def _on_manage_nodes(self) -> None:
            """打开节点管理对话框"""
            dialog = NodeManagementDialog(self.node_manager, self)
            dialog.exec()
            self._update_stats()
        
        def _on_verify_all(self) -> None:
            """验证所有节点"""
            def verify_worker() -> None:
                self.log_info("正在验证所有节点...")
                results = self.node_manager.verify_all_nodes()
                valid_count = sum(1 for v in results.values() if v)
                self.log_info(f"验证完成: {valid_count}/{len(results)} 个节点有效")
                self._update_stats()
            
            threading.Thread(target=verify_worker, daemon=True).start()
        
        def _on_cleanup(self) -> None:
            """清除失效节点"""
            removed = self.node_manager.cleanup_invalid_nodes()
            self.log_info(f"已清除 {len(removed)} 个失效节点")
            self._update_stats()
        
        def _on_fetch_hotspot_nodes(self) -> None:
            """拉取 GitHub 热点节点"""
            def fetch_worker() -> None:
                self.log_info("正在拉取 GitHub 热点节点...")
                result = self.node_manager.auto_fetch_hotspot_nodes()
                msg = f"拉取完成: {result['repos']} 个仓库, {result['nodes']} 个新节点"
                self._log_text.append(msg)
                self.log_info(msg)
                self._update_stats()
            
            threading.Thread(target=fetch_worker, daemon=True).start()
        
        def _on_update_complete(self, result: dict[str, Any]) -> None:
            """每日更新完成回调"""
            msg = f"每日更新完成: 验证 {result['verified']} 个节点, 清除 {result['removed']} 个失效节点"
            self._log_text.append(msg)
            self.log_info(msg)
            self._update_stats()
        
        def get_module_name(self) -> str:
            return "proxy_enhanced"
        
        def get_display_name(self) -> str:
            return "代理管理 (增强)"
        
        def get_icon(self) -> QIcon:
            return QIcon()
        
        def stop(self) -> None:
            """停止模块"""
            super().stop()
            self.log_info("代理管理模块已停止")
