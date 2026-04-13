# linktunnel Unified GUI - 测试指南

**版本**: 0.3.0  
**更新日期**: 2026-04-13

---

## 📋 目录

1. [测试概述](#测试概述)
2. [测试环境](#测试环境)
3. [单元测试](#单元测试)
4. [集成测试](#集成测试)
5. [跨平台测试](#跨平台测试)
6. [性能测试](#性能测试)
7. [测试报告](#测试报告)

---

## 测试概述

### 测试目标

- 确保所有功能正常工作
- 验证跨平台兼容性
- 检查性能指标
- 发现和修复 Bug

### 测试类型

| 类型 | 说明 | 工具 |
|------|------|------|
| 单元测试 | 测试单个组件 | pytest |
| 集成测试 | 测试组件集成 | pytest |
| 功能测试 | 测试完整功能 | 手动测试 |
| 性能测试 | 测试性能指标 | pytest + psutil |
| 兼容性测试 | 测试跨平台 | 手动测试 |

---

## 测试环境

### 开发环境

```bash
# 安装测试依赖
pip install -e '.[dev,gui-full]'

# 验证安装
pytest --version
```

### 测试平台

| 平台 | 版本 | Python | 状态 |
|------|------|--------|------|
| Windows 10 | 21H2+ | 3.8+ | ✅ |
| Windows 11 | 22H2+ | 3.8+ | ✅ |
| macOS | 10.14+ | 3.8+ | ✅ |
| Ubuntu | 20.04+ | 3.8+ | ✅ |
| Fedora | 35+ | 3.8+ | ✅ |

---

## 单元测试

### 运行单元测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_config_manager.py

# 运行特定测试
pytest tests/test_config_manager.py::test_get_set

# 显示详细输出
pytest tests/ -v

# 显示覆盖率
pytest tests/ --cov=src/linktunnel/unified_gui
```

### 测试覆盖

| 组件 | 测试文件 | 覆盖率 |
|------|----------|--------|
| ConfigManager | test_config_manager.py | - |
| LogManager | test_logfmt.py | - |
| BaseModule | test_*_module.py | - |
| SerialModule | test_serial_module.py | ✅ |
| NetworkModule | test_tcp_udp.py | ✅ |
| ProxyModule | test_proxy_module.py | ✅ |
| GrblModule | test_grbl_module.py | ✅ |
| BLEModule | test_ble_module.py | ✅ |
| I2CModule | test_i2c_module.py | ✅ |
| ThemeManager | test_theme_manager.py | ✅ |
| FeedbackManager | test_feedback_manager.py | ✅ |
| HelpManager | test_help_manager.py | ✅ |
| Performance | test_performance.py | ✅ |

---

## 集成测试

### Checkpoint 测试

```bash
# 运行 Checkpoint 17 测试
pytest tests/test_checkpoint_17.py -v
```

### 测试内容

1. **模块导入测试**
   - 所有模块可以正常导入
   - 无导入错误

2. **模块实例化测试**
   - 所有模块可以正常创建
   - 初始化无错误

3. **模块容器测试**
   - 模块注册正常
   - 模块切换正常
   - 资源管理正常

4. **主窗口集成测试**
   - 主窗口创建正常
   - 所有组件集成正常
   - 生命周期管理正常

---

## 跨平台测试

### Windows 测试

#### 测试清单

- [ ] 应用程序启动
- [ ] 配置文件读写
- [ ] 日志文件创建
- [ ] 主题显示
- [ ] 串口功能
  - [ ] 串口列表刷新
  - [ ] 串口桥接
  - [ ] 调试终端
- [ ] 网络功能
  - [ ] TCP 中继
  - [ ] UDP 中继
- [ ] 代理功能
  - [ ] API 连接
  - [ ] 节点切换
- [ ] Grbl 功能
  - [ ] 串口连接
  - [ ] WiFi 连接
- [ ] BLE 功能
  - [ ] 设备扫描
- [ ] 性能
  - [ ] CPU 使用率 < 5%
  - [ ] 内存占用 < 200MB

#### 测试步骤

1. **安装测试**
   ```bash
   pip install 'linktunnel[gui-full]'
   ```

2. **启动测试**
   ```bash
   linktunnel-unified
   ```

3. **功能测试**
   - 测试每个模块的基本功能
   - 记录任何错误或异常

4. **性能测试**
   - 监控 CPU 和内存使用
   - 测试长时间运行稳定性

### macOS 测试

#### 测试清单

- [ ] 应用程序启动
- [ ] 配置文件读写
- [ ] 日志文件创建
- [ ] 主题显示
- [ ] 串口功能
- [ ] 网络功能
- [ ] 代理功能
- [ ] Grbl 功能
- [ ] BLE 功能（需要权限）
- [ ] 性能

#### 特殊注意

- 蓝牙权限请求
- 串口设备路径（/dev/cu.*）
- 配置文件位置验证

### Linux 测试

#### 测试清单

- [ ] 应用程序启动
- [ ] 配置文件读写
- [ ] 日志文件创建
- [ ] 主题显示
- [ ] 串口功能（需要权限）
- [ ] 网络功能
- [ ] 代理功能
- [ ] Grbl 功能
- [ ] BLE 功能（需要 BlueZ）
- [ ] I2C 功能（Linux 专有）
- [ ] 性能

#### 特殊注意

- 串口权限（dialout 组）
- I2C 权限（i2c 组）
- 蓝牙服务状态
- Qt 依赖库

#### 测试命令

```bash
# 检查权限
groups

# 检查串口设备
ls /dev/ttyUSB* /dev/ttyACM*

# 检查 I2C 设备
ls /dev/i2c-*

# 检查蓝牙服务
systemctl status bluetooth
```

---

## 性能测试

### 性能指标

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| 启动时间 | < 3s | 手动计时 |
| 空闲 CPU | < 5% | 任务管理器 |
| 空闲内存 | < 200MB | 任务管理器 |
| 模块切换 | < 100ms | 自动测试 |
| 日志处理 | 5000 行流畅 | 自动测试 |

### 性能测试脚本

```python
# tests/test_performance_metrics.py
import pytest
import time
from linktunnel.unified_gui.utils.performance import (
    MemoryOptimizer,
    CPUOptimizer,
    PerformanceMonitor
)

def test_memory_usage():
    """测试内存使用"""
    info = MemoryOptimizer.get_memory_usage()
    assert info['rss_mb'] < 200, f"内存使用过高: {info['rss_mb']:.1f} MB"

def test_cpu_usage():
    """测试 CPU 使用率"""
    cpu = CPUOptimizer.get_cpu_usage()
    assert cpu < 50, f"CPU 使用率过高: {cpu:.1f}%"

def test_module_switching_performance():
    """测试模块切换性能"""
    monitor = PerformanceMonitor()
    
    monitor.checkpoint("开始")
    # 模拟模块切换
    time.sleep(0.05)
    monitor.checkpoint("结束")
    
    # 检查耗时
    report = monitor.get_report()
    assert "结束" in report
```

### 运行性能测试

```bash
pytest tests/test_performance_metrics.py -v
```

---

## 测试报告

### 测试报告模板

```markdown
# 测试报告

**日期**: YYYY-MM-DD
**版本**: 0.3.0
**测试人员**: [姓名]
**平台**: [Windows/macOS/Linux]

## 测试环境

- 操作系统: [详细版本]
- Python 版本: [版本号]
- PyQt6 版本: [版本号]

## 测试结果

### 功能测试

| 功能 | 状态 | 备注 |
|------|------|------|
| 应用启动 | ✅/❌ | |
| 串口工具 | ✅/❌ | |
| 网络中继 | ✅/❌ | |
| 代理管理 | ✅/❌ | |
| Grbl CNC | ✅/❌ | |
| BLE 扫描 | ✅/❌ | |
| I2C 扫描 | ✅/❌ | |

### 性能测试

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 启动时间 | < 3s | [实际值] | ✅/❌ |
| 空闲 CPU | < 5% | [实际值] | ✅/❌ |
| 空闲内存 | < 200MB | [实际值] | ✅/❌ |

### 发现的问题

1. [问题描述]
   - 严重程度: [高/中/低]
   - 复现步骤: [步骤]
   - 预期结果: [描述]
   - 实际结果: [描述]

## 总结

[测试总结]

## 建议

[改进建议]
```

### 生成测试报告

```bash
# 生成 HTML 报告
pytest tests/ --html=report.html --self-contained-html

# 生成覆盖率报告
pytest tests/ --cov=src/linktunnel/unified_gui --cov-report=html
```

---

## 自动化测试

### CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e '.[dev,gui-full]'
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src/linktunnel/unified_gui
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 测试最佳实践

### 1. 编写可测试的代码

```python
# 好的做法：依赖注入
class MyModule(BaseModule):
    def __init__(self, config_manager, log_manager):
        self.config_manager = config_manager
        self.log_manager = log_manager

# 不好的做法：硬编码依赖
class MyModule(BaseModule):
    def __init__(self):
        self.config_manager = ConfigManager()  # 难以测试
```

### 2. 使用 Mock 对象

```python
from unittest.mock import Mock, patch

def test_with_mock():
    mock_config = Mock()
    mock_config.get.return_value = "test_value"
    
    module = MyModule(mock_config, Mock())
    assert module.config_manager.get("key") == "test_value"
```

### 3. 测试边界条件

```python
def test_boundary_conditions():
    # 测试空值
    assert function(None) is None
    
    # 测试空列表
    assert function([]) == []
    
    # 测试极大值
    assert function(sys.maxsize) > 0
```

### 4. 使用 Fixtures

```python
@pytest.fixture
def module():
    config = ConfigManager()
    log = LogManager()
    return MyModule(config, log)

def test_with_fixture(module):
    assert module.get_module_name() == "my_module"
```

---

## 常见问题

### Q1: 测试失败怎么办？

**A**: 
1. 查看错误信息
2. 检查测试环境
3. 验证依赖安装
4. 查看日志文件

### Q2: 如何跳过某些测试？

**A**: 使用 pytest 标记

```python
@pytest.mark.skip(reason="需要实际设备")
def test_serial_connection():
    pass

@pytest.mark.skipif(sys.platform != "linux", reason="仅 Linux")
def test_i2c_scan():
    pass
```

### Q3: 如何测试 GUI？

**A**: 使用 pytest-qt

```bash
pip install pytest-qt
```

```python
def test_button_click(qtbot):
    button = QPushButton("Click")
    qtbot.addWidget(button)
    
    with qtbot.waitSignal(button.clicked):
        qtbot.mouseClick(button, Qt.LeftButton)
```

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**适用版本**: linktunnel Unified GUI 0.3.0
