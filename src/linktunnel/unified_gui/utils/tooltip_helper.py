"""工具提示助手 - 为控件添加友好的工具提示"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget


class TooltipHelper:
    """工具提示助手"""

    # 通用工具提示
    TOOLTIPS = {
        # 按钮
        "refresh": "刷新列表或重新加载数据",
        "start": "开始操作",
        "stop": "停止当前操作",
        "pause": "暂停当前操作",
        "resume": "恢复暂停的操作",
        "connect": "连接到设备或服务",
        "disconnect": "断开连接",
        "browse": "浏览并选择文件",
        "export": "导出数据到文件",
        "import": "从文件导入数据",
        "save": "保存当前配置",
        "load": "加载配置",
        "clear": "清空内容",
        "search": "搜索内容",
        "filter": "过滤显示内容",
        "apply": "应用更改",
        "cancel": "取消操作",
        "close": "关闭窗口",
        # 输入框
        "port": "输入端口号（1-65535）",
        "ip_address": "输入 IP 地址（支持 IPv4 和 IPv6）",
        "url": "输入完整的 URL 地址",
        "file_path": "输入或选择文件路径",
        "timeout": "设置超时时间（秒）",
        # 复选框
        "auto_refresh": "启用后自动刷新数据",
        "hex_mode": "以十六进制格式显示数据",
        "timestamp": "在日志中显示时间戳",
        "auto_scroll": "自动滚动到最新内容",
    }

    # 模块特定工具提示
    MODULE_TOOLTIPS = {
        "serial": {
            "port_combo": "选择要使用的串口设备",
            "baud_combo": "选择波特率（常用：115200、9600）",
            "encoding_combo": "选择字符编码（UTF-8、ASCII、GBK）",
            "bridge_start": "开始串口桥接，连接两个串口设备",
            "terminal_send": "发送数据到串口",
        },
        "network": {
            "listen_address": "输入监听地址（0.0.0.0 表示所有接口）",
            "listen_port": "输入监听端口号",
            "target_address": "输入目标服务器地址",
            "target_port": "输入目标服务器端口号",
            "tcp_start": "启动 TCP 中继服务",
            "udp_start": "启动 UDP 中继服务",
        },
        "proxy": {
            "api_entry": "输入 Mihomo/Clash API 地址（如：http://127.0.0.1:9090）",
            "secret_entry": "输入 API Secret（如果设置了）",
            "from_profile": "从 profile 的 config.yaml 自动读取配置",
            "connect_btn": "连接到代理服务并获取信息",
            "mode_combo": "选择代理模式（rule/global/direct）",
            "apply_mode": "应用选择的代理模式",
            "test_delay": "测试选中节点的延迟",
            "close_connections": "关闭所有活动连接",
            "open_dashboard": "在浏览器中打开控制台",
        },
        "grbl": {
            "conn_type": "选择连接类型（串口或 WiFi）",
            "port_combo": "选择 Grbl 设备的串口",
            "host_entry": "输入 Grbl 设备的 IP 地址",
            "connect_btn": "连接到 Grbl 设备",
            "reset_btn": "发送复位命令（Ctrl+X）",
            "query_status": "查询当前机器状态",
            "gcode_file": "选择要传输的 G代码文件",
            "start_stream": "开始流式传输 G代码",
        },
        "ble": {
            "timeout_combo": "选择扫描超时时间",
            "start_scan": "开始扫描附近的 BLE 设备",
            "stop_scan": "停止当前扫描",
            "export_results": "将扫描结果导出到文件",
        },
        "i2c": {
            "bus_combo": "选择 I2C 总线编号",
            "scan_btn": "扫描 I2C 总线上的设备",
            "export_results": "将扫描结果导出到文件",
        },
    }

    @classmethod
    def set_tooltip(cls, widget: QWidget, tooltip_key: str, module: str = None) -> None:
        """为控件设置工具提示

        Args:
            widget: Qt 控件
            tooltip_key: 工具提示键
            module: 模块名称（可选）
        """
        tooltip = None

        # 先查找模块特定的工具提示
        if module and module in cls.MODULE_TOOLTIPS:
            tooltip = cls.MODULE_TOOLTIPS[module].get(tooltip_key)

        # 如果没找到，使用通用工具提示
        if not tooltip:
            tooltip = cls.TOOLTIPS.get(tooltip_key)

        # 设置工具提示
        if tooltip:
            widget.setToolTip(tooltip)

    @classmethod
    def set_custom_tooltip(cls, widget: QWidget, tooltip: str) -> None:
        """为控件设置自定义工具提示

        Args:
            widget: Qt 控件
            tooltip: 工具提示文本
        """
        widget.setToolTip(tooltip)
