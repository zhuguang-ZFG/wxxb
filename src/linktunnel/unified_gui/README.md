# linktunnel Unified GUI

统一图形界面 - 整合 linktunnel 所有功能模块的桌面应用程序。

## 当前状态

✅ **已完成的核心架构**：

1. **项目结构** - 完整的目录结构和配置
2. **配置管理器** (`ConfigManager`) - 跨平台配置加载/保存
3. **日志管理器** (`LogManager`) - 日志格式化、过滤、文件轮转
4. **模块基类** (`BaseModule`) - 所有功能模块的抽象基类
5. **日志查看器** (`LogViewer`) - 统一的日志显示组件
6. **导航系统** (`NavigationSystem`) - 侧边栏模块切换
7. **模块容器** (`ModuleContainer`) - 模块管理和显示
8. **主窗口** (`MainWindow`) - 应用程序主界面

## 架构设计

```
src/linktunnel/unified_gui/
├── __init__.py
├── __main__.py              # 应用程序入口
├── core/                    # 核心组件
│   ├── config_manager.py    # 配置管理
│   ├── log_manager.py       # 日志管理
│   ├── base_module.py       # 模块基类
│   ├── module_container.py  # 模块容器
│   └── main_window.py       # 主窗口
├── modules/                 # 功能模块
│   └── placeholder_module.py # 占位符模块（示例）
├── ui/                      # UI 组件
│   ├── log_viewer.py        # 日志查看器
│   └── navigation_system.py # 导航系统
└── utils/                   # 工具函数
```

## 技术栈

- **主要方案**: PyQt6 (需要安装: `pip install 'linktunnel[gui]'`)
- **备选方案**: tkinter (Python 内置，无需额外安装)

## 运行方式

### 使用 PyQt6 (推荐)

```bash
# 安装 GUI 依赖
pip install 'linktunnel[gui]'

# 运行应用程序
python -m linktunnel.unified_gui
# 或
linktunnel-unified
```

### 使用 tkinter (备选)

如果未安装 PyQt6，程序会自动降级到 tkinter 实现：

```bash
python -m linktunnel.unified_gui
```

## 待实现的功能模块

根据 `.kiro/specs/unified-gui/tasks.md`，以下模块尚未实现：

### 高优先级
- [ ] **串口工具模块** (`SerialModule`) - 任务 10
- [ ] **网络中继模块** (`NetworkModule`) - 任务 11
- [ ] **代理管理模块** (`ProxyModule`) - 任务 13

### 中优先级
- [ ] **Grbl CNC 控制模块** (`GrblModule`) - 任务 14
- [ ] **BLE 蓝牙扫描模块** (`BLEModule`) - 任务 15
- [ ] **I2C 扫描模块** (`I2CModule`) - 任务 16

### 低优先级
- [ ] 主题系统 - 任务 18
- [ ] 错误处理和用户反馈 - 任务 19
- [ ] 帮助和文档功能 - 任务 20
- [ ] 性能优化 - 任务 21

## 如何添加新模块

1. 在 `modules/` 目录创建新模块文件
2. 继承 `BaseModule` 类
3. 实现必需的抽象方法：
   - `get_module_name()` - 返回模块内部名称
   - `get_display_name()` - 返回显示名称
   - `get_icon()` - 返回模块图标
4. 在 `main_window.py` 的 `_register_modules()` 中注册模块

### 示例代码

```python
from linktunnel.unified_gui.core.base_module import BaseModule
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QLabel

class MyModule(BaseModule):
    def get_module_name(self) -> str:
        return "my_module"
    
    def get_display_name(self) -> str:
        return "我的模块"
    
    def get_icon(self) -> QIcon:
        return QIcon()  # 或加载实际图标
    
    def __init__(self, config_manager, log_manager, parent=None):
        super().__init__(config_manager, log_manager, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("模块内容"))
```

## 配置文件位置

- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\config.json`
- **macOS**: `~/Library/Application Support/linktunnel/unified-gui/config.json`
- **Linux**: `~/.config/linktunnel/unified-gui/config.json`

## 日志文件位置

- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\logs\`
- **macOS**: `~/Library/Logs/linktunnel/unified-gui/`
- **Linux**: `~/.local/share/linktunnel/unified-gui/logs/`

## 开发指南

### 运行测试

```bash
# 安装开发依赖
pip install -e '.[dev,gui]'

# 运行测试
pytest tests/

# 代码检查
ruff check src/linktunnel/unified_gui/
ruff format src/linktunnel/unified_gui/
```

### 调试模式

设置日志级别为 DEBUG：

```python
# 修改 config.json
{
  "log_level": "DEBUG"
}
```

## 下一步计划

1. 实现串口工具模块（复用 `serial_term.py` 和 `bridge.py`）
2. 实现网络中继模块（复用 `tcp_udp.py`）
3. 实现代理管理模块（整合 `client_app.py`）
4. 添加主题系统（浅色/深色模式）
5. 完善错误处理和用户反馈
6. 编写用户文档和开发者文档
7. 跨平台测试和打包

## 参考资料

- **需求文档**: `.kiro/specs/unified-gui/requirements.md`
- **设计文档**: `.kiro/specs/unified-gui/design.md`
- **任务列表**: `.kiro/specs/unified-gui/tasks.md`
- **PyQt6 文档**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **参考项目**:
  - RYCOM: https://github.com/rymcu/RYCOM
  - Clash Verge Rev: https://github.com/clash-verge-rev/clash-verge-rev

## 许可证

遵循 linktunnel 项目的许可证（见根目录 LICENSE 文件）。
