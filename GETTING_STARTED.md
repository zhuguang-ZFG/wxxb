# linktunnel 统一 GUI - 快速入门指南

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础安装（必需）
pip install -e .

# 安装 GUI 依赖（推荐）
pip install 'linktunnel[gui]'

# 完整安装（包含所有可选功能）
pip install 'linktunnel[gui-full]'
```

### 2. 启动应用

```bash
# 方式 1: 使用 Python 模块
python -m linktunnel.unified_gui

# 方式 2: 使用命令行入口
linktunnel-unified

# 方式 3: 在虚拟环境中
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
python -m linktunnel.unified_gui
```

### 3. 界面概览

```
┌─────────────────────────────────────────────────────────┐
│ linktunnel Unified GUI                          [_][□][X]│
├──────────────┬──────────────────────────────────────────┤
│ 导航栏       │ 模块内容区域                             │
│              │                                          │
│ 串口工具     │ [当前选中模块的界面]                     │
│ 网络中继     │                                          │
│ 代理管理     │                                          │
│ Grbl CNC     │                                          │
│ BLE 扫描     │                                          │
│ I2C 扫描     │                                          │
│              │                                          │
├──────────────┴──────────────────────────────────────────┤
│ 日志查看器                                              │
│ [INFO] 应用程序启动                                     │
│ [INFO] 发现 3 个串口                                    │
└─────────────────────────────────────────────────────────┘
│ 状态栏: 就绪                                            │
└─────────────────────────────────────────────────────────┘
```

## 📦 功能模块

### 1. 串口工具 🔌

**功能**：
- 串口列表刷新
- 串口桥接（双端转发）
- 调试终端（发送/接收）

**使用场景**：
- 连接两个串口设备进行通信
- 调试串口设备
- 查看串口数据

**快速操作**：
1. 点击"串口工具"
2. 点击"刷新串口列表"
3. 选择"串口桥接"或"调试终端"标签页
4. 配置参数后点击"启动"

### 2. 网络中继 🌐

**功能**：
- TCP 中继（支持 IPv4/IPv6）
- UDP 中继
- 数据流日志

**使用场景**：
- 端口转发
- 网络调试
- 流量监控

**快速操作**：
1. 点击"网络中继"
2. 选择"TCP 中继"或"UDP 中继"标签页
3. 配置监听地址和目标地址
4. 点击"启动中继"

### 3. 代理管理 🔐

**功能**：
- Mihomo/Clash 代理管理
- 节点切换
- 延迟测试
- 浏览器控制台

**使用场景**：
- 管理本地代理服务
- 切换代理节点
- 测试节点延迟

**快速操作**：
1. 点击"代理管理"
2. 输入 API 地址（默认：http://127.0.0.1:9090）
3. 点击"连接/刷新"
4. 在节点树中双击节点切换

### 4. Grbl CNC 🔧

**功能**：
- CNC 设备连接（串口/WiFi）
- 实时状态监控
- G 代码流式传输
- 手动控制

**使用场景**：
- 控制 CNC 雕刻机
- 发送 G 代码文件
- 监控机器状态

**快速操作**：
1. 点击"Grbl CNC"
2. 选择连接类型（串口或 WiFi）
3. 配置连接参数
4. 点击"连接"

### 5. BLE 扫描 📡

**功能**：
- BLE 设备扫描
- 信号强度显示
- 结果导出

**使用场景**：
- 发现附近的蓝牙设备
- 查看设备信息
- 调试 BLE 应用

**快速操作**：
1. 点击"BLE 扫描"
2. 选择扫描超时时间
3. 点击"开始扫描"
4. 查看扫描结果

**注意**：需要安装 bleak 库：`pip install 'linktunnel[ble]'`

### 6. I2C 扫描 🔍

**功能**：
- I2C 总线扫描（仅 Linux）
- 地址网格显示
- 结果导出

**使用场景**：
- 发现 I2C 设备
- 查看设备地址
- 调试 I2C 总线

**快速操作**：
1. 点击"I2C 扫描"
2. 选择 I2C 总线编号
3. 点击"扫描"
4. 查看地址网格

**注意**：
- 仅支持 Linux 平台
- 需要安装 smbus2 库：`pip install 'linktunnel[i2c]'`
- 需要权限：`sudo usermod -a -G i2c $USER`

## ⚙️ 配置文件

### 配置文件位置

- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\config.json`
- **macOS**: `~/Library/Application Support/linktunnel/unified-gui/config.json`
- **Linux**: `~/.config/linktunnel/unified-gui/config.json`

### 日志文件位置

- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\logs\`
- **macOS**: `~/Library/Logs/linktunnel/unified-gui/`
- **Linux**: `~/.local/share/linktunnel/unified-gui/logs/`

### 配置示例

```json
{
  "log_level": "INFO",
  "last_active_module": "serial",
  "window": {
    "width": 1200,
    "height": 800,
    "x": 100,
    "y": 100
  },
  "modules": {
    "serial": {
      "last_port": "COM3",
      "last_baud": 115200
    },
    "proxy": {
      "api": "http://127.0.0.1:9090",
      "auto_refresh": true,
      "refresh_interval": 5
    }
  }
}
```

## 🔧 故障排除

### Q: 提示"未安装 PyQt6"

**A**: 运行以下命令安装：
```bash
pip install PyQt6
```

### Q: 串口列表为空

**A**: 
1. 确保有串口设备连接
2. 检查设备驱动是否安装
3. 在 macOS 上可能需要授予权限

### Q: BLE 扫描不可用

**A**: 安装 bleak 库：
```bash
pip install 'linktunnel[ble]'
```

### Q: I2C 扫描不可用

**A**: 
1. 确保使用 Linux 系统
2. 安装 smbus2 库：`pip install 'linktunnel[i2c]'`
3. 添加用户到 i2c 组：`sudo usermod -a -G i2c $USER`
4. 重新登录使权限生效

### Q: 代理管理连接失败

**A**: 
1. 确保 Mihomo/Clash 正在运行
2. 检查 API 地址是否正确
3. 检查 Secret 是否正确（如果设置了）

### Q: Grbl 连接失败

**A**: 
1. 确保串口未被其他程序占用
2. 检查波特率是否正确（通常为 115200）
3. 检查设备是否正确连接

## 📚 更多资源

- **完整文档**: `IMPLEMENTATION_SUMMARY.md`
- **任务列表**: `.kiro/specs/unified-gui/tasks.md`
- **需求文档**: `.kiro/specs/unified-gui/requirements.md`
- **设计文档**: `.kiro/specs/unified-gui/design.md`

## 🆘 获取帮助

如有问题或建议，请：
1. 查看日志文件（见上述日志文件位置）
2. 查看项目文档
3. 提交 Issue 到 GitHub 仓库

## 🎉 开始使用

现在你已经了解了基本操作，可以开始使用 linktunnel 统一 GUI 了！

```bash
# 启动应用
python -m linktunnel.unified_gui
```

祝使用愉快！ 🚀

---

**版本**: 0.2.0  
**更新日期**: 2026-04-13
