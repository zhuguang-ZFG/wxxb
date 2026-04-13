# linktunnel Unified GUI - 架构文档

**版本**: 0.3.0  
**更新日期**: 2026-04-13

---

## 📋 目录

1. [架构概述](#架构概述)
2. [技术栈](#技术栈)
3. [项目结构](#项目结构)
4. [核心组件](#核心组件)
5. [模块系统](#模块系统)
6. [数据流](#数据流)
7. [设计模式](#设计模式)
8. [性能优化](#性能优化)

---

## 架构概述

linktunnel Unified GUI 采用模块化架构设计，将应用程序分为核心层、模块层和 UI 层三个主要层次。

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    应用程序层                             │
│                   (MainWindow)                          │
├─────────────────────────────────────────────────────────┤
│                     UI 层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ NavigationSys│  │  LogViewer   │  │ ThemeManager │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    模块层                                │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │Serial│ │Network│ │Proxy│ │ Grbl │ │ BLE  │ │ I2C  ││
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘│
├─────────────────────────────────────────────────────────┤
│                    核心层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ConfigManager │  │ LogManager   │  │ModuleContainer│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │FeedbackMgr   │  │ HelpManager  │  │PerformanceMgr│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 设计原则

1. **模块化** - 功能模块独立，易于扩展
2. **松耦合** - 模块间通过接口通信
3. **高内聚** - 相关功能集中在同一模块
4. **可测试** - 每个组件都可独立测试
5. **可维护** - 代码结构清晰，文档完整

---

## 技术栈

### 主要技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 编程语言 |
| PyQt6 | 6.4+ | GUI 框架 |
| pyserial | 3.5+ | 串口通信 |

### 可选依赖

| 技术 | 版本 | 用途 |
|------|------|------|
| bleak | latest | BLE 蓝牙扫描 |
| smbus2 | latest | I2C 通信 |
| psutil | latest | 性能监控 |

### 开发工具

| 工具 | 用途 |
|------|------|
| pytest | 单元测试 |
| ruff | 代码检查 |
| black | 代码格式化 |
| mypy | 类型检查 |

---

## 项目结构

```
linktunnel/
├── src/
│   └── linktunnel/
│       └── unified_gui/
│           ├── __init__.py           # 包初始化
│           ├── __main__.py           # 应用入口
│           ├── core/                 # 核心组件
│           │   ├── base_module.py    # 模块基类
│           │   ├── config_manager.py # 配置管理
│           │   ├── log_manager.py    # 日志管理
│           │   ├── main_window.py    # 主窗口
│           │   ├── module_container.py # 模块容器
│           │   ├── theme_manager.py  # 主题管理
│           │   ├── feedback_manager.py # 反馈管理
│           │   └── help_manager.py   # 帮助管理
│           ├── modules/              # 功能模块
│           │   ├── serial_module.py  # 串口模块
│           │   ├── network_module.py # 网络模块
│           │   ├── proxy_module.py   # 代理模块
│           │   ├── grbl_module.py    # Grbl 模块
│           │   ├── ble_module.py     # BLE 模块
│           │   └── i2c_module.py     # I2C 模块
│           ├── ui/                   # UI 组件
│           │   ├── log_viewer.py     # 日志查看器
│           │   └── navigation_system.py # 导航系统
│           └── utils/                # 工具函数
│               ├── tooltip_helper.py # 工具提示
│               └── performance.py    # 性能工具
├── tests/                            # 测试文件
├── docs/                             # 文档
└── pyproject.toml                    # 项目配置
```

---

## 核心组件

### 1. ConfigManager (配置管理器)

**职责**: 管理应用程序配置

**功能**:
- 加载和保存配置
- 跨平台配置目录
- 配置验证
- 默认配置

**接口**:
```python
class ConfigManager:
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
    def save(self) -> None
    def load(self) -> None
```

### 2. LogManager (日志管理器)

**职责**: 管理应用程序日志

**功能**:
- 多级别日志
- 文件轮转
- 实时回调
- 跨平台日志目录

**接口**:
```python
class LogManager:
    def debug(self, module: str, message: str) -> None
    def info(self, module: str, message: str) -> None
    def warning(self, module: str, message: str) -> None
    def error(self, module: str, message: str) -> None
    def add_callback(self, callback: Callable) -> None
```

### 3. ModuleContainer (模块容器)

**职责**: 管理功能模块生命周期

**功能**:
- 模块注册
- 模块切换
- 资源管理
- 冲突检测

**接口**:
```python
class ModuleContainer:
    def register_module(self, module: BaseModule) -> None
    def show_module(self, name: str) -> None
    def get_active_module(self) -> BaseModule | None
    def stop_all_modules(self) -> None
```

### 4. BaseModule (模块基类)

**职责**: 定义模块接口

**功能**:
- 生命周期管理
- 配置持久化
- 资源声明
- 日志输出

**接口**:
```python
class BaseModule(ABC):
    @abstractmethod
    def get_module_name(self) -> str
    
    @abstractmethod
    def get_display_name(self) -> str
    
    def on_activate(self) -> None
    def on_deactivate(self) -> None
    def stop(self) -> None
    def is_running(self) -> bool
    def get_occupied_resources(self) -> list[str]
```

---

## 模块系统

### 模块生命周期

```
注册 → 激活 → 运行 → 停用 → 销毁
  ↓      ↓      ↓      ↓      ↓
register activate run deactivate destroy
```

### 模块状态

- **Inactive**: 未激活
- **Active**: 已激活但未运行
- **Running**: 正在运行
- **Stopping**: 正在停止

### 资源管理

模块可以声明占用的资源：

```python
def get_occupied_resources(self) -> list[str]:
    if self.is_running():
        return ["serial:/dev/ttyUSB0"]
    return []
```

容器会检测资源冲突，防止多个模块同时使用同一资源。

---

## 数据流

### 配置流

```
用户输入 → UI 组件 → 模块 → ConfigManager → 配置文件
```

### 日志流

```
模块 → LogManager → 回调 → LogViewer → 用户界面
                  ↓
              日志文件
```

### 事件流

```
用户操作 → UI 事件 → 信号 → 槽函数 → 模块方法
```

---

## 设计模式

### 1. 单例模式

**应用**: ConfigManager, LogManager

**目的**: 确保全局唯一实例

```python
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. 观察者模式

**应用**: LogManager 回调系统

**目的**: 解耦日志生产者和消费者

```python
class LogManager:
    def __init__(self):
        self._callbacks = []
    
    def add_callback(self, callback):
        self._callbacks.append(callback)
    
    def _emit(self, level, module, message):
        for callback in self._callbacks:
            callback(level, module, message)
```

### 3. 策略模式

**应用**: 主题系统

**目的**: 动态切换主题

```python
class ThemeManager:
    def set_theme(self, theme: Theme):
        if theme == Theme.LIGHT:
            self._apply_light_theme()
        elif theme == Theme.DARK:
            self._apply_dark_theme()
```

### 4. 模板方法模式

**应用**: BaseModule

**目的**: 定义模块框架

```python
class BaseModule(ABC):
    def activate(self):
        self.on_activate()  # 子类实现
        self._is_active = True
```

---

## 性能优化

### 1. 批量处理

日志查看器使用批量处理减少 UI 更新：

```python
self._log_buffer = []
self._buffer_size = 100

def append_log(self, level, module, message):
    self._log_buffer.append((level, module, message))
    if len(self._log_buffer) >= self._buffer_size:
        self._flush_log_buffer()
```

### 2. 异步操作

模块切换使用异步操作避免阻塞：

```python
QTimer.singleShot(0, current.on_deactivate)
self.setCurrentWidget(target_module)
QTimer.singleShot(0, target_module.on_activate)
```

### 3. 延迟加载

模块按需加载，减少启动时间。

### 4. 资源池

重用对象，减少创建开销。

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**适用版本**: linktunnel Unified GUI 0.3.0
