"""BLE 蓝牙扫描模块"""

from __future__ import annotations

import asyncio
import io
import sys
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

from linktunnel.unified_gui.core.base_module import BaseModule

try:
    from PyQt6.QtCore import QTimer, pyqtSignal
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QComboBox,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
        QFileDialog,
    )
    
    class BLEModule(BaseModule):
        """BLE 蓝牙扫描模块（PyQt6 版本）"""
        
        # 信号
        scan_completed = pyqtSignal(list)  # 扫描完成信号
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: QWidget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            self._scan_thread: threading.Thread | None = None
            self._scan_results: list = []
            self._bleak_available = self._check_bleak_available()
            self._setup_ui()
        
        def get_module_name(self) -> str:
            return "ble"
        
        def get_display_name(self) -> str:
            return "BLE 蓝牙扫描"
        
        def get_icon(self) -> QIcon:
            return QIcon()  # TODO: 添加图标
        
        def _check_bleak_available(self) -> bool:
            """检测 bleak 库是否可用"""
            try:
                import bleak
                return True
            except ImportError:
                return False
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            
            # 依赖检测提示
            if not self._bleak_available:
                warning_group = QGroupBox("依赖缺失")
                warning_layout = QVBoxLayout(warning_group)
                
                warning_label = QLabel(
                    "⚠️ BLE 扫描需要安装 bleak 库\n\n"
                    "请运行以下命令安装：\n"
                    "  pip install 'linktunnel[ble]'\n\n"
                    "或者：\n"
                    "  pip install bleak"
                )
                warning_label.setStyleSheet("color: orange; padding: 10px;")
                warning_layout.addWidget(warning_label)
                
                layout.addWidget(warning_group)
                layout.addStretch()
                return
            
            # 配置区域
            config_group = QGroupBox("扫描配置")
            config_layout = QHBoxLayout(config_group)
            
            config_layout.addWidget(QLabel("扫描超时:"))
            self.timeout_combo = QComboBox()
            self.timeout_combo.addItems(["5", "10", "15", "20", "30"])
            self.timeout_combo.setCurrentText("5")
            config_layout.addWidget(self.timeout_combo)
            config_layout.addWidget(QLabel("秒"))
            
            config_layout.addStretch()
            
            # 控制按钮
            self.start_btn = QPushButton("开始扫描")
            self.start_btn.clicked.connect(self._on_start_scan)
            config_layout.addWidget(self.start_btn)
            
            self.stop_btn = QPushButton("停止")
            self.stop_btn.clicked.connect(self._on_stop_scan)
            self.stop_btn.setEnabled(False)
            config_layout.addWidget(self.stop_btn)
            
            self.export_btn = QPushButton("导出结果")
            self.export_btn.clicked.connect(self._on_export_results)
            config_layout.addWidget(self.export_btn)
            
            layout.addWidget(config_group)
            
            # 扫描结果表格
            results_group = QGroupBox("扫描结果")
            results_layout = QVBoxLayout(results_group)
            
            self.results_table = QTableWidget()
            self.results_table.setColumnCount(3)
            self.results_table.setHorizontalHeaderLabels(["设备名称", "地址", "RSSI"])
            self.results_table.setColumnWidth(0, 200)
            self.results_table.setColumnWidth(1, 200)
            self.results_table.setColumnWidth(2, 100)
            results_layout.addWidget(self.results_table)
            
            layout.addWidget(results_group)
            
            # 状态信息
            self.status_label = QLabel("状态: 就绪")
            layout.addWidget(self.status_label)
            
            # 连接信号
            self.scan_completed.connect(self._on_scan_completed)
        
        def _on_start_scan(self) -> None:
            """开始 BLE 扫描"""
            timeout = int(self.timeout_combo.currentText())
            
            self.log_info(f"开始 BLE 扫描，超时 {timeout} 秒")
            
            # 清空之前的结果
            self._scan_results.clear()
            self.results_table.setRowCount(0)
            
            # 更新 UI 状态
            self._is_running = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText(f"状态: 扫描中... (超时 {timeout} 秒)")
            
            # 在后台线程中执行扫描
            self._scan_thread = threading.Thread(
                target=self._run_scan,
                args=(timeout,),
                daemon=True
            )
            self._scan_thread.start()
        
        def _run_scan(self, timeout: int) -> None:
            """在后台线程中运行 BLE 扫描"""
            try:
                # 调用现有的 ble_scan.py 逻辑
                from linktunnel.ble_scan import run_ble_scan
                
                # 捕获输出
                output = io.StringIO()
                result_code = run_ble_scan(timeout_s=float(timeout), out=output)
                
                if result_code == 0:
                    # 解析输出
                    output_text = output.getvalue()
                    devices = self._parse_scan_output(output_text)
                    self._scan_results = devices
                    
                    # 发送完成信号
                    self.scan_completed.emit(devices)
                else:
                    self.log_error("BLE 扫描失败")
                    self.scan_completed.emit([])
                    
            except Exception as e:
                self.log_error(f"BLE 扫描异常: {e}")
                self.scan_completed.emit([])
        
        def _parse_scan_output(self, output: str) -> list[dict]:
            """解析扫描输出
            
            Args:
                output: ble_scan.py 的输出文本
                
            Returns:
                设备列表，每个设备是一个字典 {name, address, rssi}
            """
            devices = []
            lines = output.strip().split('\n')
            
            # 跳过表头和分隔线
            for line in lines:
                if line.startswith('ADDRESS') or line.startswith('-') or not line.strip():
                    continue
                if '(no BLE devices found)' in line:
                    break
                
                # 解析设备信息
                parts = line.split(None, 2)  # 最多分割成 3 部分
                if len(parts) >= 2:
                    address = parts[0]
                    rssi = parts[1] if len(parts) > 1 else ""
                    name = parts[2] if len(parts) > 2 else ""
                    
                    devices.append({
                        'name': name,
                        'address': address,
                        'rssi': rssi
                    })
            
            return devices
        
        def _on_scan_completed(self, devices: list[dict]) -> None:
            """扫描完成回调"""
            # 更新 UI 状态
            self._is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            # 显示结果
            self.results_table.setRowCount(len(devices))
            for i, device in enumerate(devices):
                self.results_table.setItem(i, 0, QTableWidgetItem(device['name']))
                self.results_table.setItem(i, 1, QTableWidgetItem(device['address']))
                self.results_table.setItem(i, 2, QTableWidgetItem(device['rssi']))
            
            # 更新状态
            self.status_label.setText(f"状态: 已发现 {len(devices)} 个设备")
            self.log_info(f"BLE 扫描完成，发现 {len(devices)} 个设备")
        
        def _on_stop_scan(self) -> None:
            """停止 BLE 扫描"""
            self.log_info("停止 BLE 扫描")
            
            # 注意：bleak 的扫描不容易中途停止，这里只是更新 UI 状态
            self._is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("状态: 已停止")
        
        def _on_export_results(self) -> None:
            """导出扫描结果"""
            if not self._scan_results:
                QMessageBox.information(self, "提示", "没有可导出的扫描结果")
                return
            
            # 选择保存文件
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出扫描结果",
                "ble_scan_results.txt",
                "文本文件 (*.txt);;CSV 文件 (*.csv);;所有文件 (*.*)"
            )
            
            if not file_path:
                return
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 写入表头
                    f.write(f"{'设备名称':<40} {'地址':<18} RSSI\n")
                    f.write("-" * 70 + "\n")
                    
                    # 写入设备信息
                    for device in self._scan_results:
                        name = device['name'][:40]
                        address = device['address']
                        rssi = device['rssi']
                        f.write(f"{name:<40} {address:<18} {rssi}\n")
                
                self.log_info(f"扫描结果已导出到: {file_path}")
                QMessageBox.information(self, "成功", f"扫描结果已导出到:\n{file_path}")
                
            except Exception as e:
                self.log_error(f"导出失败: {e}")
                QMessageBox.critical(self, "错误", f"导出失败:\n{e}")
        
        def stop(self) -> None:
            """停止模块"""
            if self._is_running:
                self._on_stop_scan()
            super().stop()

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    
    class BLEModule(BaseModule):  # type: ignore
        """BLE 蓝牙扫描模块（tkinter 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: tk.Widget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            self._scan_thread: threading.Thread | None = None
            self._scan_results: list = []
            self._bleak_available = self._check_bleak_available()
            self._setup_ui()
        
        def get_module_name(self) -> str:
            return "ble"
        
        def get_display_name(self) -> str:
            return "BLE 蓝牙扫描"
        
        def _check_bleak_available(self) -> bool:
            """检测 bleak 库是否可用"""
            try:
                import bleak
                return True
            except ImportError:
                return False
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            if not self._bleak_available:
                # 显示依赖缺失提示
                warning_frame = ttk.LabelFrame(self, text="依赖缺失")
                warning_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                warning_text = tk.Text(warning_frame, height=8, wrap=tk.WORD)
                warning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                warning_text.insert(1.0,
                    "⚠️ BLE 扫描需要安装 bleak 库\n\n"
                    "请运行以下命令安装：\n"
                    "  pip install 'linktunnel[ble]'\n\n"
                    "或者：\n"
                    "  pip install bleak"
                )
                warning_text.config(state=tk.DISABLED)
                return
            
            # 配置区域
            config_frame = ttk.LabelFrame(self, text="扫描配置")
            config_frame.pack(fill=tk.X, padx=5, pady=5)
            
            control_frame = ttk.Frame(config_frame)
            control_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(control_frame, text="扫描超时:").pack(side=tk.LEFT, padx=5)
            self.timeout_var = tk.StringVar(value="5")
            timeout_combo = ttk.Combobox(control_frame, textvariable=self.timeout_var, width=5)
            timeout_combo['values'] = ["5", "10", "15", "20", "30"]
            timeout_combo.pack(side=tk.LEFT, padx=5)
            ttk.Label(control_frame, text="秒").pack(side=tk.LEFT, padx=5)
            
            self.start_btn = ttk.Button(control_frame, text="开始扫描", command=self._on_start_scan)
            self.start_btn.pack(side=tk.LEFT, padx=5)
            
            self.stop_btn = ttk.Button(control_frame, text="停止", command=self._on_stop_scan, state=tk.DISABLED)
            self.stop_btn.pack(side=tk.LEFT, padx=5)
            
            self.export_btn = ttk.Button(control_frame, text="导出结果", command=self._on_export_results)
            self.export_btn.pack(side=tk.LEFT, padx=5)
            
            # 结果表格
            results_frame = ttk.LabelFrame(self, text="扫描结果")
            results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建表格
            columns = ("name", "address", "rssi")
            self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings")
            self.results_tree.heading("name", text="设备名称")
            self.results_tree.heading("address", text="地址")
            self.results_tree.heading("rssi", text="RSSI")
            self.results_tree.column("name", width=200)
            self.results_tree.column("address", width=200)
            self.results_tree.column("rssi", width=100)
            
            scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
            self.results_tree.configure(yscrollcommand=scrollbar.set)
            
            self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 状态标签
            self.status_label = ttk.Label(self, text="状态: 就绪")
            self.status_label.pack(fill=tk.X, padx=5, pady=5)
        
        def _on_start_scan(self) -> None:
            """开始 BLE 扫描"""
            timeout = int(self.timeout_var.get())
            
            self.log_info(f"开始 BLE 扫描，超时 {timeout} 秒")
            
            # 清空之前的结果
            self._scan_results.clear()
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # 更新 UI 状态
            self._is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"状态: 扫描中... (超时 {timeout} 秒)")
            
            # 在后台线程中执行扫描
            self._scan_thread = threading.Thread(
                target=self._run_scan,
                args=(timeout,),
                daemon=True
            )
            self._scan_thread.start()
        
        def _run_scan(self, timeout: int) -> None:
            """在后台线程中运行 BLE 扫描"""
            try:
                from linktunnel.ble_scan import run_ble_scan
                
                output = io.StringIO()
                result_code = run_ble_scan(timeout_s=float(timeout), out=output)
                
                if result_code == 0:
                    output_text = output.getvalue()
                    devices = self._parse_scan_output(output_text)
                    self._scan_results = devices
                    
                    # 在主线程中更新 UI
                    self.after(0, self._on_scan_completed, devices)
                else:
                    self.log_error("BLE 扫描失败")
                    self.after(0, self._on_scan_completed, [])
                    
            except Exception as e:
                self.log_error(f"BLE 扫描异常: {e}")
                self.after(0, self._on_scan_completed, [])
        
        def _parse_scan_output(self, output: str) -> list[dict]:
            """解析扫描输出"""
            devices = []
            lines = output.strip().split('\n')
            
            for line in lines:
                if line.startswith('ADDRESS') or line.startswith('-') or not line.strip():
                    continue
                if '(no BLE devices found)' in line:
                    break
                
                parts = line.split(None, 2)
                if len(parts) >= 2:
                    address = parts[0]
                    rssi = parts[1] if len(parts) > 1 else ""
                    name = parts[2] if len(parts) > 2 else ""
                    
                    devices.append({
                        'name': name,
                        'address': address,
                        'rssi': rssi
                    })
            
            return devices
        
        def _on_scan_completed(self, devices: list[dict]) -> None:
            """扫描完成回调"""
            self._is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            # 显示结果
            for device in devices:
                self.results_tree.insert("", tk.END, values=(
                    device['name'],
                    device['address'],
                    device['rssi']
                ))
            
            self.status_label.config(text=f"状态: 已发现 {len(devices)} 个设备")
            self.log_info(f"BLE 扫描完成，发现 {len(devices)} 个设备")
        
        def _on_stop_scan(self) -> None:
            """停止 BLE 扫描"""
            self.log_info("停止 BLE 扫描")
            
            self._is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="状态: 已停止")
        
        def _on_export_results(self) -> None:
            """导出扫描结果"""
            if not self._scan_results:
                messagebox.showinfo("提示", "没有可导出的扫描结果")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="导出扫描结果",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("CSV 文件", "*.csv"), ("所有文件", "*.*")]
            )
            
            if not file_path:
                return
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"{'设备名称':<40} {'地址':<18} RSSI\n")
                    f.write("-" * 70 + "\n")
                    
                    for device in self._scan_results:
                        name = device['name'][:40]
                        address = device['address']
                        rssi = device['rssi']
                        f.write(f"{name:<40} {address:<18} {rssi}\n")
                
                self.log_info(f"扫描结果已导出到: {file_path}")
                messagebox.showinfo("成功", f"扫描结果已导出到:\n{file_path}")
                
            except Exception as e:
                self.log_error(f"导出失败: {e}")
                messagebox.showerror("错误", f"导出失败:\n{e}")
        
        def stop(self) -> None:
            """停止模块"""
            if self._is_running:
                self._on_stop_scan()
            super().stop()
