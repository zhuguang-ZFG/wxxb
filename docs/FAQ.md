# linktunnel Unified GUI - 常见问题 (FAQ)

**版本**: 0.3.0  
**更新日期**: 2026-04-13

---

## 📋 目录

1. [一般问题](#一般问题)
2. [安装问题](#安装问题)
3. [串口问题](#串口问题)
4. [网络问题](#网络问题)
5. [代理问题](#代理问题)
6. [Grbl CNC 问题](#grbl-cnc-问题)
7. [BLE 问题](#ble-问题)
8. [I2C 问题](#i2c-问题)
9. [性能问题](#性能问题)
10. [配置问题](#配置问题)

---

## 一般问题

### Q1: linktunnel Unified GUI 是什么？

**A**: linktunnel Unified GUI 是一个统一的图形界面应用程序，整合了 linktunnel 项目的所有功能，包括串口工具、网络中继、代理管理、Grbl CNC 控制、BLE 扫描和 I2C 扫描等。

### Q2: 支持哪些操作系统？

**A**: 支持以下操作系统：

- Windows 10 及更高版本
- macOS 10.14 (Mojave) 及更高版本
- Linux (Ubuntu 20.04+, Fedora, Arch 等)

### Q3: 需要什么 Python 版本？

**A**: 需要 Python 3.8 或更高版本。推荐使用 Python 3.10 或 3.11。

### Q4: 是否免费？

**A**: 是的，linktunnel 是开源项目，完全免费使用。

### Q5: 如何获取最新版本？

**A**: 使用以下命令更新：

```bash
pip install --upgrade 'linktunnel[gui]'
```

或访问 [GitHub Releases](https://github.com/yourusername/linktunnel/releases)。

### Q6: 如何报告 Bug？

**A**: 在 [GitHub Issues](https://github.com/yourusername/linktunnel/issues) 创建新的 Issue，提供详细的错误信息和复现步骤。

### Q7: 如何贡献代码？

**A**: 欢迎贡献！请查看 [CONTRIBUTING.md](https://github.com/yourusername/linktunnel/blob/main/CONTRIBUTING.md) 了解详情。

---

## 安装问题

### Q8: 如何安装 linktunnel Unified GUI？

**A**: 使用 pip 安装：

```bash
pip install 'linktunnel[gui]'
```

详细说明请参考 [安装指南](INSTALLATION_GUIDE.md)。

### Q9: 安装时出现权限错误怎么办？

**A**: 使用 `--user` 参数安装到用户目录：

```bash
pip install --user 'linktunnel[gui]'
```

或使用虚拟环境（推荐）：

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
pip install 'linktunnel[gui]'
```

### Q10: PyQt6 安装失败怎么办？

**A**: 

**Linux**: 安装构建依赖

```bash
sudo apt install build-essential python3-dev  # Ubuntu/Debian
sudo dnf install gcc gcc-c++ python3-devel  # Fedora
```

**macOS**: 安装 Xcode Command Line Tools

```bash
xcode-select --install
```

**Windows**: 安装 Visual C++ Build Tools

从 [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 下载安装。

### Q11: 如何卸载？

**A**: 

```bash
pip uninstall linktunnel
```

删除配置文件：

```bash
# Linux/macOS
rm -rf ~/.config/linktunnel

# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\linktunnel"
```

### Q12: 如何在虚拟环境中安装？

**A**: 

```bash
# 创建虚拟环境
python -m venv linktunnel-env

# 激活虚拟环境
source linktunnel-env/bin/activate  # Linux/macOS
linktunnel-env\Scripts\activate  # Windows

# 安装
pip install 'linktunnel[gui]'
```

---

## 串口问题

### Q13: 找不到串口设备怎么办？

**A**: 

1. **确认设备已连接**
2. **点击"刷新"按钮**更新列表
3. **检查驱动**：某些设备需要安装驱动（CH340, CP210x, FTDI 等）
4. **检查权限**（Linux）：
   ```bash
   sudo usermod -a -G dialout $USER
   ```
   然后重新登录

### Q14: 串口打开失败怎么办？

**A**: 

1. **确认串口未被占用**：关闭其他使用该串口的程序
2. **检查权限**：确保有访问串口的权限
3. **检查参数**：确认波特率等参数正确
4. **重新插拔设备**

### Q15: 串口数据乱码怎么办？

**A**: 

1. **检查波特率**：确保与设备一致
2. **检查编码**：尝试不同的编码（UTF-8, ASCII, GBK）
3. **检查数据位、停止位、校验位**
4. **使用十六进制模式**查看原始数据

### Q16: 如何同时使用多个串口？

**A**: 

- **串口桥接**：连接两个串口
- **多个终端**：目前不支持，需要启动多个应用实例

### Q17: 串口桥接时数据丢失怎么办？

**A**: 

1. **降低波特率**
2. **检查硬件连接**
3. **查看日志**了解详细错误
4. **使用流控制**（如果设备支持）

---

## 网络问题

### Q18: TCP 中继连接失败怎么办？

**A**: 

1. **检查目标地址和端口**是否正确
2. **检查防火墙设置**
3. **检查目标服务是否运行**
4. **尝试使用 telnet 测试**：
   ```bash
   telnet <目标地址> <端口>
   ```

### Q19: 监听端口被占用怎么办？

**A**: 

1. **更换端口**
2. **查找占用进程**：
   ```bash
   # Linux/macOS
   lsof -i :<端口>
   
   # Windows
   netstat -ano | findstr :<端口>
   ```
3. **停止占用进程**

### Q20: UDP 中继不工作怎么办？

**A**: 

1. **确认使用 UDP 协议**
2. **检查防火墙**是否允许 UDP
3. **注意 UDP 是无连接协议**，不保证数据送达
4. **查看日志**了解详细信息

### Q21: 如何查看网络流量统计？

**A**: 在中继界面可以看到：

- 上行流量
- 下行流量
- 连接数
- 数据流日志

### Q22: 支持 IPv6 吗？

**A**: 是的，TCP 中继支持 IPv6。在配置中启用"IPv6 支持"选项。

---

## 代理问题

### Q23: 无法连接到代理怎么办？

**A**: 

1. **确认 Mihomo/Clash 正在运行**
2. **检查 API 地址**（默认 http://127.0.0.1:9090）
3. **检查 Secret**（如果设置了）
4. **查看代理日志**
5. **尝试在浏览器访问** API 地址

### Q24: 如何获取 API Secret？

**A**: 

1. **查看配置文件**：
   - Mihomo: `config.yaml` 中的 `secret` 字段
   - Clash: `config.yaml` 中的 `secret` 字段

2. **启用"从 profile 读取"**自动读取

### Q25: 节点延迟测试失败怎么办？

**A**: 

1. **确认代理正在运行**
2. **检查网络连接**
3. **某些节点可能不可用**
4. **等待测试完成**（可能需要较长时间）

### Q26: 如何切换节点？

**A**: 

1. **双击节点**
2. **或选择节点后点击"应用"**
3. **查看日志确认切换成功**

### Q27: 打开控制台失败怎么办？

**A**: 

1. **确认代理正在运行**
2. **检查浏览器是否安装**
3. **手动访问**：http://127.0.0.1:9090/ui

### Q28: 支持哪些代理内核？

**A**: 

- Mihomo (Clash Meta)
- Clash Premium
- Clash

---

## Grbl CNC 问题

### Q29: 无法连接到 CNC 设备怎么办？

**A**: 

1. **检查连接方式**（串口或 WiFi）
2. **串口连接**：
   - 确认设备已连接
   - 检查波特率（通常 115200）
   - 检查驱动
3. **WiFi 连接**：
   - 确认 IP 地址和端口
   - 检查网络连接
   - 尝试 ping 设备

### Q30: G 代码传输失败怎么办？

**A**: 

1. **检查文件格式**（.nc, .gcode, .txt）
2. **检查文件内容**是否为有效的 G 代码
3. **查看传输日志**了解错误
4. **尝试暂停后恢复**
5. **重新连接设备**

### Q31: 机器状态显示 Alarm 怎么办？

**A**: 

1. **查看错误代码**
2. **发送解锁命令**：$X
3. **执行回零**：$H
4. **检查限位开关**
5. **查看 Grbl 文档**了解错误代码含义

### Q32: 如何暂停和恢复传输？

**A**: 

- **暂停**：点击"暂停"按钮或发送 ! 命令
- **恢复**：点击"恢复"按钮或发送 ~ 命令
- **停止**：点击"停止"按钮或发送 Ctrl+X

### Q33: 支持哪些 Grbl 版本？

**A**: 

- Grbl 1.1
- Grbl 0.9
- 其他兼容版本

### Q34: 如何查看 Grbl 设置？

**A**: 

在手动控制中发送 `$$` 命令。

---

## BLE 问题

### Q35: BLE 扫描不工作怎么办？

**A**: 

1. **确认已安装 bleak**：
   ```bash
   pip install bleak
   ```

2. **检查蓝牙适配器**是否启用

3. **Linux**：
   ```bash
   sudo systemctl status bluetooth
   sudo systemctl start bluetooth
   ```

4. **macOS**：授予蓝牙权限

5. **Windows**：确认蓝牙已启用

### Q36: 找不到蓝牙设备怎么办？

**A**: 

1. **确认设备已开启**且处于可发现模式
2. **增加扫描超时**（默认 10 秒）
3. **靠近设备**
4. **重启蓝牙适配器**
5. **尝试其他蓝牙工具**验证设备可见性

### Q37: RSSI 值是什么？

**A**: 

RSSI (Received Signal Strength Indicator) 是信号强度指示器，单位 dBm：

- **-30 dBm**: 极强信号
- **-50 dBm**: 强信号
- **-70 dBm**: 中等信号
- **-90 dBm**: 弱信号
- **-100 dBm**: 极弱信号

### Q38: 如何导出扫描结果？

**A**: 

点击"导出"按钮，选择保存位置，结果将保存为 CSV 文件。

### Q39: 支持 BLE 连接吗？

**A**: 

目前仅支持扫描，不支持连接。连接功能计划在未来版本中添加。

---

## I2C 问题

### Q40: I2C 扫描不可用怎么办？

**A**: 

I2C 扫描仅支持 Linux：

1. **确认已安装 smbus2**：
   ```bash
   pip install smbus2
   ```

2. **检查 I2C 设备**：
   ```bash
   ls /dev/i2c-*
   ```

3. **加载 I2C 模块**：
   ```bash
   sudo modprobe i2c-dev
   ```

4. **检查权限**：
   ```bash
   sudo usermod -a -G i2c $USER
   ```
   然后重新登录

### Q41: 找不到 I2C 设备怎么办？

**A**: 

1. **确认设备已连接**
2. **检查接线**（SDA, SCL, VCC, GND）
3. **检查上拉电阻**（通常 4.7kΩ）
4. **尝试不同的总线编号**
5. **使用 i2cdetect 工具**验证：
   ```bash
   sudo i2cdetect -y 1
   ```

### Q42: 如何选择 I2C 总线？

**A**: 

在扫描界面选择总线编号：

- **Raspberry Pi**: 通常是 1
- **其他设备**: 可能是 0, 2 等

使用 `ls /dev/i2c-*` 查看可用总线。

### Q43: 扫描结果如何解读？

**A**: 

- **绿色高亮**: 找到设备
- **灰色**: 无设备
- **地址范围**: 0x00-0x7F

常见设备地址：

- 0x27, 0x3F: LCD1602/2004
- 0x48-0x4F: ADS1115, PCF8591
- 0x68: MPU6050, DS1307
- 0x76, 0x77: BMP280, BME280

### Q44: Windows/macOS 支持 I2C 吗？

**A**: 

目前不支持。I2C 扫描功能仅在 Linux 上可用。

---

## 性能问题

### Q45: 应用程序运行缓慢怎么办？

**A**: 

1. **清空日志查看器**
2. **关闭不使用的模块**
3. **减少日志级别**（设置为 WARNING 或 ERROR）
4. **重启应用程序**
5. **检查系统资源**（CPU, 内存）

### Q46: 内存占用过高怎么办？

**A**: 

应用程序会自动监控和优化内存。如果仍然过高：

1. **定期清空日志**
2. **关闭不使用的模块**
3. **重启应用程序**
4. **查看性能日志**了解详情

### Q47: 日志查看器卡顿怎么办？

**A**: 

1. **清空日志**（Ctrl+L 或点击"清空"）
2. **减少日志级别**
3. **使用日志过滤**只显示重要日志
4. **导出日志后清空**

### Q48: 模块切换慢怎么办？

**A**: 

模块切换已优化，响应时间 < 50ms。如果仍然慢：

1. **检查系统资源**
2. **关闭其他程序**
3. **重启应用程序**
4. **更新到最新版本**

### Q49: 如何查看性能统计？

**A**: 

性能统计自动记录在日志中。查看日志查看器中的 "Performance" 模块日志。

### Q50: CPU 使用率过高怎么办？

**A**: 

1. **检查哪个模块占用高**
2. **停止不使用的模块**
3. **减少日志输出**
4. **查看性能日志**
5. **报告问题**如果持续高占用

---

## 配置问题

### Q51: 配置文件在哪里？

**A**: 

配置文件位置因操作系统而异：

- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\config.json`
- **macOS**: `~/Library/Application Support/linktunnel/unified-gui/config.json`
- **Linux**: `~/.config/linktunnel/unified-gui/config.json`

### Q52: 如何重置配置？

**A**: 

删除配置文件，应用程序会自动创建默认配置：

```bash
# Linux/macOS
rm ~/.config/linktunnel/unified-gui/config.json

# Windows (PowerShell)
Remove-Item "$env:LOCALAPPDATA\linktunnel\unified-gui\config.json"
```

### Q53: 如何备份配置？

**A**: 

复制配置文件到安全位置：

```bash
# Linux/macOS
cp ~/.config/linktunnel/unified-gui/config.json ~/backup/

# Windows (PowerShell)
Copy-Item "$env:LOCALAPPDATA\linktunnel\unified-gui\config.json" "$HOME\backup\"
```

### Q54: 如何导入/导出配置？

**A**: 

目前需要手动复制配置文件。未来版本将添加导入/导出功能。

### Q55: 配置文件格式是什么？

**A**: 

JSON 格式。示例：

```json
{
  "log_level": "INFO",
  "theme": "light",
  "window": {
    "width": 1280,
    "height": 800
  }
}
```

### Q56: 如何修改日志级别？

**A**: 

编辑配置文件，修改 `log_level` 字段：

- DEBUG: 调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息

### Q57: 如何切换主题？

**A**: 

1. **菜单栏**: 视图 → 主题 → 选择主题
2. **快捷键**: Ctrl+T 快速切换
3. **配置文件**: 修改 `theme` 字段（light/dark/system）

### Q58: 主题设置不生效怎么办？

**A**: 

1. **重启应用程序**
2. **检查配置文件**
3. **重置配置**
4. **更新到最新版本**

---

## 其他问题

### Q59: 如何查看日志文件？

**A**: 

日志文件位置：

- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\logs\`
- **macOS**: `~/Library/Logs/linktunnel/unified-gui/`
- **Linux**: `~/.local/share/linktunnel/unified-gui/logs/`

### Q60: 支持命令行参数吗？

**A**: 

目前支持的参数：

```bash
linktunnel-unified --version  # 显示版本
linktunnel-unified --help     # 显示帮助
```

更多参数计划在未来版本中添加。

### Q61: 如何获取帮助？

**A**: 

1. **查看文档**: 
   - 用户手册
   - 安装指南
   - 常见问题（本文档）

2. **在线资源**:
   - [在线文档](https://linktunnel.readthedocs.io)
   - [GitHub Wiki](https://github.com/yourusername/linktunnel/wiki)

3. **社区支持**:
   - [GitHub Issues](https://github.com/yourusername/linktunnel/issues)
   - [讨论区](https://github.com/yourusername/linktunnel/discussions)

### Q62: 如何贡献翻译？

**A**: 

目前仅支持中文。欢迎贡献其他语言翻译！请查看 [CONTRIBUTING.md](https://github.com/yourusername/linktunnel/blob/main/CONTRIBUTING.md)。

### Q63: 有移动版本吗？

**A**: 

目前没有。linktunnel Unified GUI 是桌面应用程序。

### Q64: 支持插件吗？

**A**: 

目前不支持。插件系统计划在未来版本中添加。

### Q65: 如何参与开发？

**A**: 

1. **Fork 仓库**
2. **创建分支**
3. **提交更改**
4. **创建 Pull Request**

详见 [CONTRIBUTING.md](https://github.com/yourusername/linktunnel/blob/main/CONTRIBUTING.md)。

---

## 联系我们

如果您的问题未在此列出，请：

- **创建 Issue**: [GitHub Issues](https://github.com/yourusername/linktunnel/issues)
- **参与讨论**: [讨论区](https://github.com/yourusername/linktunnel/discussions)
- **发送邮件**: support@linktunnel.example.com

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**适用版本**: linktunnel Unified GUI 0.3.0

感谢使用 linktunnel Unified GUI！
