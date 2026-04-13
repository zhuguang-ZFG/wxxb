"""Grbl CNC 控制模块"""

from __future__ import annotations

import queue
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

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
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    
    class GrblModule(BaseModule):
        """Grbl CNC 控制模块（PyQt6 版本）"""
        
        # 信号
        status_updated = pyqtSignal(dict)  # 状态更新信号
        stream_progress = pyqtSignal(int, int)  # 流式传输进度信号 (current, total)
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: QWidget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            
            # 状态变量
            self._grbl_serial = None
            self._monitor_thread: threading.Thread | None = None
            self._stream_thread: threading.Thread | None = None
            self._stop_monitor = threading.Event()
            self._stop_stream = threading.Event()
            self._status_queue: queue.Queue = queue.Queue()
            
            # 连接状态
            self._connected = False
            self._streaming = False
            
            # 设置 UI
            self._setup_ui()
            
            # 启动队列轮询
            self._poll_timer = QTimer(self)
            self._poll_timer.timeout.connect(self._poll_status_queue)
            self._poll_timer.start(100)
            
            # 加载配置
            self._load_saved_config()
        
        def get_module_name(self) -> str:
            return "grbl"
        
        def get_display_name(self) -> str:
            return "Grbl CNC 控制"
        
        def get_icon(self) -> QIcon:
            return QIcon()  # TODO: 添加图标
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            layout = QVBoxLayout(self)
            
            # 连接配置区域
            conn_group = self._create_connection_group()
            layout.addWidget(conn_group)
            
            # 状态显示区域
            status_group = self._create_status_group()
            layout.addWidget(status_group)
            
            # 标签页
            self.tabs = QTabWidget()
            
            # G 代码流式传输标签页
            self.stream_tab = self._create_stream_tab()
            self.tabs.addTab(self.stream_tab, "G 代码流式传输")
            
            # 手动控制标签页
            self.manual_tab = self._create_manual_tab()
            self.tabs.addTab(self.manual_tab, "手动控制")
            
            # 设置标签页
            self.settings_tab = self._create_settings_tab()
            self.tabs.addTab(self.settings_tab, "设置")
            
            layout.addWidget(self.tabs)
        
        def _create_connection_group(self) -> QGroupBox:
            """创建连接配置区域"""
            group = QGroupBox("设备连接")
            layout = QVBoxLayout(group)
            
            # 连接类型选择
            conn_type_layout = QHBoxLayout()
            conn_type_layout.addWidget(QLabel("连接方式:"))
            
            self.serial_radio = QRadioButton("串口")
            self.serial_radio.setChecked(True)
            self.serial_radio.toggled.connect(self._on_connection_type_changed)
            conn_type_layout.addWidget(self.serial_radio)
            
            self.wifi_radio = QRadioButton("WiFi (Telnet)")
            conn_type_layout.addWidget(self.wifi_radio)
            
            conn_type_layout.addStretch()
            layout.addLayout(conn_type_layout)
            
            # 串口配置
            serial_layout = QHBoxLayout()
            serial_layout.addWidget(QLabel("串口:"))
            self.port_combo = QComboBox()
            self.port_combo.setEditable(True)
            self.port_combo.setMinimumWidth(150)
            serial_layout.addWidget(self.port_combo)
            
            refresh_btn = QPushButton("刷新")
            refresh_btn.clicked.connect(self._refresh_serial_ports)
            serial_layout.addWidget(refresh_btn)
            
            serial_layout.addWidget(QLabel("波特率:"))
            self.baud_combo = QComboBox()
            self.baud_combo.addItems(["9600", "115200", "230400", "460800", "921600"])
            self.baud_combo.setCurrentText("115200")
            serial_layout.addWidget(self.baud_combo)
            
            serial_layout.addStretch()
            self.serial_config_widget = QWidget()
            self.serial_config_widget.setLayout(serial_layout)
            layout.addWidget(self.serial_config_widget)
            
            # WiFi 配置
            wifi_layout = QHBoxLayout()
            wifi_layout.addWidget(QLabel("地址:"))
            self.wifi_address = QLineEdit()
            self.wifi_address.setPlaceholderText("socket://192.168.4.1:23")
            self.wifi_address.setMinimumWidth(300)
            wifi_layout.addWidget(self.wifi_address)
            wifi_layout.addStretch()
            
            self.wifi_config_widget = QWidget()
            self.wifi_config_widget.setLayout(wifi_layout)
            self.wifi_config_widget.setVisible(False)
            layout.addWidget(self.wifi_config_widget)
            
            # 控制按钮
            btn_layout = QHBoxLayout()
            self.connect_btn = QPushButton("连接")
            self.connect_btn.clicked.connect(self._on_connect)
            btn_layout.addWidget(self.connect_btn)
            
            self.disconnect_btn = QPushButton("断开")
            self.disconnect_btn.clicked.connect(self._on_disconnect)
            self.disconnect_btn.setEnabled(False)
            btn_layout.addWidget(self.disconnect_btn)
            
            self.reset_btn = QPushButton("复位")
            self.reset_btn.clicked.connect(self._on_reset)
            self.reset_btn.setEnabled(False)
            btn_layout.addWidget(self.reset_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            return group
        
        def _create_status_group(self) -> QGroupBox:
            """创建状态显示区域"""
            group = QGroupBox("实时状态")
            layout = QHBoxLayout(group)
            
            layout.addWidget(QLabel("状态:"))
            self.state_label = QLabel("未连接")
            self.state_label.setMinimumWidth(80)
            layout.addWidget(self.state_label)
            
            layout.addSpacing(20)
            
            layout.addWidget(QLabel("位置:"))
            self.position_label = QLabel("X:0.00 Y:0.00 Z:0.00")
            self.position_label.setMinimumWidth(200)
            layout.addWidget(self.position_label)
            
            layout.addSpacing(20)
            
            layout.addWidget(QLabel("缓冲:"))
            self.buffer_label = QLabel("0/127")
            self.buffer_label.setMinimumWidth(60)
            layout.addWidget(self.buffer_label)
            
            layout.addStretch()
            
            return group
        
        def _create_stream_tab(self) -> QWidget:
            """创建 G 代码流式传输标签页"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # 文件选择
            file_layout = QHBoxLayout()
            file_layout.addWidget(QLabel("G 代码文件:"))
            self.gcode_file_entry = QLineEdit()
            self.gcode_file_entry.setReadOnly(True)
            file_layout.addWidget(self.gcode_file_entry)
            
            browse_btn = QPushButton("浏览...")
            browse_btn.clicked.connect(self._on_browse_gcode)
            file_layout.addWidget(browse_btn)
            
            layout.addLayout(file_layout)
            
            # 控制按钮
            btn_layout = QHBoxLayout()
            self.stream_start_btn = QPushButton("开始传输")
            self.stream_start_btn.clicked.connect(self._on_start_stream)
            self.stream_start_btn.setEnabled(False)
            btn_layout.addWidget(self.stream_start_btn)
            
            self.stream_pause_btn = QPushButton("暂停")
            self.stream_pause_btn.clicked.connect(self._on_pause_stream)
            self.stream_pause_btn.setEnabled(False)
            btn_layout.addWidget(self.stream_pause_btn)
            
            self.stream_resume_btn = QPushButton("恢复")
            self.stream_resume_btn.clicked.connect(self._on_resume_stream)
            self.stream_resume_btn.setEnabled(False)
            btn_layout.addWidget(self.stream_resume_btn)
            
            self.stream_stop_btn = QPushButton("停止")
            self.stream_stop_btn.clicked.connect(self._on_stop_stream)
            self.stream_stop_btn.setEnabled(False)
            btn_layout.addWidget(self.stream_stop_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            # 进度显示
            progress_layout = QVBoxLayout()
            progress_layout.addWidget(QLabel("进度:"))
            self.progress_bar = QProgressBar()
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            progress_layout.addWidget(self.progress_bar)
            
            self.progress_label = QLabel("0 / 0 行")
            progress_layout.addWidget(self.progress_label)
            
            layout.addLayout(progress_layout)
            
            # 实时反馈
            layout.addWidget(QLabel("实时反馈:"))
            self.stream_log = QTextEdit()
            self.stream_log.setReadOnly(True)
            layout.addWidget(self.stream_log)
            
            return widget
        
        def _create_manual_tab(self) -> QWidget:
            """创建手动控制标签页"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # 命令输入
            cmd_layout = QHBoxLayout()
            cmd_layout.addWidget(QLabel("命令:"))
            self.manual_cmd_entry = QLineEdit()
            self.manual_cmd_entry.setPlaceholderText("输入 G 代码或 Grbl 命令...")
            self.manual_cmd_entry.returnPressed.connect(self._on_send_manual_command)
            cmd_layout.addWidget(self.manual_cmd_entry)
            
            send_btn = QPushButton("发送")
            send_btn.clicked.connect(self._on_send_manual_command)
            cmd_layout.addWidget(send_btn)
            
            layout.addLayout(cmd_layout)
            
            # 常用命令按钮
            quick_layout = QHBoxLayout()
            quick_layout.addWidget(QLabel("快捷命令:"))
            
            status_btn = QPushButton("查询状态 (?)")
            status_btn.clicked.connect(lambda: self._send_command("?"))
            quick_layout.addWidget(status_btn)
            
            home_btn = QPushButton("回零 ($H)")
            home_btn.clicked.connect(lambda: self._send_command("$H"))
            quick_layout.addWidget(home_btn)
            
            unlock_btn = QPushButton("解锁 ($X)")
            unlock_btn.clicked.connect(lambda: self._send_command("$X"))
            quick_layout.addWidget(unlock_btn)
            
            quick_layout.addStretch()
            layout.addLayout(quick_layout)
            
            # 响应显示
            layout.addWidget(QLabel("响应:"))
            self.manual_log = QTextEdit()
            self.manual_log.setReadOnly(True)
            layout.addWidget(self.manual_log)
            
            return widget
        
        def _create_settings_tab(self) -> QWidget:
            """创建设置标签页"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # 查询按钮
            btn_layout = QHBoxLayout()
            
            query_settings_btn = QPushButton("查询设置 ($$)")
            query_settings_btn.clicked.connect(self._on_query_settings)
            btn_layout.addWidget(query_settings_btn)
            
            query_build_btn = QPushButton("查询版本 ($I)")
            query_build_btn.clicked.connect(self._on_query_build_info)
            btn_layout.addWidget(query_build_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            # 设置显示
            layout.addWidget(QLabel("设置信息:"))
            self.settings_text = QTextEdit()
            self.settings_text.setReadOnly(True)
            layout.addWidget(self.settings_text)
            
            # 修改设置
            modify_layout = QHBoxLayout()
            modify_layout.addWidget(QLabel("修改设置:"))
            self.setting_key = QLineEdit()
            self.setting_key.setPlaceholderText("例如: $100")
            self.setting_key.setMaximumWidth(100)
            modify_layout.addWidget(self.setting_key)
            
            modify_layout.addWidget(QLabel("="))
            self.setting_value = QLineEdit()
            self.setting_value.setPlaceholderText("新值")
            self.setting_value.setMaximumWidth(150)
            modify_layout.addWidget(self.setting_value)
            
            apply_setting_btn = QPushButton("应用")
            apply_setting_btn.clicked.connect(self._on_apply_setting)
            modify_layout.addWidget(apply_setting_btn)
            
            modify_layout.addStretch()
            layout.addLayout(modify_layout)
            
            return widget
        
        def _load_saved_config(self) -> None:
            """加载保存的配置"""
            config = self.load_config()
            
            # 连接类型
            conn_type = config.get("connection_type", "serial")
            if conn_type == "wifi":
                self.wifi_radio.setChecked(True)
            else:
                self.serial_radio.setChecked(True)
            
            # 串口配置
            self.baud_combo.setCurrentText(str(config.get("baudrate", 115200)))
            
            # WiFi 配置
            self.wifi_address.setText(config.get("wifi_address", "socket://192.168.4.1:23"))
            
            # 自动刷新串口列表
            QTimer.singleShot(100, self._refresh_serial_ports)
        
        def _save_current_config(self) -> None:
            """保存当前配置"""
            config = {
                "connection_type": "wifi" if self.wifi_radio.isChecked() else "serial",
                "port": self.port_combo.currentText(),
                "baudrate": int(self.baud_combo.currentText()),
                "wifi_address": self.wifi_address.text(),
            }
            self.save_config(config)
        
        def _on_connection_type_changed(self) -> None:
            """连接类型改变"""
            is_serial = self.serial_radio.isChecked()
            self.serial_config_widget.setVisible(is_serial)
            self.wifi_config_widget.setVisible(not is_serial)
        
        def _refresh_serial_ports(self) -> None:
            """刷新串口列表"""
            try:
                from linktunnel.serial_util import list_serial_ports
                
                ports = list_serial_ports()
                port_names = [p.device for p in ports]
                
                current = self.port_combo.currentText()
                self.port_combo.clear()
                self.port_combo.addItems(port_names)
                
                # 恢复之前的选择
                if current and current in port_names:
                    self.port_combo.setCurrentText(current)
                
                self.log_info(f"发现 {len(ports)} 个串口")
                
            except Exception as e:
                self.log_error(f"刷新串口列表失败: {e}")
        
        def _on_connect(self) -> None:
            """连接设备"""
            if self._connected:
                self.log_warning("已经连接")
                return
            
            try:
                from linktunnel.grbl.client import open_grbl_serial
                
                if self.serial_radio.isChecked():
                    # 串口连接
                    port = self.port_combo.currentText()
                    if not port:
                        self.log_error("请选择串口")
                        return
                    
                    baudrate = int(self.baud_combo.currentText())
                    self.log_info(f"正在连接串口: {port} @ {baudrate}")
                    
                    self._grbl_serial = open_grbl_serial(
                        port=port,
                        url=None,
                        baud=baudrate,
                        timeout=0.1
                    )
                else:
                    # WiFi 连接
                    url = self.wifi_address.text().strip()
                    if not url:
                        self.log_error("请输入 WiFi 地址")
                        return
                    
                    self.log_info(f"正在连接 WiFi: {url}")
                    
                    self._grbl_serial = open_grbl_serial(
                        port=None,
                        url=url,
                        baud=115200,
                        timeout=0.1
                    )
                
                # 启动状态监控线程
                self._start_monitor()
                
                self._connected = True
                self._is_running = True
                
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.stream_start_btn.setEnabled(True)
                
                self.state_label.setText("已连接")
                self.log_info("设备已连接")
                
                self._save_current_config()
                
            except Exception as e:
                self.log_error(f"连接失败: {e}")
                if self._grbl_serial:
                    try:
                        self._grbl_serial.close()
                    except:
                        pass
                    self._grbl_serial = None
        
        def _on_disconnect(self) -> None:
            """断开连接"""
            if not self._connected:
                return
            
            self.log_info("正在断开连接...")
            
            # 停止监控线程
            self._stop_monitor.set()
            if self._monitor_thread:
                self._monitor_thread.join(timeout=2.0)
                self._monitor_thread = None
            
            # 停止流式传输
            if self._streaming:
                self._on_stop_stream()
            
            # 关闭串口
            if self._grbl_serial:
                try:
                    self._grbl_serial.close()
                except:
                    pass
                self._grbl_serial = None
            
            self._connected = False
            self._is_running = False
            
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.stream_start_btn.setEnabled(False)
            
            self.state_label.setText("未连接")
            self.position_label.setText("X:0.00 Y:0.00 Z:0.00")
            self.buffer_label.setText("0/127")
            
            self.log_info("设备已断开")
        
        def _on_reset(self) -> None:
            """复位设备"""
            if not self._connected or not self._grbl_serial:
                self.log_error("未连接设备")
                return
            
            try:
                from linktunnel.grbl.protocol import REALTIME_RESET
                
                self.log_info("正在复位设备...")
                self._grbl_serial.write(REALTIME_RESET)
                self._grbl_serial.flush()
                
                # 等待复位完成
                time.sleep(0.5)
                
                self.log_info("设备已复位")
                
            except Exception as e:
                self.log_error(f"复位失败: {e}")
        
        def _start_monitor(self) -> None:
            """启动状态监控线程"""
            self._stop_monitor.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
            self._monitor_thread.start()
        
        def _monitor_worker(self) -> None:
            """状态监控工作线程"""
            from linktunnel.grbl.protocol import REALTIME_STATUS
            from linktunnel.grbl.status import parse_status_report
            
            while not self._stop_monitor.is_set():
                try:
                    if not self._grbl_serial:
                        break
                    
                    # 发送状态查询
                    self._grbl_serial.write(REALTIME_STATUS)
                    self._grbl_serial.flush()
                    
                    # 读取响应
                    deadline = time.monotonic() + 1.0
                    while time.monotonic() < deadline:
                        if self._stop_monitor.is_set():
                            break
                        
                        raw = self._grbl_serial.readline()
                        if not raw:
                            time.sleep(0.01)
                            continue
                        
                        text = raw.decode("utf-8", errors="replace").strip()
                        if not text:
                            continue
                        
                        # 解析状态报告
                        report = parse_status_report(text)
                        if report:
                            self._status_queue.put(("status", report))
                            break
                    
                    # 每秒查询一次
                    time.sleep(1.0)
                    
                except Exception as e:
                    self._status_queue.put(("error", str(e)))
                    break
        
        def _poll_status_queue(self) -> None:
            """轮询状态队列"""
            try:
                while True:
                    item = self._status_queue.get_nowait()
                    if not isinstance(item, tuple) or len(item) != 2:
                        continue
                    
                    kind, data = item
                    
                    if kind == "status":
                        self._update_status_display(data)
                    elif kind == "error":
                        self.log_error(f"监控错误: {data}")
                    elif kind == "stream_line":
                        self.stream_log.append(data)
                    elif kind == "stream_progress":
                        current, total = data
                        self._update_stream_progress(current, total)
                    elif kind == "stream_done":
                        self._on_stream_complete(data)
                    
            except queue.Empty:
                pass
        
        def _update_status_display(self, report) -> None:
            """更新状态显示"""
            # 更新状态
            self.state_label.setText(report.state)
            
            # 更新位置
            mpos = report.fields.get("MPos", "")
            wpos = report.fields.get("WPos", "")
            
            if mpos:
                coords = mpos.split(",")
                if len(coords) >= 3:
                    self.position_label.setText(f"X:{coords[0]} Y:{coords[1]} Z:{coords[2]}")
            elif wpos:
                coords = wpos.split(",")
                if len(coords) >= 3:
                    self.position_label.setText(f"X:{coords[0]} Y:{coords[1]} Z:{coords[2]}")
            
            # 更新缓冲区
            buf = report.fields.get("Bf", "")
            if buf:
                self.buffer_label.setText(buf)
        
        def _on_browse_gcode(self) -> None:
            """浏览 G 代码文件"""
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择 G 代码文件",
                "",
                "G-code Files (*.nc *.gcode *.txt);;All Files (*)"
            )
            
            if file_path:
                self.gcode_file_entry.setText(file_path)
                self.log_info(f"已选择文件: {file_path}")
        
        def _on_start_stream(self) -> None:
            """开始流式传输"""
            if not self._connected or not self._grbl_serial:
                self.log_error("未连接设备")
                return
            
            file_path = self.gcode_file_entry.text()
            if not file_path:
                self.log_error("请选择 G 代码文件")
                return
            
            if not Path(file_path).is_file():
                self.log_error("文件不存在")
                return
            
            self.log_info(f"开始传输: {file_path}")
            
            self._streaming = True
            self._stop_stream.clear()
            
            self.stream_start_btn.setEnabled(False)
            self.stream_pause_btn.setEnabled(True)
            self.stream_stop_btn.setEnabled(True)
            self.stream_log.clear()
            self.progress_bar.setValue(0)
            
            # 启动流式传输线程
            self._stream_thread = threading.Thread(
                target=self._stream_worker,
                args=(file_path,),
                daemon=True
            )
            self._stream_thread.start()
        
        def _on_pause_stream(self) -> None:
            """暂停流式传输"""
            if not self._connected or not self._grbl_serial:
                return
            
            try:
                from linktunnel.grbl.protocol import REALTIME_HOLD
                
                self.log_info("暂停传输")
                self._grbl_serial.write(REALTIME_HOLD)
                self._grbl_serial.flush()
                
                self.stream_pause_btn.setEnabled(False)
                self.stream_resume_btn.setEnabled(True)
                
            except Exception as e:
                self.log_error(f"暂停失败: {e}")
        
        def _on_resume_stream(self) -> None:
            """恢复流式传输"""
            if not self._connected or not self._grbl_serial:
                return
            
            try:
                from linktunnel.grbl.protocol import REALTIME_RESUME
                
                self.log_info("恢复传输")
                self._grbl_serial.write(REALTIME_RESUME)
                self._grbl_serial.flush()
                
                self.stream_pause_btn.setEnabled(True)
                self.stream_resume_btn.setEnabled(False)
                
            except Exception as e:
                self.log_error(f"恢复失败: {e}")
        
        def _on_stop_stream(self) -> None:
            """停止流式传输"""
            self.log_info("停止传输")
            
            self._stop_stream.set()
            
            if self._stream_thread:
                self._stream_thread.join(timeout=2.0)
                self._stream_thread = None
            
            self._streaming = False
            
            self.stream_start_btn.setEnabled(True)
            self.stream_pause_btn.setEnabled(False)
            self.stream_resume_btn.setEnabled(False)
            self.stream_stop_btn.setEnabled(False)
        
        def _stream_worker(self, file_path: str) -> None:
            """流式传输工作线程"""
            try:
                from linktunnel.grbl.stream_job import iter_gcode_lines
                from linktunnel.grbl.protocol import send_line, read_until_ok
                
                # 统计总行数
                lines = list(iter_gcode_lines(file_path))
                total = len(lines)
                
                self._status_queue.put(("stream_line", f"总共 {total} 行 G 代码"))
                
                # 逐行发送
                for i, line in enumerate(lines):
                    if self._stop_stream.is_set():
                        self._status_queue.put(("stream_line", "传输已取消"))
                        self._status_queue.put(("stream_done", False))
                        return
                    
                    # 发送行
                    send_line(self._grbl_serial, line)
                    self._grbl_serial.flush()
                    
                    # 等待响应
                    try:
                        responses = read_until_ok(
                            self._grbl_serial,
                            timeout_s=10.0,
                            echo_status=False
                        )
                        
                        # 检查错误
                        for resp in responses:
                            if resp.strip().lower().startswith("error:"):
                                self._status_queue.put(("stream_line", f"[ERROR] {line} -> {resp}"))
                            else:
                                self._status_queue.put(("stream_line", f"[{i+1}/{total}] {line} -> {resp}"))
                    
                    except Exception as e:
                        self._status_queue.put(("stream_line", f"[ERROR] {line} -> {e}"))
                    
                    # 更新进度
                    self._status_queue.put(("stream_progress", (i + 1, total)))
                
                self._status_queue.put(("stream_line", "传输完成"))
                self._status_queue.put(("stream_done", True))
                
            except Exception as e:
                self._status_queue.put(("stream_line", f"传输错误: {e}"))
                self._status_queue.put(("stream_done", False))
        
        def _update_stream_progress(self, current: int, total: int) -> None:
            """更新流式传输进度"""
            if total > 0:
                percent = int(current * 100 / total)
                self.progress_bar.setValue(percent)
                self.progress_label.setText(f"{current} / {total} 行 ({percent}%)")
        
        def _on_stream_complete(self, success: bool) -> None:
            """流式传输完成"""
            self._streaming = False
            
            self.stream_start_btn.setEnabled(True)
            self.stream_pause_btn.setEnabled(False)
            self.stream_resume_btn.setEnabled(False)
            self.stream_stop_btn.setEnabled(False)
            
            if success:
                self.log_info("G 代码传输完成")
            else:
                self.log_warning("G 代码传输未完成")
        
        def _on_send_manual_command(self) -> None:
            """发送手动命令"""
            cmd = self.manual_cmd_entry.text().strip()
            if not cmd:
                return
            
            self._send_command(cmd)
            self.manual_cmd_entry.clear()
        
        def _send_command(self, cmd: str) -> None:
            """发送命令"""
            if not self._connected or not self._grbl_serial:
                self.log_error("未连接设备")
                return
            
            try:
                from linktunnel.grbl.protocol import send_line, read_until_ok
                
                self.manual_log.append(f"> {cmd}")
                
                # 发送命令
                send_line(self._grbl_serial, cmd)
                self._grbl_serial.flush()
                
                # 读取响应
                responses = read_until_ok(self._grbl_serial, timeout_s=5.0)
                
                for resp in responses:
                    self.manual_log.append(f"< {resp}")
                
            except Exception as e:
                self.manual_log.append(f"错误: {e}")
                self.log_error(f"发送命令失败: {e}")
        
        def _on_query_settings(self) -> None:
            """查询设置"""
            if not self._connected or not self._grbl_serial:
                self.log_error("未连接设备")
                return
            
            try:
                from linktunnel.grbl.report import dump_settings
                
                self.log_info("正在查询设置...")
                self.settings_text.clear()
                
                settings = dump_settings(self._grbl_serial, timeout_s=10.0)
                
                for line in settings:
                    self.settings_text.append(line)
                
                self.log_info("设置查询完成")
                
            except Exception as e:
                self.log_error(f"查询设置失败: {e}")
        
        def _on_query_build_info(self) -> None:
            """查询版本信息"""
            if not self._connected or not self._grbl_serial:
                self.log_error("未连接设备")
                return
            
            try:
                from linktunnel.grbl.report import dump_build_info
                
                self.log_info("正在查询版本信息...")
                self.settings_text.clear()
                
                info = dump_build_info(self._grbl_serial, timeout_s=5.0)
                
                for line in info:
                    self.settings_text.append(line)
                
                self.log_info("版本查询完成")
                
            except Exception as e:
                self.log_error(f"查询版本失败: {e}")
        
        def _on_apply_setting(self) -> None:
            """应用设置"""
            key = self.setting_key.text().strip()
            value = self.setting_value.text().strip()
            
            if not key or not value:
                self.log_error("请输入设置键和值")
                return
            
            cmd = f"{key}={value}"
            self._send_command(cmd)
            
            self.settings_text.append(f"\n应用设置: {cmd}")
        
        def get_occupied_resources(self) -> list[str]:
            """返回当前占用的资源"""
            if self._connected and self.serial_radio.isChecked():
                port = self.port_combo.currentText()
                if port:
                    return [port]
            return []
        
        def stop(self) -> None:
            """停止模块"""
            if self._connected:
                self._on_disconnect()
            super().stop()

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk
    
    class GrblModule(BaseModule):  # type: ignore
        """Grbl CNC 控制模块（tkinter 版本）"""
        
        def __init__(
            self,
            config_manager: ConfigManager,
            log_manager: LogManager,
            parent: tk.Widget | None = None
        ):
            super().__init__(config_manager, log_manager, parent)
            self._setup_ui()
        
        def get_module_name(self) -> str:
            return "grbl"
        
        def get_display_name(self) -> str:
            return "Grbl CNC 控制"
        
        def _setup_ui(self) -> None:
            """设置用户界面"""
            label = ttk.Label(self, text="Grbl CNC 控制模块（待实现 tkinter 版本）")
            label.pack(pady=20)
