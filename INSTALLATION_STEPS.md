# linktunnel Unified GUI - 安装和测试步骤

**日期**: 2026-04-13  
**版本**: 0.3.0

---

## 🚀 快速开始

### 步骤 1: 安装 Python

#### 方式 1: 使用 Chocolatey（推荐）

```powershell
# 以管理员身份运行 PowerShell
choco install python311 -y

# 等待安装完成后，重新打开 PowerShell
python --version
```

#### 方式 2: 从官网下载

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.11.x 安装程序
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH"
5. 点击 "Install Now"

#### 方式 3: 使用 Microsoft Store

1. 打开 Microsoft Store
2. 搜索 "Python 3.11"
3. 点击安装

### 步骤 2: 验证 Python 安装

```powershell
# 检查 Python 版本
python --version
# 应该显示: Python 3.11.x

# 检查 pip
pip --version
# 应该显示: pip 23.x.x
```

### 步骤 3: 安装项目依赖

```powershell
# 进入项目目录
cd C:\Users\Administrator\Documents\GitHub\wxxb

# 安装依赖
pip install PyQt6 pyserial

# 或安装完整依赖
pip install PyQt6 pyserial bleak psutil
```

### 步骤 4: 测试启动

```powershell
# 方式 1: 使用测试脚本
python test_startup.py

# 方式 2: 直接启动
python -m linktunnel.unified_gui

# 方式 3: 使用启动脚本
python -c "import sys; sys.path.insert(0, 'src'); from linktunnel.unified_gui.__main__ import main; main()"
```

---

## 📋 详细安装步骤

### Windows 安装

#### 1. 检查现有 Python

```powershell
# 查找所有 Python 安装
Get-Command python* | Select-Object Name, Source

# 检查版本
python --version
python3 --version
```

#### 2. 安装 Python 3.11

如果没有 Python 或版本过低：

```powershell
# 使用 Chocolatey
choco install python311 -y

# 安装完成后，关闭并重新打开 PowerShell
```

#### 3. 配置环境变量

如果 Python 不在 PATH 中：

1. 右键"此电脑" → "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"系统变量"中找到"Path"
5. 添加以下路径：
   - `C:\Python311`
   - `C:\Python311\Scripts`

#### 4. 验证安装

```powershell
# 重新打开 PowerShell
python --version
pip --version
```

### 安装项目依赖

#### 最小依赖（仅 GUI）

```powershell
pip install PyQt6 pyserial
```

#### 推荐依赖（包含性能监控）

```powershell
pip install PyQt6 pyserial psutil
```

#### 完整依赖（所有功能）

```powershell
pip install PyQt6 pyserial bleak psutil
```

**注意**: 
- `bleak` 用于 BLE 蓝牙扫描
- `psutil` 用于性能监控
- `smbus2` 仅 Linux 需要（I2C 扫描）

---

## 🧪 测试应用

### 测试 1: 导入测试

```powershell
python -c "import sys; sys.path.insert(0, 'src'); from linktunnel.unified_gui.core.config_manager import ConfigManager; print('✓ 导入成功')"
```

### 测试 2: PyQt6 测试

```powershell
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 可用')"
```

### 测试 3: 完整启动测试

```powershell
python test_startup.py
```

这个脚本会：
1. 检查 Python 版本
2. 验证 PyQt6 安装
3. 测试所有核心模块
4. 创建主窗口
5. 启动应用程序

### 测试 4: 直接启动

```powershell
# 添加 src 到 Python 路径并启动
$env:PYTHONPATH="src"; python -m linktunnel.unified_gui
```

---

## 🐛 故障排除

### 问题 1: python 命令不存在

**症状**: `python: 命令未找到`

**解决方法**:
1. 确认 Python 已安装
2. 检查环境变量 PATH
3. 重新打开 PowerShell
4. 尝试使用完整路径: `C:\Python311\python.exe`

### 问题 2: PyQt6 安装失败

**症状**: `ERROR: Could not build wheels for PyQt6`

**解决方法**:
```powershell
# 升级 pip
python -m pip install --upgrade pip

# 重新安装
pip install PyQt6
```

### 问题 3: 导入错误

**症状**: `ModuleNotFoundError: No module named 'linktunnel'`

**解决方法**:
```powershell
# 确保在项目根目录
cd C:\Users\Administrator\Documents\GitHub\wxxb

# 设置 PYTHONPATH
$env:PYTHONPATH="src"

# 或使用完整路径
python -c "import sys; sys.path.insert(0, 'src'); from linktunnel.unified_gui.__main__ import main; main()"
```

### 问题 4: 权限错误

**症状**: `PermissionError: [Errno 13]`

**解决方法**:
```powershell
# 使用 --user 参数
pip install --user PyQt6 pyserial

# 或以管理员身份运行 PowerShell
```

### 问题 5: Chocolatey 安装超时

**症状**: 安装过程中超时

**解决方法**:
1. 等待后台安装完成（可能需要 5-10 分钟）
2. 检查安装状态: `choco list --local-only | findstr python`
3. 如果失败，使用官网安装程序

---

## 📊 验证清单

安装完成后，验证以下项目：

- [ ] Python 版本 >= 3.8
  ```powershell
  python --version
  ```

- [ ] pip 可用
  ```powershell
  pip --version
  ```

- [ ] PyQt6 已安装
  ```powershell
  pip show PyQt6
  ```

- [ ] pyserial 已安装
  ```powershell
  pip show pyserial
  ```

- [ ] 可以导入核心模块
  ```powershell
  python -c "import sys; sys.path.insert(0, 'src'); from linktunnel.unified_gui.core.config_manager import ConfigManager"
  ```

- [ ] 应用可以启动
  ```powershell
  python test_startup.py
  ```

---

## 🎯 下一步

安装成功后：

1. **运行测试脚本**
   ```powershell
   python test_startup.py
   ```

2. **查看测试指南**
   - 阅读 `MANUAL_TESTING.md`
   - 按照清单逐项测试

3. **运行自动化测试**
   ```powershell
   pip install pytest
   pytest tests/test_cross_platform.py -v
   ```

4. **开始使用**
   - 探索各个功能模块
   - 尝试不同的主题
   - 查看帮助文档

---

## 📞 获取帮助

如果遇到问题：

1. 查看 `TESTING_STATUS.md` - 测试状态
2. 查看 `MANUAL_TESTING.md` - 测试清单
3. 查看 `docs/FAQ.md` - 常见问题
4. 查看 `docs/INSTALLATION_GUIDE.md` - 详细安装指南

---

## 🎉 成功标志

当您看到以下内容时，表示安装成功：

```
============================================================
linktunnel Unified GUI 启动测试
============================================================

Python 版本: 3.11.x
Python 路径: C:\Python311\python.exe
当前目录: C:\Users\Administrator\Documents\GitHub\wxxb

测试导入...
1. 测试 PyQt6...
   ✓ PyQt6 已安装
   - Qt 版本: 6.x.x
   - PyQt 版本: 6.x.x

2. 测试核心模块...
   ✓ ConfigManager
   ✓ LogManager
   ✓ MainWindow

3. 测试配置管理器...
   ✓ 配置管理器创建成功

4. 测试日志管理器...
   ✓ 日志管理器创建成功

5. 测试主窗口创建...
   ✓ 主窗口创建成功

============================================================
✓ 所有测试通过！
============================================================

启动应用程序...
✓ 窗口已显示
```

然后您应该看到 linktunnel Unified GUI 主窗口！

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13
