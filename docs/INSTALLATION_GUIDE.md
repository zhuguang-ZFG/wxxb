# linktunnel Unified GUI - 安装指南

**版本**: 0.3.0  
**更新日期**: 2026-04-13

---

## 📋 目录

1. [系统要求](#系统要求)
2. [安装方式](#安装方式)
3. [依赖管理](#依赖管理)
4. [平台特定说明](#平台特定说明)
5. [验证安装](#验证安装)
6. [故障排除](#故障排除)

---

## 系统要求

### 操作系统

| 操作系统 | 最低版本 | 推荐版本 |
|----------|----------|----------|
| Windows | Windows 10 | Windows 11 |
| macOS | 10.14 (Mojave) | 12.0 (Monterey) 或更高 |
| Linux | Ubuntu 20.04 | Ubuntu 22.04 或更高 |

### Python 版本

- **最低版本**: Python 3.8
- **推荐版本**: Python 3.10 或 3.11
- **不支持**: Python 2.x, Python 3.7 及更早版本

### 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 双核 1.5GHz | 四核 2.0GHz 或更高 |
| 内存 | 2GB RAM | 4GB RAM 或更多 |
| 磁盘 | 100MB 可用空间 | 500MB 可用空间 |
| 显示器 | 1024x768 | 1920x1080 或更高 |

---

## 安装方式

### 方式 1: 使用 pip 安装（推荐）

这是最简单和推荐的安装方式。

#### 1.1 基础安装

安装核心功能（不包含 GUI）：

```bash
pip install linktunnel
```

#### 1.2 安装 GUI 版本

安装包含 GUI 的版本：

```bash
pip install 'linktunnel[gui]'
```

这将安装以下依赖：
- PyQt6 (GUI 框架)
- pyserial (串口通信)

#### 1.3 完整安装

安装所有可选功能：

```bash
pip install 'linktunnel[gui-full]'
```

这将额外安装：
- bleak (BLE 蓝牙扫描)
- smbus2 (I2C 扫描，Linux)
- psutil (性能监控)

### 方式 2: 从源码安装

适合开发者或需要最新功能的用户。

#### 2.1 克隆仓库

```bash
git clone https://github.com/yourusername/linktunnel.git
cd linktunnel
```

#### 2.2 安装依赖

**开发模式安装**（推荐）：

```bash
pip install -e '.[gui]'
```

**完整安装**：

```bash
pip install -e '.[gui-full,dev]'
```

### 方式 3: 使用虚拟环境（推荐）

使用虚拟环境可以避免依赖冲突。

#### 3.1 创建虚拟环境

**Linux/macOS**:

```bash
python3 -m venv linktunnel-env
source linktunnel-env/bin/activate
```

**Windows**:

```bash
python -m venv linktunnel-env
linktunnel-env\Scripts\activate
```

#### 3.2 安装软件

```bash
pip install 'linktunnel[gui]'
```

#### 3.3 退出虚拟环境

```bash
deactivate
```

---

## 依赖管理

### 必需依赖

这些依赖在安装 GUI 版本时会自动安装：

| 包名 | 版本要求 | 用途 |
|------|----------|------|
| PyQt6 | >= 6.4.0 | GUI 框架 |
| pyserial | >= 3.5 | 串口通信 |

### 可选依赖

根据需要手动安装：

#### BLE 蓝牙扫描

```bash
pip install bleak
```

**支持平台**: Windows, macOS, Linux

#### I2C 扫描

```bash
pip install smbus2
```

**支持平台**: 仅 Linux

#### 性能监控

```bash
pip install psutil
```

**支持平台**: Windows, macOS, Linux

### 开发依赖

如果需要参与开发：

```bash
pip install 'linktunnel[dev]'
```

这将安装：
- pytest (测试框架)
- ruff (代码检查)
- black (代码格式化)

### 查看已安装依赖

```bash
pip list | grep -E "PyQt6|pyserial|bleak|smbus2|psutil"
```

### 更新依赖

```bash
pip install --upgrade 'linktunnel[gui]'
```

---

## 平台特定说明

### Windows

#### 安装 Python

1. 从 [python.org](https://www.python.org/downloads/) 下载 Python 安装程序
2. 运行安装程序，**勾选 "Add Python to PATH"**
3. 选择 "Install Now"

#### 安装 linktunnel

打开命令提示符或 PowerShell：

```bash
pip install 'linktunnel[gui]'
```

#### 串口驱动

某些串口设备需要安装驱动：

- **CH340/CH341**: [下载驱动](http://www.wch.cn/downloads/CH341SER_EXE.html)
- **CP210x**: [下载驱动](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
- **FTDI**: [下载驱动](https://ftdichip.com/drivers/vcp-drivers/)

#### 防火墙设置

如果使用网络功能，可能需要允许应用通过防火墙。

### macOS

#### 安装 Python

macOS 自带 Python 2.x，需要安装 Python 3：

**使用 Homebrew**（推荐）:

```bash
brew install python@3.11
```

**或从官网下载**:

从 [python.org](https://www.python.org/downloads/macos/) 下载安装程序。

#### 安装 linktunnel

```bash
pip3 install 'linktunnel[gui]'
```

#### 串口权限

macOS 通常不需要额外配置串口权限。

#### 蓝牙权限

首次使用 BLE 扫描时，系统会请求蓝牙权限，点击"允许"。

### Linux

#### 安装 Python

大多数 Linux 发行版已预装 Python 3。如果没有：

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora**:

```bash
sudo dnf install python3 python3-pip
```

**Arch Linux**:

```bash
sudo pacman -S python python-pip
```

#### 安装 linktunnel

```bash
pip3 install --user 'linktunnel[gui]'
```

或使用虚拟环境（推荐）。

#### 串口权限

将用户添加到 `dialout` 组：

```bash
sudo usermod -a -G dialout $USER
```

**重新登录**以使更改生效。

#### I2C 权限

将用户添加到 `i2c` 组：

```bash
sudo usermod -a -G i2c $USER
```

确保 I2C 设备存在：

```bash
ls /dev/i2c-*
```

如果没有，加载 I2C 模块：

```bash
sudo modprobe i2c-dev
```

#### 蓝牙依赖

确保蓝牙服务运行：

```bash
sudo systemctl status bluetooth
sudo systemctl start bluetooth
```

安装 BlueZ：

```bash
sudo apt install bluez  # Ubuntu/Debian
sudo dnf install bluez  # Fedora
```

#### Qt 依赖

某些发行版可能需要额外的 Qt 库：

**Ubuntu/Debian**:

```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

---

## 验证安装

### 检查版本

```bash
python -m linktunnel.unified_gui --version
```

或

```bash
linktunnel-unified --version
```

预期输出：

```
linktunnel Unified GUI 0.3.0
```

### 测试导入

```bash
python -c "from linktunnel.unified_gui import __version__; print(__version__)"
```

### 启动应用

```bash
linktunnel-unified
```

或

```bash
python -m linktunnel.unified_gui
```

应用程序应该正常启动并显示主窗口。

### 检查依赖

```bash
python -c "import PyQt6; print('PyQt6:', PyQt6.QtCore.PYQT_VERSION_STR)"
python -c "import serial; print('pyserial:', serial.VERSION)"
```

### 检查可选依赖

```bash
# BLE
python -c "import bleak; print('bleak:', bleak.__version__)" 2>/dev/null || echo "bleak not installed"

# I2C (Linux only)
python -c "import smbus2; print('smbus2 installed')" 2>/dev/null || echo "smbus2 not installed"

# 性能监控
python -c "import psutil; print('psutil:', psutil.__version__)" 2>/dev/null || echo "psutil not installed"
```

---

## 故障排除

### 问题 1: pip 命令不存在

**症状**:

```
bash: pip: command not found
```

**解决方法**:

使用 `pip3` 或 `python -m pip`：

```bash
python3 -m pip install 'linktunnel[gui]'
```

或安装 pip：

```bash
# Ubuntu/Debian
sudo apt install python3-pip

# macOS
python3 -m ensurepip --upgrade
```

### 问题 2: 权限错误

**症状**:

```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**解决方法**:

使用 `--user` 参数：

```bash
pip install --user 'linktunnel[gui]'
```

或使用虚拟环境（推荐）。

### 问题 3: PyQt6 安装失败

**症状**:

```
ERROR: Failed building wheel for PyQt6
```

**解决方法**:

**Linux**: 安装构建依赖

```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora
sudo dnf install gcc gcc-c++ python3-devel
```

**macOS**: 安装 Xcode Command Line Tools

```bash
xcode-select --install
```

**Windows**: 安装 Visual C++ Build Tools

从 [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 下载安装。

### 问题 4: 找不到命令

**症状**:

```
bash: linktunnel-unified: command not found
```

**解决方法**:

1. 确认安装成功：
   ```bash
   pip show linktunnel
   ```

2. 检查 PATH：
   ```bash
   echo $PATH
   ```

3. 使用完整路径：
   ```bash
   python -m linktunnel.unified_gui
   ```

4. 或添加到 PATH：
   ```bash
   # Linux/macOS
   export PATH="$HOME/.local/bin:$PATH"
   
   # Windows (PowerShell)
   $env:Path += ";$env:LOCALAPPDATA\Programs\Python\Python311\Scripts"
   ```

### 问题 5: 依赖冲突

**症状**:

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**解决方法**:

使用虚拟环境隔离依赖：

```bash
python3 -m venv fresh-env
source fresh-env/bin/activate  # Linux/macOS
# 或
fresh-env\Scripts\activate  # Windows

pip install 'linktunnel[gui]'
```

### 问题 6: 串口权限错误（Linux）

**症状**:

```
PermissionError: [Errno 13] Permission denied: '/dev/ttyUSB0'
```

**解决方法**:

```bash
sudo usermod -a -G dialout $USER
```

重新登录或重启。

### 问题 7: 蓝牙不工作（Linux）

**症状**:

BLE 扫描失败或找不到设备。

**解决方法**:

1. 检查蓝牙服务：
   ```bash
   sudo systemctl status bluetooth
   sudo systemctl start bluetooth
   ```

2. 检查蓝牙适配器：
   ```bash
   hciconfig
   ```

3. 安装 BlueZ：
   ```bash
   sudo apt install bluez
   ```

### 问题 8: I2C 设备不存在（Linux）

**症状**:

```
FileNotFoundError: [Errno 2] No such file or directory: '/dev/i2c-1'
```

**解决方法**:

1. 加载 I2C 模块：
   ```bash
   sudo modprobe i2c-dev
   ```

2. 永久启用：
   ```bash
   echo "i2c-dev" | sudo tee -a /etc/modules
   ```

3. 检查设备：
   ```bash
   ls /dev/i2c-*
   ```

---

## 卸载

### 卸载 linktunnel

```bash
pip uninstall linktunnel
```

### 删除配置文件

**Linux/macOS**:

```bash
rm -rf ~/.config/linktunnel
rm -rf ~/.local/share/linktunnel
```

**macOS** (额外):

```bash
rm -rf ~/Library/Application\ Support/linktunnel
rm -rf ~/Library/Logs/linktunnel
```

**Windows** (PowerShell):

```powershell
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\linktunnel"
```

---

## 升级

### 升级到最新版本

```bash
pip install --upgrade 'linktunnel[gui]'
```

### 升级所有依赖

```bash
pip install --upgrade --upgrade-strategy eager 'linktunnel[gui]'
```

### 查看更新日志

访问 [GitHub Releases](https://github.com/yourusername/linktunnel/releases) 查看更新内容。

---

## 获取帮助

如果遇到安装问题：

1. **查看文档**: [在线文档](https://linktunnel.readthedocs.io)
2. **搜索 Issues**: [GitHub Issues](https://github.com/yourusername/linktunnel/issues)
3. **提问**: [讨论区](https://github.com/yourusername/linktunnel/discussions)
4. **报告问题**: 创建新的 Issue

提供以下信息有助于快速解决问题：

- 操作系统和版本
- Python 版本
- 完整的错误信息
- 安装命令

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**适用版本**: linktunnel Unified GUI 0.3.0
