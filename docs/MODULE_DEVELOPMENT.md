# linktunnel Unified GUI - 模块开发指南

**版本**: 0.3.0  
**更新日期**: 2026-04-13

---

## 📋 目录

1. [快速开始](#快速开始)
2. [模块基础](#模块基础)
3. [开发步骤](#开发步骤)
4. [最佳实践](#最佳实践)
5. [测试指南](#测试指南)
6. [示例模块](#示例模块)

---

## 快速开始

### 创建新模块的步骤

1. 继承 `BaseModule` 类
2. 实现必需方法
3. 创建 UI 界面
4. 注册模块
5. 编写测试

### 最小示例

```python
from linktunnel.unified_gui.core.base_module import BaseModule
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MyModule(BaseModule):
    def __init__(self, config_manager, log_manager, parent=None):
        super().__init__(config_manager, log_manager, parent)
        self._setup_ui()
    
    def get_module_name(self) -> str:
        return "my_module"
    
    def get_display_name(self) -> str:
        return "我的模块"
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Hello, Module!"))
```

---

## 模块基础

### BaseModule 类

所有功能模块必须继承 `BaseModule` 类。

#### 必需方法

```python
@abstractmethod
def get_module_name(self) -> str:
    """返回模块唯一标识符"""
    pass

@abstractmethod
def get_display_name(self) -> str:
    """返回模块显示名称"""
    pass
```

#### 可选方法

```python
def on_activate(self) -> None:
    """模块被激活时调用"""
    pass

def on_deactivate(self) -> None:
    """模块被停用时调用"""
    pass

def stop(self) -> None:
    """停止模块运行"""
    pass

def is_running(self) -> bool:
    """返回模块是否正在运行"""
    return False

def get_occupied_resources(self) -> list[str]:
    """返回模块占用的资源列表"""
    return []
```

### 生命周期

```
创建 → 注册 → 激活 → 运行 → 停用 → 销毁
  ↓      ↓      ↓      ↓      ↓      ↓
__init__ register activate run deactivate __del__
```

---

## 开发步骤

### 步骤 1: 创建模块文件

在 `src/linktunnel/unified_gui/modules/` 创建新文件：

```bash
touch src/linktunnel/unified_gui/modules/my_module.py
```

### 步骤 2: 导入依赖

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
    from PyQt6.QtCore import Qt
    
    from linktunnel.unified_gui.core.base_module import BaseModule
    
    # PyQt6 实现
    class MyModule(BaseModule):
        pass

except ImportError:
    # tkinter 备选实现
    import tkinter as tk
    from tkinter import ttk
    
    from linktunnel.unified_gui.core.base_module import BaseModule
    
    class MyModule(BaseModule):  # type: ignore
        pass
```

### 步骤 3: 实现模块类

```python
class MyModule(BaseModule):
    """我的模块"""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        log_manager: LogManager,
        parent: QWidget | None = None
    ):
        super().__init__(config_manager, log_manager, parent)
        
        # 初始化状态
        self._running = False
        
        # 设置 UI
        self._setup_ui()
        
        # 加载配置
        self._load_config()
    
    def get_module_name(self) -> str:
        return "my_module"
    
    def get_display_name(self) -> str:
        return "我的模块"
    
    def _setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 添加控件
        self.start_btn = QPushButton("开始")
        self.start_btn.clicked.connect(self._on_start)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self._on_stop)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
    
    def _load_config(self) -> None:
        """加载配置"""
        config = self.config_manager.get(f"modules.{self.get_module_name()}", {})
        # 应用配置
    
    def _save_config(self) -> None:
        """保存配置"""
        config = {
            # 配置项
        }
        self.config_manager.set(f"modules.{self.get_module_name()}", config)
    
    def _on_start(self) -> None:
        """开始按钮点击"""
        self._running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_manager.info(self.get_module_name(), "模块已启动")
    
    def _on_stop(self) -> None:
        """停止按钮点击"""
        self.stop()
    
    def on_activate(self) -> None:
        """模块激活"""
        self.log_manager.debug(self.get_module_name(), "模块已激活")
    
    def on_deactivate(self) -> None:
        """模块停用"""
        self._save_config()
        self.log_manager.debug(self.get_module_name(), "模块已停用")
    
    def stop(self) -> None:
        """停止模块"""
        if self._running:
            self._running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.log_manager.info(self.get_module_name(), "模块已停止")
    
    def is_running(self) -> bool:
        """返回运行状态"""
        return self._running
    
    def get_occupied_resources(self) -> list[str]:
        """返回占用的资源"""
        if self._running:
            return ["my_resource"]
        return []
```

### 步骤 4: 注册模块

在 `main_window.py` 的 `_register_modules` 方法中注册：

```python
def _register_modules(self) -> None:
    from linktunnel.unified_gui.modules.my_module import MyModule
    
    # 创建模块实例
    my_module = MyModule(self.config_manager, self.log_manager)
    
    # 注册到容器
    self.module_container.register_module(my_module)
    
    # 添加到导航
    self.navigation.add_module("my_module", "我的模块", QIcon())
```

### 步骤 5: 编写测试

创建 `tests/test_my_module.py`：

```python
import pytest
from linktunnel.unified_gui.modules.my_module import MyModule
from linktunnel.unified_gui.core.config_manager import ConfigManager
from linktunnel.unified_gui.core.log_manager import LogManager

@pytest.fixture
def module():
    config_manager = ConfigManager()
    log_manager = LogManager()
    return MyModule(config_manager, log_manager)

def test_module_name(module):
    assert module.get_module_name() == "my_module"

def test_module_display_name(module):
    assert module.get_display_name() == "我的模块"

def test_module_lifecycle(module):
    # 测试激活
    module.on_activate()
    
    # 测试运行
    assert not module.is_running()
    
    # 测试停用
    module.on_deactivate()
```

---

## 最佳实践

### 1. 命名规范

- **模块名**: 小写字母和下划线，如 `my_module`
- **类名**: 驼峰命名，如 `MyModule`
- **方法名**: 小写字母和下划线，如 `_setup_ui`
- **私有方法**: 以下划线开头，如 `_on_start`

### 2. 配置管理

使用模块命名空间存储配置：

```python
# 保存配置
self.config_manager.set(f"modules.{self.get_module_name()}.option", value)

# 读取配置
value = self.config_manager.get(f"modules.{self.get_module_name()}.option", default)
```

### 3. 日志记录

使用适当的日志级别：

```python
# 调试信息
self.log_manager.debug(self.get_module_name(), "详细的调试信息")

# 一般信息
self.log_manager.info(self.get_module_name(), "操作成功")

# 警告信息
self.log_manager.warning(self.get_module_name(), "潜在问题")

# 错误信息
self.log_manager.error(self.get_module_name(), "操作失败")
```

### 4. 资源管理

声明占用的资源：

```python
def get_occupied_resources(self) -> list[str]:
    resources = []
    if self._running:
        if self.serial_port:
            resources.append(f"serial:{self.serial_port}")
        if self.network_port:
            resources.append(f"network:{self.network_port}")
    return resources
```

### 5. 错误处理

使用 try-except 处理异常：

```python
def _on_start(self) -> None:
    try:
        # 执行操作
        self._do_something()
        self.log_manager.info(self.get_module_name(), "操作成功")
    except Exception as e:
        self.log_manager.error(self.get_module_name(), f"操作失败: {e}")
        # 显示错误对话框
```

### 6. UI 更新

在主线程更新 UI：

```python
from PyQt6.QtCore import QTimer

def _update_ui(self):
    # 在主线程执行
    QTimer.singleShot(0, self._do_update_ui)

def _do_update_ui(self):
    # 更新 UI 控件
    self.label.setText("新文本")
```

### 7. 后台任务

使用线程处理耗时操作：

```python
from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal(object)
    
    def run(self):
        result = self._do_work()
        self.finished.emit(result)

# 使用
self.worker = WorkerThread()
self.worker.finished.connect(self._on_finished)
self.worker.start()
```

---

## 测试指南

### 单元测试

测试模块的基本功能：

```python
def test_module_creation():
    """测试模块创建"""
    module = MyModule(config_manager, log_manager)
    assert module is not None

def test_module_name():
    """测试模块名称"""
    module = MyModule(config_manager, log_manager)
    assert module.get_module_name() == "my_module"

def test_module_lifecycle():
    """测试模块生命周期"""
    module = MyModule(config_manager, log_manager)
    
    # 激活
    module.on_activate()
    
    # 运行
    assert not module.is_running()
    
    # 停止
    module.stop()
    assert not module.is_running()
    
    # 停用
    module.on_deactivate()
```

### 集成测试

测试模块与其他组件的集成：

```python
def test_module_registration():
    """测试模块注册"""
    container = ModuleContainer(config_manager, log_manager)
    module = MyModule(config_manager, log_manager)
    
    container.register_module(module)
    assert module.get_module_name() in container._modules

def test_module_switching():
    """测试模块切换"""
    container = ModuleContainer(config_manager, log_manager)
    module1 = MyModule(config_manager, log_manager)
    module2 = AnotherModule(config_manager, log_manager)
    
    container.register_module(module1)
    container.register_module(module2)
    
    container.show_module("my_module")
    assert container.get_active_module() == module1
    
    container.show_module("another_module")
    assert container.get_active_module() == module2
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_my_module.py

# 运行并显示覆盖率
pytest tests/ --cov=src/linktunnel/unified_gui
```

---

## 示例模块

### 简单计数器模块

```python
from linktunnel.unified_gui.core.base_module import BaseModule
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class CounterModule(BaseModule):
    """计数器模块示例"""
    
    def __init__(self, config_manager, log_manager, parent=None):
        super().__init__(config_manager, log_manager, parent)
        self._count = 0
        self._setup_ui()
    
    def get_module_name(self) -> str:
        return "counter"
    
    def get_display_name(self) -> str:
        return "计数器"
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # 显示计数
        self.count_label = QLabel("0")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_label)
        
        # 增加按钮
        inc_btn = QPushButton("增加")
        inc_btn.clicked.connect(self._increment)
        layout.addWidget(inc_btn)
        
        # 减少按钮
        dec_btn = QPushButton("减少")
        dec_btn.clicked.connect(self._decrement)
        layout.addWidget(dec_btn)
        
        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._reset)
        layout.addWidget(reset_btn)
    
    def _increment(self) -> None:
        self._count += 1
        self._update_display()
        self.log_manager.info(self.get_module_name(), f"计数增加到 {self._count}")
    
    def _decrement(self) -> None:
        self._count -= 1
        self._update_display()
        self.log_manager.info(self.get_module_name(), f"计数减少到 {self._count}")
    
    def _reset(self) -> None:
        self._count = 0
        self._update_display()
        self.log_manager.info(self.get_module_name(), "计数已重置")
    
    def _update_display(self) -> None:
        self.count_label.setText(str(self._count))
    
    def on_activate(self) -> None:
        # 加载保存的计数
        self._count = self.config_manager.get(f"modules.{self.get_module_name()}.count", 0)
        self._update_display()
    
    def on_deactivate(self) -> None:
        # 保存计数
        self.config_manager.set(f"modules.{self.get_module_name()}.count", self._count)
```

---

## 常见问题

### Q1: 如何在模块间通信？

**A**: 使用信号和槽机制：

```python
from PyQt6.QtCore import pyqtSignal

class MyModule(BaseModule):
    data_changed = pyqtSignal(object)
    
    def _on_data_change(self, data):
        self.data_changed.emit(data)

# 在主窗口连接
module1.data_changed.connect(module2.on_data_received)
```

### Q2: 如何处理长时间操作？

**A**: 使用后台线程：

```python
from PyQt6.QtCore import QThread

class WorkerThread(QThread):
    def run(self):
        # 长时间操作
        pass

self.worker = WorkerThread()
self.worker.start()
```

### Q3: 如何添加模块图标？

**A**: 在注册时提供图标：

```python
from PyQt6.QtGui import QIcon

icon = QIcon("path/to/icon.png")
self.navigation.add_module("my_module", "我的模块", icon)
```

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**适用版本**: linktunnel Unified GUI 0.3.0
