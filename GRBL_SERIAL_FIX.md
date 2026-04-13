# Grbl 模块 - 串口列表修复

**日期**: 2026-04-13  
**版本**: 0.3.0  
**状态**: ✅ 完成

---

## 🔧 问题和解决方案

### 问题

Grbl 模块中的串口列表没有显示任何设备。

### 原因

在 `grbl_module.py` 的 `_refresh_ports()` 方法中，调用了错误的函数名：

```python
# ✗ 错误的代码
from linktunnel.serial_util import list_ports
ports = list_ports()  # 这个函数不存在！
```

实际的函数名是 `list_serial_ports()`，而不是 `list_ports()`。

### 解决方案

修改 `_refresh_ports()` 方法，使用正确的函数名：

```python
# ✓ 正确的代码
from linktunnel.serial_util import list_serial_ports
ports = list_serial_ports()  # 正确的函数名
```

---

## 📝 修改详情

### 文件: src/linktunnel/unified_gui/modules/grbl_module.py

**修改前**:
```python
def _refresh_ports(self) -> None:
    """刷新串口列表"""
    try:
        from linktunnel.serial_util import list_ports  # ✗ 错误

        ports = list_ports()  # ✗ 错误
        self._port_combo.clear()
        for p in ports:
            self._port_combo.addItem(f"{p.device} - {p.description}")
        self.log_info(f"发现 {len(ports)} 个串口")
    except Exception as e:
        self.log_error(f"刷新串口失败: {e}")
```

**修改后**:
```python
def _refresh_ports(self) -> None:
    """刷新串口列表"""
    try:
        from linktunnel.serial_util import list_serial_ports  # ✓ 正确

        ports = list_serial_ports()  # ✓ 正确
        self._port_combo.clear()
        for p in ports:
            self._port_combo.addItem(f"{p.device} - {p.description}")
        self.log_info(f"发现 {len(ports)} 个串口")
    except Exception as e:
        self.log_error(f"刷新串口失败: {e}")
```

---

## ✅ 验证

### 测试结果

运行 `test_grbl_ports.py` 后的输出：

```
发现 2 个串口:
  1. COM1
     描述: 通信端口 (COM1)
     硬件ID: ACPI\PNP0501\0

  2. COM3
     描述: USB-SERIAL CH340 (COM3)
     硬件ID: USB VID:PID=1A86:7523 SER= LOCATION=1

✓ 串口列表正常

✓ 串口下拉框中有 2 个项目:
  1. COM1 - 通信端口 (COM1)
  2. COM3 - USB-SERIAL CH340 (COM3)
```

### 验证清单

- [x] 串口列表正确显示
- [x] 串口描述正确显示
- [x] 下拉框中有正确的项目数
- [x] 可以选择不同的串口
- [x] 刷新按钮正常工作

---

## 🚀 使用方法

### 启动 Grbl 模块

1. 启动应用程序
2. 点击左侧导航中的 "Grbl CNC"
3. 在 "设备连接" 标签页中查看串口列表
4. 选择要连接的串口
5. 点击 "连接" 按钮

### 测试串口列表

```bash
py -3 test_grbl_ports.py
```

---

## 📊 对比表

### 修复前 vs 修复后

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 串口列表 | 空 | 显示所有可用串口 |
| 错误信息 | ImportError | 无 |
| 功能 | 无法使用 | 正常工作 |

---

## 🔍 相关函数

### serial_util.py 中的函数

```python
def list_serial_ports() -> list[PortInfo]:
    """列出所有可用的串口
    
    Returns:
        PortInfo 对象列表，包含:
        - device: 串口设备名 (如 COM1, /dev/ttyUSB0)
        - description: 设备描述
        - hwid: 硬件 ID
    """
```

### PortInfo 类

```python
class PortInfo:
    device: str          # 设备名
    description: str     # 描述
    hwid: str           # 硬件 ID
```

---

## 📝 其他模块检查

已检查其他模块是否有相同问题：

- ✓ **SerialModule**: 使用正确的 `list_serial_ports()`
- ✓ **NetworkModule**: 不需要列出串口
- ✓ **ProxyModule**: 不需要列出串口
- ✓ **BLEModule**: 不需要列出串口
- ✓ **I2CModule**: 不需要列出串口
- ✓ **GrblModule**: 已修复

---

## 🎯 总结

修复后的 Grbl 模块现在可以：

1. ✅ 正确列出所有可用的串口
2. ✅ 显示串口的描述信息
3. ✅ 允许用户选择要连接的串口
4. ✅ 支持刷新串口列表
5. ✅ 支持 USB 和虚拟串口

---

## 📞 故障排除

### 问题: 仍然看不到串口

**解决方案**:
1. 检查 USB 设备是否已连接
2. 检查驱动程序是否已安装
3. 在设备管理器中查看是否显示串口
4. 尝试重新启动应用程序

### 问题: 显示错误信息

**解决方案**:
1. 检查是否有其他应用程序占用了串口
2. 关闭其他串口应用程序
3. 尝试重新连接 USB 设备

---

**最后更新**: 2026-04-13  
**状态**: ✅ 完成并测试通过
