"""帮助系统管理器 - 提供帮助文档和快捷键列表"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    pass

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QKeySequence
    from PyQt6.QtWidgets import (
        QDialog,
        QDialogButtonBox,
        QLabel,
        QTableWidget,
        QTableWidgetItem,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class HelpManager:
    """帮助系统管理器"""

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化帮助管理器

        Args:
            parent: 父窗口
        """
        self.parent = parent

    def show_shortcuts(self) -> None:
        """显示快捷键列表"""
        if not PYQT_AVAILABLE:
            print("[HELP] 快捷键列表")
            return

        dialog = ShortcutsDialog(self.parent)
        dialog.exec()

    def show_user_manual(self) -> None:
        """显示用户手册"""
        if not PYQT_AVAILABLE:
            print("[HELP] 用户手册")
            return

        dialog = UserManualDialog(self.parent)
        dialog.exec()

    def show_module_help(self, module_name: str) -> None:
        """显示模块帮助

        Args:
            module_name: 模块名称
        """
        if not PYQT_AVAILABLE:
            print(f"[HELP] {module_name} 模块帮助")
            return

        dialog = ModuleHelpDialog(self.parent, module_name)
        dialog.exec()

    def open_online_docs(self) -> None:
        """打开在线文档"""
        import webbrowser

        url = "https://github.com/your-repo/linktunnel/wiki"
        webbrowser.open(url)

    def open_github_repo(self) -> None:
        """打开 GitHub 仓库"""
        import webbrowser

        url = "https://github.com/your-repo/linktunnel"
        webbrowser.open(url)


class ShortcutsDialog(QDialog):
    """快捷键列表对话框"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("快捷键列表")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 说明标签
        label = QLabel("以下是 linktunnel Unified GUI 的快捷键列表：")
        layout.addWidget(label)

        # 快捷键表格
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["快捷键", "功能"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # 添加快捷键
        shortcuts = [
            ("Ctrl+T", "切换主题（浅色/深色）"),
            ("Ctrl+Q", "退出应用程序"),
            ("Ctrl+W", "关闭当前窗口"),
            ("F5", "刷新当前模块（如适用）"),
            ("Ctrl+1", "切换到串口工具模块"),
            ("Ctrl+2", "切换到网络中继模块"),
            ("Ctrl+3", "切换到代理管理模块"),
            ("Ctrl+4", "切换到 Grbl CNC 模块"),
            ("Ctrl+5", "切换到 BLE 扫描模块"),
            ("Ctrl+6", "切换到 I2C 扫描模块"),
            ("Ctrl+L", "清空日志查看器"),
            ("Ctrl+F", "在日志中搜索"),
            ("Ctrl+S", "保存当前配置"),
            ("F1", "显示帮助"),
        ]

        table.setRowCount(len(shortcuts))
        for i, (key, desc) in enumerate(shortcuts):
            table.setItem(i, 0, QTableWidgetItem(key))
            table.setItem(i, 1, QTableWidgetItem(desc))

        layout.addWidget(table)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class UserManualDialog(QDialog):
    """用户手册对话框"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("用户手册")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 文本浏览器
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_manual_html())
        layout.addWidget(browser)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _get_manual_html(self) -> str:
        """获取用户手册 HTML"""
        return """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 20px; }
                h3 { color: #7f8c8d; }
                .module { background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .tip { background-color: #d5f4e6; padding: 10px; margin: 10px 0; border-left: 4px solid #27ae60; }
                .warning { background-color: #ffeaa7; padding: 10px; margin: 10px 0; border-left: 4px solid #fdcb6e; }
                code { background-color: #f8f9fa; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
            </style>
        </head>
        <body>
            <h1>linktunnel Unified GUI 用户手册</h1>
            
            <h2>📖 简介</h2>
            <p>linktunnel Unified GUI 是一个统一的图形界面，整合了 linktunnel 的所有功能模块，
            包括串口工具、网络中继、代理管理、Grbl CNC 控制、BLE 扫描和 I2C 扫描。</p>
            
            <h2>🚀 快速开始</h2>
            <ol>
                <li>从左侧导航栏选择要使用的功能模块</li>
                <li>在模块界面中配置参数</li>
                <li>点击"启动"或相应的操作按钮</li>
                <li>在日志查看器中查看操作日志</li>
            </ol>
            
            <h2>📦 功能模块</h2>
            
            <div class="module">
                <h3>🔌 串口工具</h3>
                <p><strong>功能</strong>：串口桥接和调试终端</p>
                <ul>
                    <li><strong>串口桥接</strong>：连接两个串口设备进行双向通信</li>
                    <li><strong>调试终端</strong>：发送和接收串口数据，支持多种编码</li>
                </ul>
                <p><strong>使用场景</strong>：串口设备调试、数据转发、协议分析</p>
            </div>
            
            <div class="module">
                <h3>🌐 网络中继</h3>
                <p><strong>功能</strong>：TCP/UDP 透明中继</p>
                <ul>
                    <li><strong>TCP 中继</strong>：转发 TCP 连接，支持 IPv4/IPv6</li>
                    <li><strong>UDP 中继</strong>：转发 UDP 数据包</li>
                </ul>
                <p><strong>使用场景</strong>：端口转发、网络调试、流量监控</p>
            </div>
            
            <div class="module">
                <h3>🔐 代理管理</h3>
                <p><strong>功能</strong>：Mihomo/Clash 代理管理</p>
                <ul>
                    <li><strong>节点管理</strong>：查看和切换代理节点</li>
                    <li><strong>延迟测试</strong>：测试节点延迟</li>
                    <li><strong>浏览器控制台</strong>：打开 Yacd 或本地 UI</li>
                </ul>
                <p><strong>使用场景</strong>：代理服务管理、节点优化</p>
            </div>
            
            <div class="module">
                <h3>🔧 Grbl CNC</h3>
                <p><strong>功能</strong>：CNC 设备控制</p>
                <ul>
                    <li><strong>设备连接</strong>：通过串口或 WiFi 连接 CNC 设备</li>
                    <li><strong>状态监控</strong>：实时查看机器状态和位置</li>
                    <li><strong>G代码传输</strong>：流式传输 G代码文件</li>
                </ul>
                <p><strong>使用场景</strong>：CNC 雕刻、3D 打印控制</p>
            </div>
            
            <div class="module">
                <h3>📡 BLE 扫描</h3>
                <p><strong>功能</strong>：蓝牙设备扫描</p>
                <ul>
                    <li><strong>设备发现</strong>：扫描附近的 BLE 设备</li>
                    <li><strong>信号强度</strong>：显示 RSSI 值</li>
                </ul>
                <p><strong>使用场景</strong>：BLE 设备调试、信号测试</p>
                <div class="warning">
                    <strong>注意</strong>：需要安装 bleak 库：<code>pip install 'linktunnel[ble]'</code>
                </div>
            </div>
            
            <div class="module">
                <h3>🔍 I2C 扫描</h3>
                <p><strong>功能</strong>：I2C 总线扫描（仅 Linux）</p>
                <ul>
                    <li><strong>总线扫描</strong>：扫描 I2C 总线上的设备</li>
                    <li><strong>地址网格</strong>：可视化显示设备地址</li>
                </ul>
                <p><strong>使用场景</strong>：I2C 设备调试、地址查找</p>
                <div class="warning">
                    <strong>注意</strong>：仅支持 Linux 平台，需要安装 smbus2 库：
                    <code>pip install 'linktunnel[i2c]'</code>
                </div>
            </div>
            
            <h2>⚙️ 设置</h2>
            
            <h3>主题</h3>
            <p>通过 <strong>视图 → 主题</strong> 菜单可以切换主题：</p>
            <ul>
                <li><strong>浅色</strong>：明亮清爽，适合白天使用</li>
                <li><strong>深色</strong>：低亮度护眼，适合夜间使用</li>
                <li><strong>跟随系统</strong>：自动跟随系统主题设置</li>
            </ul>
            <div class="tip">
                <strong>提示</strong>：使用快捷键 <code>Ctrl+T</code> 可以快速切换主题
            </div>
            
            <h3>配置文件</h3>
            <p>配置文件位置：</p>
            <ul>
                <li><strong>Windows</strong>：<code>%LOCALAPPDATA%\\linktunnel\\unified-gui\\config.json</code></li>
                <li><strong>macOS</strong>：<code>~/Library/Application Support/linktunnel/unified-gui/config.json</code></li>
                <li><strong>Linux</strong>：<code>~/.config/linktunnel/unified-gui/config.json</code></li>
            </ul>
            
            <h3>日志文件</h3>
            <p>日志文件位置：</p>
            <ul>
                <li><strong>Windows</strong>：<code>%LOCALAPPDATA%\\linktunnel\\unified-gui\\logs\\</code></li>
                <li><strong>macOS</strong>：<code>~/Library/Logs/linktunnel/unified-gui/</code></li>
                <li><strong>Linux</strong>：<code>~/.local/share/linktunnel/unified-gui/logs/</code></li>
            </ul>
            
            <h2>❓ 常见问题</h2>
            
            <h3>Q: 串口列表为空？</h3>
            <p>A: 请确保：</p>
            <ul>
                <li>串口设备已正确连接</li>
                <li>设备驱动已安装</li>
                <li>在 macOS 上可能需要授予权限</li>
            </ul>
            
            <h3>Q: BLE 扫描不可用？</h3>
            <p>A: 请安装 bleak 库：<code>pip install 'linktunnel[ble]'</code></p>
            
            <h3>Q: I2C 扫描不可用？</h3>
            <p>A: 请确保：</p>
            <ul>
                <li>使用 Linux 系统</li>
                <li>已安装 smbus2 库：<code>pip install 'linktunnel[i2c]'</code></li>
                <li>用户在 i2c 组中：<code>sudo usermod -a -G i2c $USER</code></li>
            </ul>
            
            <h2>🔗 更多资源</h2>
            <ul>
                <li><a href="https://github.com/your-repo/linktunnel">GitHub 仓库</a></li>
                <li><a href="https://github.com/your-repo/linktunnel/wiki">在线文档</a></li>
                <li><a href="https://github.com/your-repo/linktunnel/issues">问题反馈</a></li>
            </ul>
            
            <div class="tip">
                <strong>提示</strong>：按 <code>F1</code> 可以随时打开帮助
            </div>
        </body>
        </html>
        """


class ModuleHelpDialog(QDialog):
    """模块帮助对话框"""

    def __init__(self, parent: Optional[QWidget], module_name: str):
        super().__init__(parent)
        self.module_name = module_name
        self.setWindowTitle(f"{module_name} 模块帮助")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 文本浏览器
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_module_help_html())
        layout.addWidget(browser)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _get_module_help_html(self) -> str:
        """获取模块帮助 HTML"""
        help_content = {
            "serial": """
                <h2>🔌 串口工具模块</h2>
                <h3>功能</h3>
                <ul>
                    <li><strong>串口桥接</strong>：连接两个串口设备进行双向通信</li>
                    <li><strong>调试终端</strong>：发送和接收串口数据</li>
                </ul>
                <h3>使用方法</h3>
                <ol>
                    <li>点击"刷新串口列表"查看可用串口</li>
                    <li>选择"串口桥接"或"调试终端"标签页</li>
                    <li>配置串口参数（端口、波特率等）</li>
                    <li>点击"启动"开始操作</li>
                </ol>
            """,
            "network": """
                <h2>🌐 网络中继模块</h2>
                <h3>功能</h3>
                <ul>
                    <li><strong>TCP 中继</strong>：转发 TCP 连接</li>
                    <li><strong>UDP 中继</strong>：转发 UDP 数据包</li>
                </ul>
                <h3>使用方法</h3>
                <ol>
                    <li>选择"TCP 中继"或"UDP 中继"标签页</li>
                    <li>配置监听地址和端口</li>
                    <li>配置目标地址和端口</li>
                    <li>点击"启动中继"</li>
                </ol>
            """,
            "proxy": """
                <h2>🔐 代理管理模块</h2>
                <h3>功能</h3>
                <ul>
                    <li><strong>节点管理</strong>：查看和切换代理节点</li>
                    <li><strong>延迟测试</strong>：测试节点延迟</li>
                    <li><strong>浏览器控制台</strong>：打开 Yacd 或本地 UI</li>
                </ul>
                <h3>使用方法</h3>
                <ol>
                    <li>输入 API 地址（默认：http://127.0.0.1:9090）</li>
                    <li>点击"连接/刷新"</li>
                    <li>在节点树中双击节点切换</li>
                    <li>或选中节点后点击"应用节点"</li>
                </ol>
            """,
            "grbl": """
                <h2>🔧 Grbl CNC 模块</h2>
                <h3>功能</h3>
                <ul>
                    <li><strong>设备连接</strong>：通过串口或 WiFi 连接</li>
                    <li><strong>状态监控</strong>：实时查看机器状态</li>
                    <li><strong>G代码传输</strong>：流式传输 G代码文件</li>
                </ul>
                <h3>使用方法</h3>
                <ol>
                    <li>选择连接类型（串口或 WiFi）</li>
                    <li>配置连接参数</li>
                    <li>点击"连接"</li>
                    <li>在"G代码传输"标签页选择文件并传输</li>
                </ol>
            """,
            "ble": """
                <h2>📡 BLE 扫描模块</h2>
                <h3>功能</h3>
                <ul>
                    <li><strong>设备扫描</strong>：扫描附近的 BLE 设备</li>
                    <li><strong>信号强度</strong>：显示 RSSI 值</li>
                </ul>
                <h3>使用方法</h3>
                <ol>
                    <li>选择扫描超时时间</li>
                    <li>点击"开始扫描"</li>
                    <li>查看扫描结果</li>
                    <li>可选：点击"导出结果"保存</li>
                </ol>
                <p><strong>注意</strong>：需要安装 bleak 库</p>
            """,
            "i2c": """
                <h2>🔍 I2C 扫描模块</h2>
                <h3>功能</h3>
                <ul>
                    <li><strong>总线扫描</strong>：扫描 I2C 总线上的设备</li>
                    <li><strong>地址网格</strong>：可视化显示设备地址</li>
                </ul>
                <h3>使用方法</h3>
                <ol>
                    <li>选择 I2C 总线编号</li>
                    <li>点击"扫描"</li>
                    <li>查看地址网格（绿色表示找到设备）</li>
                    <li>可选：点击"导出结果"保存</li>
                </ol>
                <p><strong>注意</strong>：仅支持 Linux 平台，需要安装 smbus2 库</p>
            """,
        }

        content = help_content.get(
            self.module_name,
            f"<h2>{self.module_name} 模块</h2><p>暂无帮助文档</p>",
        )

        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h3 {{ color: #34495e; margin-top: 15px; }}
                ul, ol {{ margin-left: 20px; }}
                li {{ margin: 5px 0; }}
                strong {{ color: #2980b9; }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
