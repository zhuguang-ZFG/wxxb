"""I2C 扫描模块（仅限 Linux）"""

from __future__ import annotations

import io
import platform
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
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    class I2CModule(BaseModule):
        """I2C 扫描模块（PyQt6 版本）"""

        # 信号
        scan_completed = pyqtSignal(list)  # 扫描完成信号

        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: QWidget | None = None,
        ):
            super().__init__(config_manager, log_manager, parent)
            self._scan_thread: threading.Thread | None = None
            self._scan_results: list[int] = []
            self._is_linux = platform.system() == "Linux"
            self._smbus_available = self._check_smbus_available()
            self._setup_ui()

        def get_module_name(self) -> str:
            return "i2c"

        def get_display_name(self) -> str:
            return "I2C 扫描"

        def get_icon(self) -> QIcon:
            return QIcon()  # TODO: 添加图标

        def _check_smbus_available(self) -> bool:
            """检测 smbus2 库是否可用"""
            if not self._is_linux:
                return False
            try:
                import smbus2

                return True
            except ImportError:
                return False

        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)

            # 平台检测提示
            if not self._is_linux:
                warning_group = QGroupBox("平台不支持")
                warning_layout = QVBoxLayout(warning_group)

                warning_label = QLabel(
                    "⚠️ I2C 扫描仅支持 Linux 平台\n\n"
                    f"当前平台: {platform.system()}\n\n"
                    "I2C 扫描需要访问 /dev/i2c-* 设备文件，\n"
                    "这些设备文件仅在 Linux 系统上可用。"
                )
                warning_label.setStyleSheet("color: orange; padding: 10px;")
                warning_layout.addWidget(warning_label)

                layout.addWidget(warning_group)
                layout.addStretch()
                return

            # 依赖检测提示
            if not self._smbus_available:
                warning_group = QGroupBox("依赖缺失")
                warning_layout = QVBoxLayout(warning_group)

                warning_label = QLabel(
                    "⚠️ I2C 扫描需要安装 smbus2 库\n\n"
                    "请运行以下命令安装：\n"
                    "  pip install 'linktunnel[i2c]'\n\n"
                    "或者：\n"
                    "  pip install smbus2\n\n"
                    "注意：您可能还需要将用户添加到 i2c 组：\n"
                    "  sudo usermod -a -G i2c $USER"
                )
                warning_label.setStyleSheet("color: orange; padding: 10px;")
                warning_layout.addWidget(warning_label)

                layout.addWidget(warning_group)
                layout.addStretch()
                return

            # 配置区域
            config_group = QGroupBox("扫描配置")
            config_layout = QHBoxLayout(config_group)

            config_layout.addWidget(QLabel("I2C 总线:"))
            self.bus_combo = QComboBox()
            self.bus_combo.addItems(["0", "1", "2", "3", "4", "5"])
            self.bus_combo.setCurrentText("1")
            config_layout.addWidget(self.bus_combo)

            config_layout.addStretch()

            # 控制按钮
            self.scan_btn = QPushButton("扫描")
            self.scan_btn.clicked.connect(self._on_start_scan)
            config_layout.addWidget(self.scan_btn)

            self.export_btn = QPushButton("导出结果")
            self.export_btn.clicked.connect(self._on_export_results)
            config_layout.addWidget(self.export_btn)

            layout.addWidget(config_group)

            # 地址网格显示
            grid_group = QGroupBox("I2C 地址网格 (0x00-0x7F)")
            grid_layout = QVBoxLayout(grid_group)

            # 创建地址网格
            self.address_grid = QGridLayout()
            self.address_labels = {}

            # 添加列标题
            for col in range(16):
                header = QLabel(f"{col:X}")
                header.setStyleSheet("font-weight: bold; padding: 5px;")
                self.address_grid.addWidget(header, 0, col + 1)

            # 添加行标题和地址单元格
            for row in range(8):
                # 行标题
                header = QLabel(f"{row:X}0")
                header.setStyleSheet("font-weight: bold; padding: 5px;")
                self.address_grid.addWidget(header, row + 1, 0)

                # 地址单元格
                for col in range(16):
                    addr = row * 16 + col
                    if addr > 0x7F:
                        break

                    label = QLabel(f"{addr:02X}")
                    label.setStyleSheet(
                        "border: 1px solid #ccc; "
                        "padding: 5px; "
                        "background-color: #f0f0f0; "
                        "min-width: 30px; "
                        "text-align: center;"
                    )
                    self.address_labels[addr] = label
                    self.address_grid.addWidget(label, row + 1, col + 1)

            grid_layout.addLayout(self.address_grid)
            layout.addWidget(grid_group)

            # 扫描日志
            log_group = QGroupBox("扫描日志")
            log_layout = QVBoxLayout(log_group)

            self.scan_log = QTextEdit()
            self.scan_log.setReadOnly(True)
            self.scan_log.setMaximumHeight(150)
            log_layout.addWidget(self.scan_log)

            layout.addWidget(log_group)

            # 状态信息
            self.status_label = QLabel("状态: 就绪")
            layout.addWidget(self.status_label)

            # 连接信号
            self.scan_completed.connect(self._on_scan_completed)

        def _on_start_scan(self) -> None:
            """开始 I2C 扫描"""
            bus = int(self.bus_combo.currentText())

            self.log_info(f"开始扫描 I2C 总线 {bus}")
            self.scan_log.append(f"正在扫描 I2C 总线 {bus}...")

            # 清空之前的结果
            self._scan_results.clear()
            self._reset_address_grid()

            # 更新 UI 状态
            self._is_running = True
            self.scan_btn.setEnabled(False)
            self.status_label.setText(f"状态: 扫描中... (总线 {bus})")

            # 在后台线程中执行扫描
            self._scan_thread = threading.Thread(
                target=self._run_scan, args=(bus,), daemon=True
            )
            self._scan_thread.start()

        def _run_scan(self, bus: int) -> None:
            """在后台线程中运行 I2C 扫描"""
            try:
                from linktunnel.i2c_linux import i2c_scan

                # 捕获输出
                output = io.StringIO()
                result_code = i2c_scan(bus, out=output)

                if result_code == 0:
                    # 解析输出
                    output_text = output.getvalue()
                    addresses = self._parse_scan_output(output_text)
                    self._scan_results = addresses

                    # 发送完成信号
                    self.scan_completed.emit(addresses)
                else:
                    self.log_error("I2C 扫描失败")
                    self.scan_completed.emit([])

            except Exception as e:
                self.log_error(f"I2C 扫描异常: {e}")
                self.scan_completed.emit([])

        def _parse_scan_output(self, output: str) -> list[int]:
            """解析扫描输出

            Args:
                output: i2c_linux.py 的输出文本

            Returns:
                地址列表（整数）
            """
            addresses = []

            # 查找地址列表
            if "addresses (7-bit):" in output:
                # 提取地址部分
                addr_part = output.split("addresses (7-bit):")[1].strip()
                # 分割并解析每个地址
                for addr_str in addr_part.split(","):
                    addr_str = addr_str.strip()
                    if addr_str.startswith("0x"):
                        try:
                            addr = int(addr_str, 16)
                            addresses.append(addr)
                        except ValueError:
                            pass

            return addresses

        def _reset_address_grid(self) -> None:
            """重置地址网格显示"""
            for addr, label in self.address_labels.items():
                label.setStyleSheet(
                    "border: 1px solid #ccc; "
                    "padding: 5px; "
                    "background-color: #f0f0f0; "
                    "min-width: 30px; "
                    "text-align: center;"
                )

        def _on_scan_completed(self, addresses: list[int]) -> None:
            """扫描完成回调"""
            # 更新 UI 状态
            self._is_running = False
            self.scan_btn.setEnabled(True)

            # 高亮显示找到的地址
            for addr in addresses:
                if addr in self.address_labels:
                    label = self.address_labels[addr]
                    label.setStyleSheet(
                        "border: 2px solid #4CAF50; "
                        "padding: 5px; "
                        "background-color: #C8E6C9; "
                        "min-width: 30px; "
                        "text-align: center; "
                        "font-weight: bold;"
                    )

            # 更新日志
            if addresses:
                addr_list = ", ".join(f"0x{a:02X}" for a in addresses)
                self.scan_log.append(f"发现 {len(addresses)} 个设备: {addr_list}")
            else:
                self.scan_log.append("未发现设备（或权限不足）")

            # 更新状态
            self.status_label.setText(f"状态: 已发现 {len(addresses)} 个设备")
            self.log_info(f"I2C 扫描完成，发现 {len(addresses)} 个设备")

        def _on_export_results(self) -> None:
            """导出扫描结果"""
            if not self._scan_results:
                QMessageBox.information(self, "提示", "没有可导出的扫描结果")
                return

            # 选择保存文件
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出扫描结果",
                "i2c_scan_results.txt",
                "文本文件 (*.txt);;所有文件 (*.*)",
            )

            if not file_path:
                return

            try:
                bus = int(self.bus_combo.currentText())
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"I2C 总线 {bus} 扫描结果\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"发现 {len(self._scan_results)} 个设备:\n\n")

                    for addr in self._scan_results:
                        f.write(f"  0x{addr:02X} ({addr})\n")

                self.log_info(f"扫描结果已导出到: {file_path}")
                QMessageBox.information(self, "成功", f"扫描结果已导出到:\n{file_path}")

            except Exception as e:
                self.log_error(f"导出失败: {e}")
                QMessageBox.critical(self, "错误", f"导出失败:\n{e}")

        def stop(self) -> None:
            """停止模块"""
            if self._is_running:
                self._is_running = False
            super().stop()

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog

    class I2CModule(BaseModule):  # type: ignore
        """I2C 扫描模块（tkinter 版本）"""

        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: tk.Widget | None = None,
        ):
            super().__init__(config_manager, log_manager, parent)
            self._scan_thread: threading.Thread | None = None
            self._scan_results: list[int] = []
            self._is_linux = platform.system() == "Linux"
            self._smbus_available = self._check_smbus_available()
            self._setup_ui()

        def get_module_name(self) -> str:
            return "i2c"

        def get_display_name(self) -> str:
            return "I2C 扫描"

        def _check_smbus_available(self) -> bool:
            """检测 smbus2 库是否可用"""
            if not self._is_linux:
                return False
            try:
                import smbus2

                return True
            except ImportError:
                return False

        def _setup_ui(self) -> None:
            """设置用户界面"""
            if not self._is_linux:
                # 显示平台不支持提示
                warning_frame = ttk.LabelFrame(self, text="平台不支持")
                warning_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                warning_text = tk.Text(warning_frame, height=8, wrap=tk.WORD)
                warning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                warning_text.insert(
                    1.0,
                    f"⚠️ I2C 扫描仅支持 Linux 平台\n\n"
                    f"当前平台: {platform.system()}\n\n"
                    "I2C 扫描需要访问 /dev/i2c-* 设备文件，\n"
                    "这些设备文件仅在 Linux 系统上可用。",
                )
                warning_text.config(state=tk.DISABLED)
                return

            if not self._smbus_available:
                # 显示依赖缺失提示
                warning_frame = ttk.LabelFrame(self, text="依赖缺失")
                warning_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                warning_text = tk.Text(warning_frame, height=10, wrap=tk.WORD)
                warning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                warning_text.insert(
                    1.0,
                    "⚠️ I2C 扫描需要安装 smbus2 库\n\n"
                    "请运行以下命令安装：\n"
                    "  pip install 'linktunnel[i2c]'\n\n"
                    "或者：\n"
                    "  pip install smbus2\n\n"
                    "注意：您可能还需要将用户添加到 i2c 组：\n"
                    "  sudo usermod -a -G i2c $USER",
                )
                warning_text.config(state=tk.DISABLED)
                return

            # 配置区域
            config_frame = ttk.LabelFrame(self, text="扫描配置")
            config_frame.pack(fill=tk.X, padx=5, pady=5)

            control_frame = ttk.Frame(config_frame)
            control_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(control_frame, text="I2C 总线:").pack(side=tk.LEFT, padx=5)
            self.bus_var = tk.StringVar(value="1")
            bus_combo = ttk.Combobox(control_frame, textvariable=self.bus_var, width=5)
            bus_combo["values"] = ["0", "1", "2", "3", "4", "5"]
            bus_combo.pack(side=tk.LEFT, padx=5)

            self.scan_btn = ttk.Button(
                control_frame, text="扫描", command=self._on_start_scan
            )
            self.scan_btn.pack(side=tk.LEFT, padx=5)

            self.export_btn = ttk.Button(
                control_frame, text="导出结果", command=self._on_export_results
            )
            self.export_btn.pack(side=tk.LEFT, padx=5)

            # 结果显示
            results_frame = ttk.LabelFrame(self, text="扫描结果")
            results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(
                results_frame, orient=tk.VERTICAL, command=self.results_text.yview
            )
            self.results_text.configure(yscrollcommand=scrollbar.set)

            self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 状态标签
            self.status_label = ttk.Label(self, text="状态: 就绪")
            self.status_label.pack(fill=tk.X, padx=5, pady=5)

        def _on_start_scan(self) -> None:
            """开始 I2C 扫描"""
            bus = int(self.bus_var.get())

            self.log_info(f"开始扫描 I2C 总线 {bus}")
            self.results_text.insert(tk.END, f"正在扫描 I2C 总线 {bus}...\n")

            # 清空之前的结果
            self._scan_results.clear()

            # 更新 UI 状态
            self._is_running = True
            self.scan_btn.config(state=tk.DISABLED)
            self.status_label.config(text=f"状态: 扫描中... (总线 {bus})")

            # 在后台线程中执行扫描
            self._scan_thread = threading.Thread(
                target=self._run_scan, args=(bus,), daemon=True
            )
            self._scan_thread.start()

        def _run_scan(self, bus: int) -> None:
            """在后台线程中运行 I2C 扫描"""
            try:
                from linktunnel.i2c_linux import i2c_scan

                output = io.StringIO()
                result_code = i2c_scan(bus, out=output)

                if result_code == 0:
                    output_text = output.getvalue()
                    addresses = self._parse_scan_output(output_text)
                    self._scan_results = addresses

                    # 在主线程中更新 UI
                    self.after(0, self._on_scan_completed, addresses)
                else:
                    self.log_error("I2C 扫描失败")
                    self.after(0, self._on_scan_completed, [])

            except Exception as e:
                self.log_error(f"I2C 扫描异常: {e}")
                self.after(0, self._on_scan_completed, [])

        def _parse_scan_output(self, output: str) -> list[int]:
            """解析扫描输出"""
            addresses = []

            if "addresses (7-bit):" in output:
                addr_part = output.split("addresses (7-bit):")[1].strip()
                for addr_str in addr_part.split(","):
                    addr_str = addr_str.strip()
                    if addr_str.startswith("0x"):
                        try:
                            addr = int(addr_str, 16)
                            addresses.append(addr)
                        except ValueError:
                            pass

            return addresses

        def _on_scan_completed(self, addresses: list[int]) -> None:
            """扫描完成回调"""
            self._is_running = False
            self.scan_btn.config(state=tk.NORMAL)

            # 显示结果
            if addresses:
                addr_list = ", ".join(f"0x{a:02X}" for a in addresses)
                self.results_text.insert(
                    tk.END, f"发现 {len(addresses)} 个设备: {addr_list}\n"
                )
            else:
                self.results_text.insert(tk.END, "未发现设备（或权限不足）\n")

            self.status_label.config(text=f"状态: 已发现 {len(addresses)} 个设备")
            self.log_info(f"I2C 扫描完成，发现 {len(addresses)} 个设备")

        def _on_export_results(self) -> None:
            """导出扫描结果"""
            if not self._scan_results:
                messagebox.showinfo("提示", "没有可导出的扫描结果")
                return

            file_path = filedialog.asksaveasfilename(
                title="导出扫描结果",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            )

            if not file_path:
                return

            try:
                bus = int(self.bus_var.get())
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"I2C 总线 {bus} 扫描结果\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"发现 {len(self._scan_results)} 个设备:\n\n")

                    for addr in self._scan_results:
                        f.write(f"  0x{addr:02X} ({addr})\n")

                self.log_info(f"扫描结果已导出到: {file_path}")
                messagebox.showinfo("成功", f"扫描结果已导出到:\n{file_path}")

            except Exception as e:
                self.log_error(f"导出失败: {e}")
                messagebox.showerror("错误", f"导出失败:\n{e}")

        def stop(self) -> None:
            """停止模块"""
            if self._is_running:
                self._is_running = False
            super().stop()
