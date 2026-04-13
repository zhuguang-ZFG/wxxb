# linktunnel Unified GUI - API 参考

**版本**: 0.3.0  
**更新日期**: 2026-04-13

---

## 📋 目录

1. [核心 API](#核心-api)
2. [模块 API](#模块-api)
3. [UI API](#ui-api)
4. [工具 API](#工具-api)

---

## 核心 API

### ConfigManager

配置管理器，管理应用程序配置。

#### 方法

##### `get(key: str, default: Any = None) -> Any`

获取配置值。

**参数**:
- `key`: 配置键，支持点号分隔的路径，如 `"window.width"`
- `default`: 默认值，当键不存在时返回

**返回**: 配置值或默认值

**示例**:
```python
width = config_manager.get("window.width", 1280)
```

##### `set(key: str, value: Any) -> None`

设置配置值。

**参数**:
- `key`: 配置键
- `value`: 配置值

**示例**:
```python
config_manager.set("window.width", 1920)
```

##### `save() -> None`

保存配置到文件。

**示例**:
```python
config_manager.save()
```

##### `load() -> None`

从文件加载配置。

**示例**:
```python
config_manager.load()
```

---

### LogManager

日志管理器，管理应用程序日志。

#### 方法

##### `debug(module: str, message: str) -> None`

记录调试日志。

**参数**:
- `module`: 模块名称
- `message`: 日志消息

**示例**:
```python
log_manager.debug("my_module", "调试信息")
```

##### `info(module: str, message: str) -> None`

记录信息日志。

**参数**:
- `module`: 模块名称
- `message`: 日志消息

**示例**:
```python
log_manager.info("my_module", "操作成功")
```

##### `warning(module: str, message: str) -> None`

记录警告日志。

**参数**:
- `module`: 模块名称
- `message`: 日志消息

**示例**:
```python
log_manager.warning("my_module", "潜在问题")
```

##### `error(module: str, message: str) -> None`

记录错误日志。

**参数**:
- `module`: 模块名称
- `message`: 日志消息

**示例**:
```python
log_manager.error("my_module", "操作失败")
```

##### `add_callback(callback: Callable[[str, str, str], None]) -> None`

添加日志回调函数。

**参数**:
- `callback`: 回调函数，接收 (level, module, message) 三个参数

**示例**:
```python
def on_log(level, module, message):
    print(f"[{level}] {module}: {message}")

log_manager.add_callback(on_log)
```

---

### ModuleContainer

模块容器，管理功能模块。

#### 方法

##### `register_module(module: BaseModule) -> None`

注册功能模块。

**参数**:
- `module`: 模块实例

**示例**:
```python
module = MyModule(config_manager, log_manager)
container.register_module(module)
```

##### `show_module(name: str) -> None`

显示指定模块。

**参数**:
- `name`: 模块名称

**示例**:
```python
container.show_module("my_module")
```

##### `get_active_module() -> BaseModule | None`

获取当前活动模块。

**返回**: 活动模块实例或 None

**示例**:
```python
active = container.get_active_module()
if active:
    print(active.get_display_name())
```

##### `stop_all_modules() -> None`

停止所有运行中的模块。

**示例**:
```python
container.stop_all_modules()
```

---

### BaseModule

模块基类，所有功能模块必须继承此类。

#### 抽象方法

##### `get_module_name() -> str`

返回模块唯一标识符。

**返回**: 模块名称（小写字母和下划线）

**示例**:
```python
def get_module_name(self) -> str:
    return "my_module"
```

##### `get_display_name() -> str`

返回模块显示名称。

**返回**: 显示名称（用户友好的名称）

**示例**:
```python
def get_display_name(self) -> str:
    return "我的模块"
```

#### 可选方法

##### `on_activate() -> None`

模块被激活时调用。

**示例**:
```python
def on_activate(self) -> None:
    self.log_manager.debug(self.get_module_name(), "模块已激活")
```

##### `on_deactivate() -> None`

模块被停用时调用。

**示例**:
```python
def on_deactivate(self) -> None:
    self._save_config()
```

##### `stop() -> None`

停止模块运行。

**示例**:
```python
def stop(self) -> None:
    if self._running:
        self._running = False
        self.log_manager.info(self.get_module_name(), "模块已停止")
```

##### `is_running() -> bool`

返回模块是否正在运行。

**返回**: True 表示运行中，False 表示未运行

**示例**:
```python
def is_running(self) -> bool:
    return self._running
```

##### `get_occupied_resources() -> list[str]`

返回模块占用的资源列表。

**返回**: 资源标识符列表

**示例**:
```python
def get_occupied_resources(self) -> list[str]:
    if self._running:
        return ["serial:/dev/ttyUSB0"]
    return []
```

---

### ThemeManager

主题管理器，管理应用程序主题。

#### 枚举

##### `Theme`

主题枚举。

- `Theme.LIGHT`: 浅色主题
- `Theme.DARK`: 深色主题
- `Theme.SYSTEM`: 系统主题

#### 方法

##### `set_theme(theme: Theme) -> None`

设置主题。

**参数**:
- `theme`: 主题枚举值

**示例**:
```python
theme_manager.set_theme(Theme.DARK)
```

##### `get_current_theme() -> Theme`

获取当前主题。

**返回**: 当前主题枚举值

**示例**:
```python
current = theme_manager.get_current_theme()
```

##### `toggle_theme() -> None`

切换主题（浅色 ↔ 深色）。

**示例**:
```python
theme_manager.toggle_theme()
```

##### `apply_theme() -> None`

应用当前主题。

**示例**:
```python
theme_manager.apply_theme()
```

---

### FeedbackManager

反馈管理器，管理用户反馈。

#### 方法

##### `show_info(title: str, message: str) -> None`

显示信息对话框。

**参数**:
- `title`: 标题
- `message`: 消息内容

**示例**:
```python
feedback_manager.show_info("提示", "操作成功")
```

##### `show_success(title: str, message: str) -> None`

显示成功对话框。

**参数**:
- `title`: 标题
- `message`: 消息内容

**示例**:
```python
feedback_manager.show_success("成功", "数据已保存")
```

##### `show_warning(title: str, message: str) -> None`

显示警告对话框。

**参数**:
- `title`: 标题
- `message`: 消息内容

**示例**:
```python
feedback_manager.show_warning("警告", "配置可能不正确")
```

##### `show_error(title: str, message: str, details: str = None) -> None`

显示错误对话框。

**参数**:
- `title`: 标题
- `message`: 消息内容
- `details`: 详细错误信息（可选）

**示例**:
```python
feedback_manager.show_error("错误", "操作失败", str(exception))
```

##### `show_question(title: str, message: str) -> bool`

显示确认对话框。

**参数**:
- `title`: 标题
- `message`: 消息内容

**返回**: True 表示确认，False 表示取消

**示例**:
```python
if feedback_manager.show_question("确认", "确定要删除吗？"):
    # 执行删除
    pass
```

##### `show_status(message: str, timeout: int = 3000) -> None`

在状态栏显示消息。

**参数**:
- `message`: 消息内容
- `timeout`: 超时时间（毫秒）

**示例**:
```python
feedback_manager.show_status("正在处理...", 5000)
```

---

### HelpManager

帮助管理器，管理帮助和文档。

#### 方法

##### `show_user_manual() -> None`

显示用户手册。

**示例**:
```python
help_manager.show_user_manual()
```

##### `show_shortcuts() -> None`

显示快捷键列表。

**示例**:
```python
help_manager.show_shortcuts()
```

##### `show_module_help(module_name: str) -> None`

显示模块帮助。

**参数**:
- `module_name`: 模块名称

**示例**:
```python
help_manager.show_module_help("serial")
```

##### `open_online_docs() -> None`

在浏览器中打开在线文档。

**示例**:
```python
help_manager.open_online_docs()
```

##### `open_github_repo() -> None`

在浏览器中打开 GitHub 仓库。

**示例**:
```python
help_manager.open_github_repo()
```

---

## 模块 API

### SerialModule

串口工具模块。

#### 方法

##### `refresh_ports() -> None`

刷新串口列表。

**示例**:
```python
serial_module.refresh_ports()
```

##### `start_bridge(port_a: str, port_b: str, baudrate: int) -> None`

开始串口桥接。

**参数**:
- `port_a`: 端口 A
- `port_b`: 端口 B
- `baudrate`: 波特率

**示例**:
```python
serial_module.start_bridge("/dev/ttyUSB0", "/dev/ttyUSB1", 115200)
```

##### `stop_bridge() -> None`

停止串口桥接。

**示例**:
```python
serial_module.stop_bridge()
```

---

### NetworkModule

网络中继模块。

#### 方法

##### `start_tcp_relay(listen_addr: str, listen_port: int, target_addr: str, target_port: int) -> None`

开始 TCP 中继。

**参数**:
- `listen_addr`: 监听地址
- `listen_port`: 监听端口
- `target_addr`: 目标地址
- `target_port`: 目标端口

**示例**:
```python
network_module.start_tcp_relay("0.0.0.0", 8080, "192.168.1.100", 80)
```

##### `stop_tcp_relay() -> None`

停止 TCP 中继。

**示例**:
```python
network_module.stop_tcp_relay()
```

---

### ProxyModule

代理管理模块。

#### 方法

##### `connect(api_url: str, secret: str = None) -> bool`

连接到代理 API。

**参数**:
- `api_url`: API 地址
- `secret`: API 密钥（可选）

**返回**: True 表示连接成功，False 表示失败

**示例**:
```python
if proxy_module.connect("http://127.0.0.1:9090", "my_secret"):
    print("连接成功")
```

##### `disconnect() -> None`

断开连接。

**示例**:
```python
proxy_module.disconnect()
```

##### `test_delay() -> None`

测试所有节点延迟。

**示例**:
```python
proxy_module.test_delay()
```

##### `switch_node(group: str, node: str) -> bool`

切换节点。

**参数**:
- `group`: 策略组名称
- `node`: 节点名称

**返回**: True 表示切换成功，False 表示失败

**示例**:
```python
if proxy_module.switch_node("PROXY", "HK-01"):
    print("切换成功")
```

---

## UI API

### LogViewer

日志查看器组件。

#### 方法

##### `append_log(level: str, module: str, message: str) -> None`

添加日志条目。

**参数**:
- `level`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `module`: 模块名称
- `message`: 日志消息

**示例**:
```python
log_viewer.append_log("INFO", "my_module", "操作成功")
```

##### `clear() -> None`

清空日志。

**示例**:
```python
log_viewer.clear()
```

---

### NavigationSystem

导航系统组件。

#### 方法

##### `add_module(name: str, display_name: str, icon: QIcon) -> None`

添加模块到导航。

**参数**:
- `name`: 模块名称
- `display_name`: 显示名称
- `icon`: 模块图标

**示例**:
```python
navigation.add_module("my_module", "我的模块", QIcon())
```

##### `set_active_module(name: str) -> None`

设置活动模块。

**参数**:
- `name`: 模块名称

**示例**:
```python
navigation.set_active_module("my_module")
```

#### 信号

##### `module_changed(str)`

模块切换信号。

**参数**: 新模块名称

**示例**:
```python
navigation.module_changed.connect(self._on_module_changed)
```

---

## 工具 API

### TooltipHelper

工具提示辅助类。

#### 静态方法

##### `set_tooltip(widget: QWidget, text: str) -> None`

设置控件工具提示。

**参数**:
- `widget`: Qt 控件
- `text`: 提示文本

**示例**:
```python
TooltipHelper.set_tooltip(button, "点击开始")
```

##### `set_module_tooltips(module: BaseModule) -> None`

设置模块所有控件的工具提示。

**参数**:
- `module`: 模块实例

**示例**:
```python
TooltipHelper.set_module_tooltips(self)
```

---

### MemoryOptimizer

内存优化器。

#### 静态方法

##### `force_gc() -> None`

强制垃圾回收。

**示例**:
```python
MemoryOptimizer.force_gc()
```

##### `get_memory_usage() -> dict[str, Any]`

获取内存使用情况。

**返回**: 包含内存信息的字典

**示例**:
```python
info = MemoryOptimizer.get_memory_usage()
print(f"内存使用: {info['rss_mb']:.1f} MB")
```

##### `optimize_memory() -> None`

优化内存使用。

**示例**:
```python
MemoryOptimizer.optimize_memory()
```

---

### CPUOptimizer

CPU 优化器。

#### 静态方法

##### `get_cpu_usage() -> float`

获取 CPU 使用率。

**返回**: CPU 使用率百分比

**示例**:
```python
cpu = CPUOptimizer.get_cpu_usage()
print(f"CPU 使用率: {cpu:.1f}%")
```

##### `is_high_cpu_usage(threshold: float = 50.0) -> bool`

检查 CPU 使用率是否过高。

**参数**:
- `threshold`: 阈值（百分比）

**返回**: True 表示超过阈值

**示例**:
```python
if CPUOptimizer.is_high_cpu_usage(80.0):
    print("CPU 使用率过高")
```

---

### PerformanceMonitor

性能监控器。

#### 方法

##### `checkpoint(name: str) -> None`

记录性能检查点。

**参数**:
- `name`: 检查点名称

**示例**:
```python
monitor = PerformanceMonitor()
monitor.checkpoint("开始")
# ... 执行操作 ...
monitor.checkpoint("结束")
```

##### `get_report() -> str`

获取性能报告。

**返回**: 性能报告字符串

**示例**:
```python
print(monitor.get_report())
```

##### `reset() -> None`

重置监控器。

**示例**:
```python
monitor.reset()
```

---

### 装饰器

#### `@debounce(wait_ms: int)`

防抖装饰器，延迟执行函数。

**参数**:
- `wait_ms`: 等待时间（毫秒）

**示例**:
```python
from linktunnel.unified_gui.utils.performance import debounce

@debounce(500)
def on_text_changed(text):
    print(f"文本: {text}")
```

#### `@throttle(wait_ms: int)`

节流装饰器，限制函数执行频率。

**参数**:
- `wait_ms`: 最小间隔时间（毫秒）

**示例**:
```python
from linktunnel.unified_gui.utils.performance import throttle

@throttle(1000)
def on_mouse_move(x, y):
    print(f"位置: ({x}, {y})")
```

#### `@measure_time`

时间测量装饰器，测量函数执行时间。

**示例**:
```python
from linktunnel.unified_gui.utils.performance import measure_time

@measure_time
def expensive_operation():
    # 耗时操作
    pass
```

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**适用版本**: linktunnel Unified GUI 0.3.0
