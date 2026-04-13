"""Grbl CNC 控制模块 - 设备连接、状态监控、G代码流式传输、手动控制"""

from __future__ import annotations

import queue
import threading
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from PyQt6.QtCore import QTimer, pyqtSignal, Qt
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QComboBox,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QProgressBar,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
    )

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

if TYPE_CHECKING or not PYQT_AVAILABLE:
    from tkinter import ttk
    import tkinter as tk

from linktunnel.unified_gui.core.base_module import BaseModule


# Grbl 命令参考
GRBL_COMMANDS = {
    "系统命令": {
        "$H": "回零 - 执行归零循环",
        "$X": "解锁 - 解除警报状态",
        "$": "查看设置 - 显示所有参数",
        "$#": "查看参数 - 显示偏移量和位置",
        "$G": "查看状态 - 显示当前 G 代码模态状态",
        "$I": "查看版本 - 显示版本和编译信息",
        "$N": "启动块 - 显示启动块",
        "$C": "检查模式 - 切换检查模式",
        "$RST=$": "恢复默认设置",
        "$RST=#": "恢复位置",
        "$RST=*": "恢复全部",
        "?": "查询状态 - 获取实时状态",
        "!": "暂停 - 暂停当前操作",
        "~": "恢复 - 恢复暂停的操作",
        "^X": "软复位 - 执行软复位",
    },
    "G 代码命令": {
        "G0": "快速移动 - 不切割移动到指定位置",
        "G1": "直线切割 - 以指定速度切割到指定位置",
        "G2": "顺时针圆弧 - 顺时针方向的圆弧切割",
        "G3": "逆时针圆弧 - 逆时针方向的圆弧切割",
        "G4": "暂停 - 暂停指定时间（毫秒）",
        "G10": "设置偏移 - 设置工作坐标系偏移",
        "G17": "XY 平面 - 选择 XY 平面进行圆弧插补",
        "G18": "XZ 平面 - 选择 XZ 平面进行圆弧插补",
        "G19": "YZ 平面 - 选择 YZ 平面进行圆弧插补",
        "G20": "英寸单位 - 使用英寸作为单位",
        "G21": "毫米单位 - 使用毫米作为单位",
        "G28": "返回参考点 - 返回到参考点",
        "G30": "返回第二参考点 - 返回到第二参考点",
        "G53": "机器坐标 - 使用机器坐标系",
        "G54-G59": "工作坐标系 - 选择工作坐标系 1-6",
        "G80": "取消循环 - 取消钻孔或其他循环",
        "G90": "绝对定位 - 使用绝对坐标",
        "G91": "相对定位 - 使用相对坐标",
        "G92": "设置位置 - 设置当前位置为指定值",
        "G93": "反向时间进给 - 使用反向时间进给",
        "G94": "每分钟进给 - 使用每分钟进给速率",
        "G95": "每转进给 - 使用每转进给速率",
    },
    "M 代码命令": {
        "M0": "程序停止 - 停止程序执行",
        "M1": "可选停止 - 可选的程序停止",
        "M2": "程序结束 - 结束程序",
        "M3": "主轴顺时针 - 启动主轴顺时针旋转",
        "M4": "主轴逆时针 - 启动主轴逆时针旋转",
        "M5": "主轴停止 - 停止主轴旋转",
        "M6": "换刀 - 执行换刀操作",
        "M7": "冷却液 1 - 启动冷却液 1",
        "M8": "冷却液 2 - 启动冷却液 2",
        "M9": "冷却液关闭 - 关闭冷却液",
        "M30": "程序结束并复位 - 结束程序并复位",
    },
    "参数设置": {
        "$0": "步进脉冲时间 (µs)",
        "$1": "步进空闲延迟 (ms)",
        "$2": "步进端口反向掩码",
        "$3": "方向端口反向掩码",
        "$4": "步进启用反向",
        "$5": "限位引脚反向",
        "$6": "探针引脚反向",
        "$10": "状态报告掩码",
        "$11": "交接偏差 (mm)",
        "$12": "弧公差 (mm)",
        "$13": "报告英寸",
        "$20": "软限位启用",
        "$21": "硬限位启用",
        "$22": "硬限位启用（归零）",
        "$23": "限位引脚禁用",
        "$24": "归零搜索速率 (mm/min)",
        "$25": "归零进给速率 (mm/min)",
        "$26": "归零搜索脉冲 (mm)",
        "$27": "归零脉冲延迟 (ms)",
        "$30": "最大主轴速度 (RPM)",
        "$31": "最小主轴速度 (RPM)",
        "$32": "激光模式启用",
        "$100": "X 轴步数/mm",
        "$101": "Y 轴步数/mm",
        "$102": "Z 轴步数/mm",
        "$110": "X 轴最大速率 (mm/min)",
        "$111": "Y 轴最大速率 (mm/min)",
        "$112": "Z 轴最大速率 (mm/min)",
        "$120": "X 轴加速度 (mm/s²)",
        "$121": "Y 轴加速度 (mm/s²)",
        "$122": "Z 轴加速度 (mm/s²)",
        "$130": "X 轴最大行程 (mm)",
        "$131": "Y 轴最大行程 (mm)",
        "$132": "Z 轴最大行程 (mm)",
    },
}


class GrblCommandHelper:
    """Grbl 命令助手"""

    @staticmethod
    def get_all_commands() -> dict[str, dict[str, str]]:
        """获取所有命令"""
        return GRBL_COMMANDS

    @staticmethod
    def get_command_description(cmd: str) -> str:
        """获取命令描述"""
        for category, commands in GRBL_COMMANDS.items():
            if cmd in commands:
                return commands[cmd]
        return "未知命令"

    @staticmethod
    def search_commands(keyword: str) -> list[tuple[str, str, str]]:
        """搜索命令 - 返回 (category, cmd, desc) 列表"""
        results = []
        keyword_lower = keyword.lower()
        for category, commands in GRBL_COMMANDS.items():
            for cmd, desc in commands.items():
                if keyword_lower in cmd.lower() or keyword_lower in desc.lower():
                    results.append((category, cmd, desc))
        return results


class GrblModule(BaseModule):
    """Grbl CNC 控制模块"""

    if PYQT_AVAILABLE:
        # PyQt6 信号
        status_updated = pyqtSignal(str)
        stream_progress = pyqtSignal(int, int)  # current, total

    def get_module_name(self) -> str:
        return "grbl"

    def get_display_name(self) -> str:
        return "Grbl CNC"

    def get_icon(self) -> QIcon | None:
        if PYQT_AVAILABLE:
            return QIcon()  # 可以添加图标
        return None

    def __init__(self, config_manager, log_manager, parent=None):
        super().__init__(config_manager, log_manager, parent)

        # 状态
        self._serial = None
        self._monitor_thread = None
        self._stream_thread = None
        self._stop_event = threading.Event()
        self._result_queue: queue.Queue = queue.Queue()

        # 创建 UI
        if PYQT_AVAILABLE:
            self._create_pyqt_ui()
        else:
            self._create_tk_ui()

        # 定时器轮询队列
        if PYQT_AVAILABLE:
            self._poll_timer = QTimer(self)
            self._poll_timer.timeout.connect(self._poll_queue)
            self._poll_timer.start(100)

    def _create_pyqt_ui(self) -> None:
        """创建 PyQt6 界面"""
        layout = QVBoxLayout(self)

        # 标签页
        tabs = QTabWidget()
        tabs.addTab(self._create_connection_tab(), "设备连接")
        tabs.addTab(self._create_status_tab(), "状态监控")
        tabs.addTab(self._create_stream_tab(), "G代码传输")
        tabs.addTab(self._create_manual_tab(), "手动控制")
        tabs.addTab(self._create_commands_tab(), "命令参考")
        layout.addWidget(tabs)

    def _create_connection_tab(self):
        """创建连接标签页"""
        widget = QGroupBox("设备连接")
        layout = QVBoxLayout(widget)

        # 连接类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("连接类型:"))
        self._conn_type = QComboBox()
        self._conn_type.addItems(["串口 (USB)", "WiFi (Telnet)"])
        self._conn_type.currentIndexChanged.connect(self._on_conn_type_changed)
        type_layout.addWidget(self._conn_type)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # 串口配置
        self._serial_group = QGroupBox("串口配置")
        serial_layout = QVBoxLayout(self._serial_group)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("串口:"))
        self._port_combo = QComboBox()
        self._port_combo.setEditable(True)
        port_layout.addWidget(self._port_combo, 1)
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh_ports)
        port_layout.addWidget(refresh_btn)
        serial_layout.addLayout(port_layout)

        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("波特率:"))
        self._baud_combo = QComboBox()
        self._baud_combo.addItems(["115200", "57600", "38400", "19200", "9600"])
        baud_layout.addWidget(self._baud_combo)
        baud_layout.addStretch()
        serial_layout.addLayout(baud_layout)

        layout.addWidget(self._serial_group)

        # WiFi 配置
        self._wifi_group = QGroupBox("WiFi 配置")
        wifi_layout = QVBoxLayout(self._wifi_group)

        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("主机:"))
        self._host_entry = QLineEdit("192.168.4.1")
        host_layout.addWidget(self._host_entry)
        wifi_layout.addLayout(host_layout)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self._telnet_port = QLineEdit("23")
        port_layout.addWidget(self._telnet_port)
        port_layout.addStretch()
        wifi_layout.addLayout(port_layout)

        layout.addWidget(self._wifi_group)
        self._wifi_group.hide()

        # 连接按钮
        btn_layout = QHBoxLayout()
        self._connect_btn = QPushButton("连接")
        self._connect_btn.clicked.connect(self._on_connect)
        btn_layout.addWidget(self._connect_btn)

        self._disconnect_btn = QPushButton("断开")
        self._disconnect_btn.clicked.connect(self._on_disconnect)
        self._disconnect_btn.setEnabled(False)
        btn_layout.addWidget(self._disconnect_btn)

        self._reset_btn = QPushButton("复位 (Ctrl+X)")
        self._reset_btn.clicked.connect(self._on_reset)
        self._reset_btn.setEnabled(False)
        btn_layout.addWidget(self._reset_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 连接状态
        self._conn_status = QLabel("未连接")
        layout.addWidget(self._conn_status)

        layout.addStretch()

        # 初始刷新串口
        self._refresh_ports()

        return widget

    def _create_status_tab(self):
        """创建状态监控标签页"""
        widget = QGroupBox("实时状态")
        layout = QVBoxLayout(widget)

        # 状态显示
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("机器状态:"))
        self._machine_state = QLabel("未知")
        status_layout.addWidget(self._machine_state)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # 位置显示
        pos_group = QGroupBox("机器位置")
        pos_layout = QVBoxLayout(pos_group)

        self._pos_x = QLabel("X: --")
        self._pos_y = QLabel("Y: --")
        self._pos_z = QLabel("Z: --")
        pos_layout.addWidget(self._pos_x)
        pos_layout.addWidget(self._pos_y)
        pos_layout.addWidget(self._pos_z)

        layout.addWidget(pos_group)

        # 状态查询按钮
        query_layout = QHBoxLayout()
        query_btn = QPushButton("查询状态 (?)")
        query_btn.clicked.connect(self._on_query_status)
        query_layout.addWidget(query_btn)

        hold_btn = QPushButton("暂停 (!)")
        hold_btn.clicked.connect(lambda: self._send_realtime("!"))
        query_layout.addWidget(hold_btn)

        resume_btn = QPushButton("恢复 (~)")
        resume_btn.clicked.connect(lambda: self._send_realtime("~"))
        query_layout.addWidget(resume_btn)

        query_layout.addStretch()
        layout.addLayout(query_layout)

        # 状态日志
        layout.addWidget(QLabel("状态日志:"))
        self._status_log = QTextEdit()
        self._status_log.setReadOnly(True)
        self._status_log.setMaximumHeight(200)
        layout.addWidget(self._status_log)

        return widget

    def _create_stream_tab(self):
        """创建 G代码传输标签页"""
        widget = QGroupBox("G代码流式传输")
        layout = QVBoxLayout(widget)

        # 文件选择
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("G代码文件:"))
        self._gcode_file = QLineEdit()
        file_layout.addWidget(self._gcode_file, 1)
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_gcode_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        # 控制按钮
        btn_layout = QHBoxLayout()
        self._start_stream_btn = QPushButton("开始传输")
        self._start_stream_btn.clicked.connect(self._on_start_stream)
        btn_layout.addWidget(self._start_stream_btn)

        self._pause_stream_btn = QPushButton("暂停")
        self._pause_stream_btn.clicked.connect(self._on_pause_stream)
        self._pause_stream_btn.setEnabled(False)
        btn_layout.addWidget(self._pause_stream_btn)

        self._stop_stream_btn = QPushButton("停止")
        self._stop_stream_btn.clicked.connect(self._on_stop_stream)
        self._stop_stream_btn.setEnabled(False)
        btn_layout.addWidget(self._stop_stream_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 进度条
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("传输进度:"))
        self._progress_bar = QProgressBar()
        progress_layout.addWidget(self._progress_bar)
        self._progress_label = QLabel("0 / 0 行")
        progress_layout.addWidget(self._progress_label)
        layout.addLayout(progress_layout)

        # 传输日志
        layout.addWidget(QLabel("传输日志:"))
        self._stream_log = QTextEdit()
        self._stream_log.setReadOnly(True)
        layout.addWidget(self._stream_log)

        return widget

    def _create_manual_tab(self):
        """创建手动控制标签页"""
        widget = QGroupBox("手动控制")
        layout = QVBoxLayout(widget)

        # 命令输入
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("命令:"))
        self._manual_cmd = QLineEdit()
        self._manual_cmd.returnPressed.connect(self._on_send_manual_cmd)
        cmd_layout.addWidget(self._manual_cmd, 1)
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self._on_send_manual_cmd)
        cmd_layout.addWidget(send_btn)
        layout.addLayout(cmd_layout)

        # 快捷命令
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("快捷命令:"))

        home_btn = QPushButton("回零 ($H)")
        home_btn.clicked.connect(lambda: self._send_command("$H"))
        quick_layout.addWidget(home_btn)

        unlock_btn = QPushButton("解锁 ($X)")
        unlock_btn.clicked.connect(lambda: self._send_command("$X"))
        quick_layout.addWidget(unlock_btn)

        settings_btn = QPushButton("查看设置 ($$)")
        settings_btn.clicked.connect(lambda: self._send_command("$$"))
        quick_layout.addWidget(settings_btn)

        quick_layout.addStretch()
        layout.addLayout(quick_layout)

        # 响应日志
        layout.addWidget(QLabel("响应:"))
        self._manual_log = QTextEdit()
        self._manual_log.setReadOnly(True)
        layout.addWidget(self._manual_log)

        return widget

    def _create_commands_tab(self):
        """创建命令参考标签页"""
        widget = QGroupBox("Grbl 命令参考")
        layout = QVBoxLayout(widget)

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self._cmd_search = QLineEdit()
        self._cmd_search.setPlaceholderText("输入命令或关键词...")
        self._cmd_search.textChanged.connect(self._on_cmd_search_changed)
        search_layout.addWidget(self._cmd_search)
        layout.addLayout(search_layout)

        # 命令列表
        self._cmd_list = QListWidget()
        self._cmd_list.itemClicked.connect(self._on_cmd_selected)
        layout.addWidget(self._cmd_list)

        # 命令详情
        layout.addWidget(QLabel("命令详情:"))
        self._cmd_detail = QTextEdit()
        self._cmd_detail.setReadOnly(True)
        self._cmd_detail.setMaximumHeight(150)
        layout.addWidget(self._cmd_detail)

        # 快速发送按钮
        btn_layout = QHBoxLayout()
        self._cmd_send_btn = QPushButton("发送选中命令")
        self._cmd_send_btn.clicked.connect(self._on_send_selected_cmd)
        btn_layout.addWidget(self._cmd_send_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 初始化命令列表
        self._populate_commands()

        return widget

    def _populate_commands(self):
        """填充命令列表"""
        self._cmd_list.clear()
        for category, commands in GRBL_COMMANDS.items():
            for cmd, desc in commands.items():
                item = QListWidgetItem(f"{cmd} - {desc}")
                item.setData(Qt.ItemDataRole.UserRole, cmd)
                self._cmd_list.addItem(item)

    def _on_cmd_search_changed(self, text: str):
        """命令搜索改变"""
        self._cmd_list.clear()
        if not text.strip():
            self._populate_commands()
            return

        results = GrblCommandHelper.search_commands(text)
        for category, cmd, desc in results:
            item = QListWidgetItem(f"[{category}] {cmd} - {desc}")
            item.setData(Qt.ItemDataRole.UserRole, cmd)
            self._cmd_list.addItem(item)

    def _on_cmd_selected(self, item: QListWidgetItem):
        """命令被选中"""
        cmd = item.data(Qt.ItemDataRole.UserRole)
        desc = GrblCommandHelper.get_command_description(cmd)
        self._cmd_detail.setText(f"命令: {cmd}\n\n说明: {desc}")

    def _on_send_selected_cmd(self):
        """发送选中的命令"""
        current = self._cmd_list.currentItem()
        if not current:
            self.log_warning("请先选中一个命令")
            return

        cmd = current.data(Qt.ItemDataRole.UserRole)
        self._send_command(cmd)

    def _create_tk_ui(self) -> None:
        """创建 tkinter 界面（简化版）"""
        # 简化的 tkinter 实现
        label = tk.Label(self, text="Grbl CNC 控制模块 (需要 PyQt6 以获得完整功能)")
        label.pack(pady=20)

    # 事件处理方法
    def _on_conn_type_changed(self, index: int) -> None:
        """连接类型改变"""
        if index == 0:  # 串口
            self._serial_group.show()
            self._wifi_group.hide()
        else:  # WiFi
            self._serial_group.hide()
            self._wifi_group.show()

    def _refresh_ports(self) -> None:
        """刷新串口列表"""
        try:
            from linktunnel.serial_util import list_serial_ports

            ports = list_serial_ports()
            self._port_combo.clear()
            for p in ports:
                self._port_combo.addItem(f"{p.device} - {p.description}")
            self.log_info(f"发现 {len(ports)} 个串口")
        except Exception as e:
            self.log_error(f"刷新串口失败: {e}")

    def _on_connect(self) -> None:
        """连接设备"""
        try:
            from linktunnel.grbl.client import open_grbl_serial

            if self._conn_type.currentIndex() == 0:  # 串口
                port_text = self._port_combo.currentText()
                port = port_text.split(" - ")[0] if " - " in port_text else port_text
                baud = int(self._baud_combo.currentText())
                self._serial = open_grbl_serial(port=port, url=None, baud=baud, timeout=1.0)
            else:  # WiFi
                host = self._host_entry.text()
                port = self._telnet_port.text()
                url = f"socket://{host}:{port}"
                self._serial = open_grbl_serial(port=None, url=url, baud=115200, timeout=1.0)

            self._connect_btn.setEnabled(False)
            self._disconnect_btn.setEnabled(True)
            self._reset_btn.setEnabled(True)
            self._conn_status.setText("已连接")
            self.log_info("Grbl 设备连接成功")

        except Exception as e:
            self.log_error(f"连接失败: {e}")
            self._conn_status.setText(f"连接失败: {e}")

    def _on_disconnect(self) -> None:
        """断开连接"""
        try:
            if self._serial:
                self._serial.close()
                self._serial = None

            self._connect_btn.setEnabled(True)
            self._disconnect_btn.setEnabled(False)
            self._reset_btn.setEnabled(False)
            self._conn_status.setText("未连接")
            self.log_info("已断开连接")

        except Exception as e:
            self.log_error(f"断开连接失败: {e}")

    def _on_reset(self) -> None:
        """复位设备"""
        if not self._serial:
            self.log_warning("未连接设备")
            return

        try:
            self._serial.write(b"\x18")  # Ctrl+X
            self.log_info("已发送复位命令")
        except Exception as e:
            self.log_error(f"复位失败: {e}")

    def _on_query_status(self) -> None:
        """查询状态"""
        self._send_realtime("?")

    def _send_realtime(self, cmd: str) -> None:
        """发送实时命令"""
        if not self._serial:
            self.log_warning("未连接设备")
            return

        try:
            from linktunnel.grbl.monitor import send_realtime

            send_realtime(self._serial, cmd)
            self.log_info(f"已发送实时命令: {cmd}")
        except Exception as e:
            self.log_error(f"发送实时命令失败: {e}")

    def _browse_gcode_file(self) -> None:
        """浏览 G代码文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 G代码文件", "", "G-code Files (*.nc *.gcode *.txt);;All Files (*)"
        )
        if file_path:
            self._gcode_file.setText(file_path)

    def _on_start_stream(self) -> None:
        """开始传输"""
        if not self._serial:
            self.log_warning("未连接设备")
            return

        file_path = self._gcode_file.text()
        if not file_path or not Path(file_path).exists():
            self.log_warning("请选择有效的 G代码文件")
            return

        self._start_stream_btn.setEnabled(False)
        self._pause_stream_btn.setEnabled(True)
        self._stop_stream_btn.setEnabled(True)

        # 在后台线程执行
        self._stop_event.clear()
        self._stream_thread = threading.Thread(
            target=self._stream_worker, args=(file_path,), daemon=True
        )
        self._stream_thread.start()

    def _on_pause_stream(self) -> None:
        """暂停传输"""
        self._send_realtime("!")

    def _on_stop_stream(self) -> None:
        """停止传输"""
        self._stop_event.set()
        self._start_stream_btn.setEnabled(True)
        self._pause_stream_btn.setEnabled(False)
        self._stop_stream_btn.setEnabled(False)

    def _stream_worker(self, file_path: str) -> None:
        """流式传输工作线程"""
        try:
            from linktunnel.grbl.stream_job import stream_gcode_file

            def on_send(line: str):
                self._result_queue.put(("stream_send", line))

            def on_rx(line: str):
                self._result_queue.put(("stream_rx", line))

            def on_error(line: str, responses: list[str]):
                self._result_queue.put(("stream_error", line, responses))

            result = stream_gcode_file(
                self._serial,
                file_path,
                timeout_per_line=10.0,
                on_send=on_send,
                on_rx=on_rx,
                on_error=on_error,
            )

            self._result_queue.put(("stream_done", result))

        except Exception as e:
            self._result_queue.put(("stream_exception", str(e)))

    def _on_send_manual_cmd(self) -> None:
        """发送手动命令"""
        cmd = self._manual_cmd.text().strip()
        if not cmd:
            return

        self._send_command(cmd)
        self._manual_cmd.clear()

    def _send_command(self, cmd: str) -> None:
        """发送命令"""
        if not self._serial:
            self.log_warning("未连接设备")
            return

        try:
            from linktunnel.grbl.protocol import send_line, read_until_ok

            send_line(self._serial, cmd)
            self._manual_log.append(f"> {cmd}")

            responses = read_until_ok(self._serial, timeout_s=5.0)
            for resp in responses:
                self._manual_log.append(f"< {resp}")

            self.log_info(f"命令已发送: {cmd}")

        except Exception as e:
            self.log_error(f"发送命令失败: {e}")
            self._manual_log.append(f"错误: {e}")

    def _poll_queue(self) -> None:
        """轮询结果队列"""
        try:
            while True:
                msg = self._result_queue.get_nowait()
                msg_type = msg[0]

                if msg_type == "stream_send":
                    self._stream_log.append(f"> {msg[1]}")
                elif msg_type == "stream_rx":
                    self._stream_log.append(f"< {msg[1]}")
                elif msg_type == "stream_error":
                    self._stream_log.append(f"ERROR: {msg[1]}")
                elif msg_type == "stream_done":
                    result = msg[1]
                    if result == 0:
                        self.log_info("G代码传输完成")
                    else:
                        self.log_warning("G代码传输完成，但有错误")
                    self._on_stop_stream()
                elif msg_type == "stream_exception":
                    self.log_error(f"传输异常: {msg[1]}")
                    self._on_stop_stream()

        except queue.Empty:
            pass

    def get_occupied_resources(self) -> list[str]:
        """返回占用的资源"""
        if self._serial:
            return [f"serial:{self._serial.port}"]
        return []

    def stop(self) -> None:
        """停止模块"""
        self._stop_event.set()
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
        self.log_info("Grbl 模块已停止")
