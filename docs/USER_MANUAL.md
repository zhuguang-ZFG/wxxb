# linktunnel Unified GUI - 用户手册

**版本**: 0.3.0  
**更新日期**: 2026-04-13

---

## 📖 目录

1. [简介](#简介)
2. [系统要求](#系统要求)
3. [安装指南](#安装指南)
4. [快速入门](#快速入门)
5. [功能模块详解](#功能模块详解)
6. [常见问题](#常见问题)
7. [故障排除](#故障排除)
8. [技术支持](#技术支持)

---

## 简介

linktunnel Unified GUI 是一个统一的图形界面应用程序，整合了 linktunnel 项目的所有功能，提供友好的用户界面和强大的功能。

### 主要特性

- 🔌 **串口工具** - 串口桥接和调试终端
- 🌐 **网络中继** - TCP/UDP 透明中继
- 🔄 **代理管理** - Mihomo/Clash 代理控制
- 🤖 **Grbl CNC** - CNC 设备控制和 G 代码传输
- 📡 **BLE 扫描** - 蓝牙设备发现和 RSSI 测量
- 🔍 **I2C 扫描** - I2C 总线扫描（Linux）
- 🎨 **主题系统** - 浅色/深色/系统主题
- 📊 **性能优化** - 流畅的用户体验

---

## 系统要求

### 最低要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+) |
| Python | 3.8 或更高版本 |
| 内存 | 2GB RAM |
| 磁盘空间 | 100MB 可用空间 |

### 推荐配置

| 项目 | 推荐 |
|------|------|
| 操作系统 | Windows 11, macOS 12+, Linux (Ubuntu 22.04+) |
| Python | 3.10 或更高版本 |
| 内存 | 4GB RAM 或更多 |
| 磁盘空间 | 500MB 可用空间 |

### 依赖说明

**必需依赖**:
- PyQt6 (GUI 框架)
- pyserial (串口通信)

**可选依赖**:
- bleak (BLE 蓝牙扫描)
- smbus2 (I2C 扫描，仅 Linux)
- psutil (性能监控)

---

## 安装指南

### 方式 1: 使用 pip 安装（推荐）

#### 基础安装

```bash
pip install linktunnel
```

#### 安装 GUI 版本

```bash
pip install 'linktunnel[gui]'
```

#### 完整安装（包含所有可选功能）

```bash
pip install 'linktunnel[gui-full]'
```

### 方式 2: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/linktunnel.git
cd linktunnel

# 安装依赖
pip install -e '.[gui]'
```

### 验证安装

```bash
# 检查版本
python -m linktunnel.unified_gui --version

# 或者
linktunnel-unified --version
```

### 安装可选依赖

#### BLE 蓝牙扫描

```bash
pip install bleak
```

#### I2C 扫描（Linux）

```bash
pip install smbus2
```

#### 性能监控

```bash
pip install psutil
```

---

## 快速入门

### 启动应用程序

有三种方式启动应用程序：

#### 方式 1: 使用命令行入口

```bash
linktunnel-unified
```

#### 方式 2: 使用 Python 模块

```bash
python -m linktunnel.unified_gui
```

#### 方式 3: 在虚拟环境中

```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 启动应用
python -m linktunnel.unified_gui
```

### 首次使用

1. **启动应用** - 使用上述任一方式启动
2. **选择模块** - 在左侧导航栏选择要使用的功能模块
3. **配置参数** - 根据需要配置模块参数
4. **开始使用** - 点击"开始"或"连接"按钮

### 界面布局

```
┌─────────────────────────────────────────────────┐
│  菜单栏: 视图 | 帮助                              │
├──────────┬──────────────────────────────────────┤
│          │                                      │
│  导航栏  │        模块内容区域                   │
│          │                                      │
│  - 串口  │                                      │
│  - 网络  │                                      │
│  - 代理  │                                      │
│  - Grbl  │                                      │
│  - BLE   │                                      │
│  - I2C   │                                      │
│          │                                      │
├──────────┴──────────────────────────────────────┤
│              日志查看器                          │
├─────────────────────────────────────────────────┤
│  状态栏: 就绪                                    │
└─────────────────────────────────────────────────┘
```

---

## 功能模块详解

### 1. 串口工具模块

串口工具模块提供串口桥接和调试终端功能。

#### 1.1 串口桥接

**功能**: 连接两个串口设备，实现数据透明转发。

**使用步骤**:

1. 点击左侧导航栏的"串口工具"
2. 选择"串口桥接"标签页
3. 配置端口 A 和端口 B：
   - 选择串口
   - 设置波特率（默认 115200）
   - 设置数据位（默认 8）
   - 设置停止位（默认 1）
   - 设置校验位（默认 None）
4. 点击"开始桥接"按钮
5. 查看 RX/TX 统计和日志

**配置说明**:

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 串口 | 串口设备名称 | - |
| 波特率 | 通信速率 | 115200 |
| 数据位 | 数据位数 | 8 |
| 停止位 | 停止位数 | 1 |
| 校验位 | 校验方式 | None |
| 十六进制日志 | 以十六进制显示数据 | 关闭 |

**提示**:
- 点击"刷新"按钮更新串口列表
- 桥接运行时无法修改配置
- 使用"停止"按钮停止桥接

#### 1.2 调试终端

**功能**: 与串口设备进行交互式通信。

**使用步骤**:

1. 选择"调试终端"标签页
2. 配置串口参数（同桥接）
3. 点击"打开串口"按钮
4. 在发送区域输入数据
5. 点击"发送"按钮或按 Enter 键
6. 在接收区域查看响应

**高级功能**:

- **编码选择**: UTF-8、ASCII、GBK
- **十六进制模式**: 以十六进制显示/发送数据
- **时间戳**: 显示每条消息的时间
- **周期发送**: 定时自动发送数据
- **保存数据**: 导出接收的数据到文件

**快捷键**:

| 快捷键 | 功能 |
|--------|------|
| Enter | 发送数据 |
| Ctrl+L | 清空接收区 |
| Ctrl+S | 保存数据 |

### 2. 网络中继模块

网络中继模块提供 TCP/UDP 透明中继功能。

#### 2.1 TCP 中继

**功能**: 在两个 TCP 端点之间转发数据。

**使用步骤**:

1. 点击左侧导航栏的"网络中继"
2. 选择"TCP 中继"标签页
3. 配置监听地址和端口
4. 配置目标地址和端口
5. 点击"开始中继"按钮
6. 查看连接状态和流量统计

**配置说明**:

| 参数 | 说明 | 示例 |
|------|------|------|
| 监听地址 | 本地监听地址 | 0.0.0.0 |
| 监听端口 | 本地监听端口 | 8080 |
| 目标地址 | 远程目标地址 | 192.168.1.100 |
| 目标端口 | 远程目标端口 | 80 |
| IPv6 支持 | 启用 IPv6 | 关闭 |
| 十六进制日志 | 以十六进制显示数据 | 关闭 |

**使用场景**:

- 端口转发
- 流量监控
- 协议调试
- 网络测试

#### 2.2 UDP 中继

**功能**: 在两个 UDP 端点之间转发数据。

**使用步骤**:

1. 选择"UDP 中继"标签页
2. 配置参数（同 TCP）
3. 点击"开始中继"按钮

**注意事项**:
- UDP 是无连接协议
- 不保证数据送达
- 适合实时数据传输

### 3. 代理管理模块

代理管理模块用于管理 Mihomo/Clash 代理。

#### 3.1 连接代理

**使用步骤**:

1. 点击左侧导航栏的"代理管理"
2. 配置 API 地址和 Secret
3. 点击"连接"按钮
4. 查看连接状态

**配置说明**:

| 参数 | 说明 | 默认值 |
|------|------|--------|
| API 地址 | Clash API 地址 | http://127.0.0.1:9090 |
| Secret | API 密钥 | - |
| 从 profile 读取 | 自动读取配置 | 启用 |

#### 3.2 查看状态

连接成功后可以查看：

- 内核版本
- 运行模式（rule/global/direct）
- 监听端口
- 当前连接数

#### 3.3 管理节点

**功能**:

- 查看所有策略组和节点
- 筛选节点
- 测试节点延迟
- 切换节点

**使用步骤**:

1. 在节点列表中浏览节点
2. 使用筛选框搜索节点
3. 点击"测试延迟"测试所有节点
4. 双击节点或点击"应用"切换节点

**节点信息**:

- 节点名称
- 节点类型
- 延迟（ms）

#### 3.4 其他功能

- **切换模式**: rule/global/direct
- **关闭连接**: 关闭所有活动连接
- **打开控制台**: 在浏览器中打开 Yacd 控制台

### 4. Grbl CNC 控制模块

Grbl CNC 控制模块用于控制 CNC 设备。

#### 4.1 连接设备

**支持的连接方式**:

- 串口（USB）
- WiFi（Telnet）

**使用步骤**:

1. 点击左侧导航栏的"Grbl CNC"
2. 选择连接类型
3. 配置连接参数：
   - 串口：选择端口和波特率
   - WiFi：输入 IP 地址和端口
4. 点击"连接"按钮

#### 4.2 实时状态监控

连接成功后可以查看：

- 机器状态（Idle/Run/Hold/Alarm）
- 当前位置（X/Y/Z）
- 缓冲区信息

**实时命令**:

- **查询状态**: 获取当前状态
- **暂停**: 暂停当前操作
- **恢复**: 恢复操作

#### 4.3 G 代码传输

**功能**: 将 G 代码文件传输到 CNC 设备。

**使用步骤**:

1. 点击"浏览"选择 G 代码文件
2. 点击"开始传输"
3. 查看传输进度和日志
4. 使用"暂停"/"恢复"/"停止"控制传输

**支持的文件格式**:

- .nc
- .gcode
- .txt

#### 4.4 手动控制

**功能**: 手动发送 G 代码命令。

**使用步骤**:

1. 在命令输入框输入 G 代码
2. 点击"发送"或按 Enter
3. 查看响应日志

**快捷命令**:

- **回零**: $H
- **解锁**: $X
- **查看设置**: $$

### 5. BLE 蓝牙扫描模块

BLE 蓝牙扫描模块用于发现附近的蓝牙设备。

#### 5.1 扫描设备

**使用步骤**:

1. 点击左侧导航栏的"BLE 蓝牙扫描"
2. 设置扫描超时（默认 10 秒）
3. 点击"开始扫描"
4. 等待扫描完成
5. 查看扫描结果

**扫描结果**:

| 列 | 说明 |
|----|------|
| 设备名称 | 蓝牙设备名称 |
| 设备地址 | MAC 地址 |
| RSSI | 信号强度（dBm）|

#### 5.2 导出结果

点击"导出"按钮将结果保存为 CSV 文件。

**依赖要求**:

需要安装 bleak 库：
```bash
pip install bleak
```

### 6. I2C 扫描模块

I2C 扫描模块用于扫描 I2C 总线上的设备（仅 Linux）。

#### 6.1 扫描总线

**使用步骤**:

1. 点击左侧导航栏的"I2C 扫描"
2. 选择 I2C 总线编号（默认 1）
3. 点击"扫描"按钮
4. 查看扫描结果

**扫描结果**:

- 8x16 地址网格（0x00-0x7F）
- 找到的设备以绿色高亮显示
- 扫描日志显示详细信息

#### 6.2 导出结果

点击"导出"按钮将结果保存为文本文件。

**依赖要求**:

需要安装 smbus2 库：
```bash
pip install smbus2
```

**平台要求**: 仅支持 Linux

---

## 常见问题

### 安装相关

#### Q1: 如何安装 PyQt6？

**A**: PyQt6 会在安装 GUI 版本时自动安装：

```bash
pip install 'linktunnel[gui]'
```

如果需要单独安装：

```bash
pip install PyQt6
```

#### Q2: 安装时出现权限错误怎么办？

**A**: 使用 `--user` 参数安装到用户目录：

```bash
pip install --user 'linktunnel[gui]'
```

或者使用虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
pip install 'linktunnel[gui]'
```

#### Q3: 如何更新到最新版本？

**A**: 使用 `--upgrade` 参数：

```bash
pip install --upgrade 'linktunnel[gui]'
```

### 使用相关

#### Q4: 找不到串口设备怎么办？

**A**: 检查以下几点：

1. 确认设备已连接
2. 检查设备驱动是否安装
3. 点击"刷新"按钮更新列表
4. 在 Linux 上检查用户权限：
   ```bash
   sudo usermod -a -G dialout $USER
   ```
   然后重新登录

#### Q5: 代理连接失败怎么办？

**A**: 检查以下几点：

1. 确认 Mihomo/Clash 正在运行
2. 检查 API 地址是否正确
3. 检查 Secret 是否正确
4. 检查防火墙设置

#### Q6: BLE 扫描不工作怎么办？

**A**: 检查以下几点：

1. 确认已安装 bleak 库
2. 检查蓝牙适配器是否启用
3. 在 Linux 上检查蓝牙服务：
   ```bash
   sudo systemctl status bluetooth
   ```

#### Q7: I2C 扫描不可用怎么办？

**A**: I2C 扫描仅支持 Linux：

1. 确认已安装 smbus2 库
2. 检查 I2C 设备是否存在：
   ```bash
   ls /dev/i2c-*
   ```
3. 检查用户权限：
   ```bash
   sudo usermod -a -G i2c $USER
   ```

### 性能相关

#### Q8: 应用程序运行缓慢怎么办？

**A**: 尝试以下方法：

1. 清空日志查看器
2. 关闭不使用的模块
3. 减少日志级别（设置为 WARNING 或 ERROR）
4. 重启应用程序

#### Q9: 内存占用过高怎么办？

**A**: 应用程序会自动监控和优化内存使用。如果仍然过高：

1. 定期清空日志
2. 关闭不使用的模块
3. 重启应用程序

#### Q10: 如何查看性能统计？

**A**: 性能统计会自动记录在日志中。查看日志查看器中的 "Performance" 模块日志。

### 配置相关

#### Q11: 配置文件保存在哪里？

**A**: 配置文件位置因操作系统而异：

- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\config.json`
- **macOS**: `~/Library/Application Support/linktunnel/unified-gui/config.json`
- **Linux**: `~/.config/linktunnel/unified-gui/config.json`

#### Q12: 如何重置配置？

**A**: 删除配置文件，应用程序会自动创建默认配置：

```bash
# Linux/macOS
rm ~/.config/linktunnel/unified-gui/config.json

# Windows (PowerShell)
Remove-Item "$env:LOCALAPPDATA\linktunnel\unified-gui\config.json"
```

#### Q13: 如何备份配置？

**A**: 复制配置文件到安全位置：

```bash
# Linux/macOS
cp ~/.config/linktunnel/unified-gui/config.json ~/backup/

# Windows (PowerShell)
Copy-Item "$env:LOCALAPPDATA\linktunnel\unified-gui\config.json" "$HOME\backup\"
```

### 主题相关

#### Q14: 如何切换主题？

**A**: 有两种方式：

1. 菜单栏：视图 → 主题 → 选择主题
2. 快捷键：Ctrl+T 快速切换

#### Q15: 主题设置不生效怎么办？

**A**: 尝试以下方法：

1. 重启应用程序
2. 检查配置文件中的主题设置
3. 重置配置文件

---

## 故障排除

### 应用程序无法启动

**症状**: 双击图标或运行命令后无反应

**解决方法**:

1. 检查 Python 版本：
   ```bash
   python --version
   ```
   确保是 3.8 或更高版本

2. 检查依赖是否安装：
   ```bash
   pip list | grep PyQt6
   ```

3. 查看错误信息：
   ```bash
   python -m linktunnel.unified_gui
   ```

4. 检查日志文件：
   - Windows: `%LOCALAPPDATA%\linktunnel\unified-gui\logs\`
   - macOS: `~/Library/Logs/linktunnel/unified-gui/`
   - Linux: `~/.local/share/linktunnel/unified-gui/logs/`

### 模块功能异常

**症状**: 某个模块无法正常工作

**解决方法**:

1. 查看日志查看器中的错误信息
2. 检查模块依赖是否安装
3. 重启模块（停止后重新启动）
4. 重启应用程序

### 界面显示异常

**症状**: 界面布局混乱或显示不正常

**解决方法**:

1. 调整窗口大小
2. 切换主题
3. 重置窗口状态（删除配置文件）
4. 更新 PyQt6：
   ```bash
   pip install --upgrade PyQt6
   ```

### 数据丢失

**症状**: 配置或数据丢失

**解决方法**:

1. 检查配置文件是否存在
2. 从备份恢复配置
3. 检查磁盘空间
4. 检查文件权限

---

## 技术支持

### 获取帮助

如果遇到问题，可以通过以下方式获取帮助：

1. **查看文档**
   - 用户手册（本文档）
   - 在线文档：https://linktunnel.readthedocs.io
   - GitHub Wiki

2. **社区支持**
   - GitHub Issues: https://github.com/yourusername/linktunnel/issues
   - 讨论区: https://github.com/yourusername/linktunnel/discussions

3. **报告问题**
   - 在 GitHub 上创建 Issue
   - 提供详细的错误信息和日志
   - 说明操作系统和 Python 版本

### 反馈建议

欢迎提供反馈和建议：

- 功能请求：在 GitHub 上创建 Feature Request
- 改进建议：在讨论区发帖
- 贡献代码：提交 Pull Request

### 联系方式

- **GitHub**: https://github.com/yourusername/linktunnel
- **Email**: support@linktunnel.example.com
- **文档**: https://linktunnel.readthedocs.io

---

## 附录

### A. 快捷键列表

| 快捷键 | 功能 |
|--------|------|
| Ctrl+T | 切换主题 |
| F1 | 打开用户手册 |
| Ctrl+L | 清空日志（在终端中） |
| Ctrl+S | 保存数据（在终端中） |
| Enter | 发送数据（在终端中） |

### B. 配置文件格式

配置文件使用 JSON 格式：

```json
{
  "log_level": "INFO",
  "theme": "light",
  "window": {
    "width": 1280,
    "height": 800,
    "maximized": false
  },
  "last_active_module": "serial",
  "modules": {
    "serial": {
      "baudrate": 115200,
      "databits": 8,
      "stopbits": 1,
      "parity": "N"
    }
  }
}
```

### C. 日志级别说明

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| DEBUG | 调试信息 | 开发和调试 |
| INFO | 一般信息 | 正常使用 |
| WARNING | 警告信息 | 潜在问题 |
| ERROR | 错误信息 | 错误和异常 |

### D. 支持的文件格式

| 模块 | 文件格式 | 说明 |
|------|----------|------|
| Grbl CNC | .nc, .gcode, .txt | G 代码文件 |
| BLE 扫描 | .csv | 扫描结果导出 |
| I2C 扫描 | .txt | 扫描结果导出 |
| 日志查看器 | .txt | 日志导出 |

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**适用版本**: linktunnel Unified GUI 0.3.0

感谢使用 linktunnel Unified GUI！
