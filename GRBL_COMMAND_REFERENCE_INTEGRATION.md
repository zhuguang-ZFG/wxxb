# Grbl 命令参考功能集成

## 概述

Grbl 命令参考功能已成功集成到 Grbl CNC 模块中。用户现在可以在应用程序中直接查看、搜索和发送 Grbl 命令。

## 新增功能

### 1. 命令参考标签页
- 在 Grbl 模块中添加了新的"命令参考"标签页
- 包含 4 个命令类别：
  - **系统命令** (15 个): $H, $X, $, $#, $G, $I, $N, $C, $RST, ?, !, ~, ^X 等
  - **G 代码命令** (20 个): G0, G1, G2, G3, G4, G10, G17-G19, G20-G21, G28, G30, G53, G54-G59, G80, G90-G95
  - **M 代码命令** (11 个): M0, M1, M2, M3, M4, M5, M6, M7, M8, M9, M30
  - **参数设置** (30+ 个): $0-$132 等所有 Grbl 参数

### 2. 搜索功能
- 实时搜索框，支持按命令名称或关键词搜索
- 搜索结果实时更新
- 支持中文和英文搜索

### 3. 命令详情显示
- 选中命令后显示详细说明
- 包含命令名称和完整描述

### 4. 快速发送功能
- "发送选中命令"按钮
- 一键发送选中的命令到 Grbl 设备
- 需要先连接设备

## 实现细节

### 新增类

#### GrblCommandHelper
```python
class GrblCommandHelper:
    """Grbl 命令助手"""
    
    @staticmethod
    def get_all_commands() -> dict[str, dict[str, str]]:
        """获取所有命令"""
    
    @staticmethod
    def get_command_description(cmd: str) -> str:
        """获取命令描述"""
    
    @staticmethod
    def search_commands(keyword: str) -> list[tuple[str, str, str]]:
        """搜索命令 - 返回 (category, cmd, desc) 列表"""
```

### 新增方法

#### GrblModule
- `_create_commands_tab()` - 创建命令参考标签页
- `_populate_commands()` - 填充命令列表
- `_on_cmd_search_changed(text)` - 处理搜索框变化
- `_on_cmd_selected(item)` - 处理命令选择
- `_on_send_selected_cmd()` - 发送选中的命令

### 数据结构

GRBL_COMMANDS 字典包含所有命令及其描述：
```python
GRBL_COMMANDS = {
    "系统命令": {
        "$H": "回零 - 执行归零循环",
        "$X": "解锁 - 解除警报状态",
        ...
    },
    "G 代码命令": {
        "G0": "快速移动 - 不切割移动到指定位置",
        ...
    },
    ...
}
```

## 使用方法

### 查看命令
1. 打开 Grbl CNC 模块
2. 点击"命令参考"标签页
3. 浏览命令列表

### 搜索命令
1. 在搜索框中输入命令名称或关键词
2. 例如：输入"回零"会显示所有与回零相关的命令
3. 搜索结果实时更新

### 发送命令
1. 先连接到 Grbl 设备（在"设备连接"标签页）
2. 在"命令参考"标签页中选择要发送的命令
3. 点击"发送选中命令"按钮
4. 命令将被发送到设备

## 文件修改

### 修改的文件
- `src/linktunnel/unified_gui/modules/grbl_module.py`
  - 添加 GRBL_COMMANDS 数据结构
  - 添加 GrblCommandHelper 类
  - 添加命令参考相关方法
  - 在 _create_pyqt_ui 中添加命令参考标签页

### 新增文件
- `test_grbl_commands.py` - 命令功能测试
- `test_grbl_ui.py` - 模块 UI 测试
- `test_app_with_commands.py` - 应用启动测试

## 测试

### 单元测试
```bash
python test_grbl_commands.py
```

### UI 测试
```bash
python test_grbl_ui.py
```

### 应用启动测试
```bash
python test_app_with_commands.py
```

## 兼容性

- 与现有的 Grbl 模块功能完全兼容
- 不影响其他模块的功能
- 支持 PyQt6 和 tkinter 两种 UI 框架

## 后续改进

可能的改进方向：
1. 添加命令历史记录
2. 添加命令收藏功能
3. 添加命令宏功能
4. 添加命令参数编辑器
5. 添加命令执行日志

## 总结

Grbl 命令参考功能已成功集成到应用程序中，用户现在可以：
- ✓ 查看所有 Grbl 命令
- ✓ 搜索特定命令
- ✓ 查看命令详情
- ✓ 快速发送命令到设备

这个功能大大提高了用户的工作效率，特别是对于不熟悉 Grbl 命令的新用户。
