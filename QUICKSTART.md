# linktunnel Unified GUI - 快速启动指南

## 5 分钟快速上手

### 1. 安装依赖

```bash
# 进入项目目录
cd /path/to/wxxb

# 激活虚拟环境（如果有）
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 安装 GUI 依赖
pip install 'PyQt6>=6.6'

# 或者安装完整依赖
pip install -e '.[gui]'
```

### 2. 启动应用

```bash
# 方式 1: 使用 Python 模块
python -m linktunnel.unified_gui

# 方式 2: 使用命令行入口（需要先 pip install -e .）
linktunnel-unified
```

### 3. 界面说明

启动后你会看到：

```
┌─────────────────────────────────────────────────────────┐
│ linktunnel Unified GUI                                  │
├──────────┬──────────────────────────────────────────────┤
│ 导航栏   │ 模块内容区域                                 │
│          │                                              │
│ 串口工具 │ [当前选中模块的界面]                         │
│ 网络中继 │                                              │
│ 代理管理 │                                              │
│          │                                              │
├──────────┴──────────────────────────────────────────────┤
│ 日志查看器                                              │
│ [INFO] 应用程序启动                                     │
│ [INFO] 发现 3 个串口                                    │
└─────────────────────────────────────────────────────────┘
│ 状态栏: 就绪                                            │
└─────────────────────────────────────────────────────────┘
```

### 4. 使用串口工具

1. 点击左侧 **"串口工具"**
2. 点击 **"刷新串口列表"** 查看可用串口
3. 选择 **"串口桥接"** 或 **"调试终端"** 标签页
4. 配置参数后点击 **"启动"**

### 5. 使用网络中继

1. 点击左侧 **"网络中继"**
2. 选择 **"TCP 中继"** 或 **"UDP 中继"** 标签页
3. 配置监听地址和目标地址
4. 点击 **"启动中继"**

## 常见问题

### Q: 提示 "未安装 PyQt6"

**A**: 运行以下命令安装：
```bash
pip install PyQt6
```

### Q: 串口列表为空

**A**: 
1. 确保有串口设备连接
2. 检查设备驱动是否安装
3. 在 macOS 上可能需要授予权限

### Q: 如何查看详细日志？

**A**: 日志文件位置：
- **macOS**: `~/Library/Logs/linktunnel/unified-gui/unified_gui.log`
- **Linux**: `~/.local/share/linktunnel/unified-gui/logs/unified_gui.log`
- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\logs\unified_gui.log`

### Q: 如何修改配置？

**A**: 配置文件位置：
- **macOS**: `~/Library/Application Support/linktunnel/unified-gui/config.json`
- **Linux**: `~/.config/linktunnel/unified-gui/config.json`
- **Windows**: `%LOCALAPPDATA%\linktunnel\unified-gui\config.json`

可以手动编辑 JSON 文件，或在应用中修改后自动保存。

### Q: 如何使用 tkinter 版本？

**A**: 如果不想安装 PyQt6，直接运行即可自动降级到 tkinter：
```bash
# 确保没有安装 PyQt6
pip uninstall PyQt6

# 运行应用（会自动使用 tkinter）
python -m linktunnel.unified_gui
```

## 下一步

- 查看完整文档: `src/linktunnel/unified_gui/README.md`
- 查看实施总结: `IMPLEMENTATION_SUMMARY.md`
- 查看需求文档: `.kiro/specs/unified-gui/requirements.md`
- 查看设计文档: `.kiro/specs/unified-gui/design.md`

## 反馈和贡献

如有问题或建议，请查看项目的 GitHub 仓库或联系维护者。

---

**提示**: 这是一个正在开发中的项目，部分功能可能尚未完全实现。
