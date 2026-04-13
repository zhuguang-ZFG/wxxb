# 代理管理模块 (ProxyModule)

## 概述

代理管理模块整合了 `client_app.py` 的功能，提供 Mihomo/Clash 代理管理的图形界面。

## 已实现功能 (Task 13.2)

### 1. 内核版本显示
- 显示 Mihomo 或 Clash 内核版本
- 自动识别版本格式（Meta 或标准 Clash）
- 格式：`Mihomo 1.18.0` 或 `Clash 1.10.0`

### 2. 运行模式管理
- 显示当前运行模式（rule/global/direct）
- 提供模式切换下拉框
- "应用模式" 按钮执行模式切换
- 可选：切换模式时自动关闭所有连接

### 3. 监听信息显示
- 显示监听端口信息
- 格式：`mixed 7890 · http 7891 · socks 7892`
- 自动从 `/configs` API 获取

### 4. 连接数显示
- 实时显示当前活动连接数
- 从 `/connections` API 获取

### 5. API 连接管理
- API 地址和 Secret 配置
- 支持从 profile 的 config.yaml 自动读取
- "复制 API" 按钮快速复制 API 地址
- "连接/刷新" 按钮手动刷新数据

### 6. 自动刷新
- 可选的自动刷新功能
- 可配置刷新间隔（3/5/10/15 秒）
- 自动刷新使用轻量级 API 调用（不包含版本信息）

### 7. 配置持久化
- 自动保存用户配置
- 下次启动时恢复上次的设置
- 包括：API、Secret、自动刷新设置等

## 技术实现

### 架构
- 继承自 `BaseModule` 基类
- 使用 PyQt6 实现 UI（带 tkinter 备选）
- 异步请求避免 UI 冻结
- 队列机制处理后台任务结果

### API 调用
- 复用 `clash.client` 模块的 API 函数
- 并行请求提高响应速度（ThreadPoolExecutor）
- 完整快照：version + configs + proxies + connections
- 轻量快照：configs + proxies + connections（用于自动刷新）

### 数据格式化
- 使用 `client_model.format_listen_line()` 格式化监听端口
- 自定义 `_format_version_line()` 格式化版本信息

## 待实现功能

### Task 13.3 - 策略组和节点管理
- 树形节点列表显示
- 节点筛选功能
- 延迟测试
- 节点切换（双击或应用按钮）
- 关闭全部连接

### Task 13.4 - 浏览器控制台
- 打开 Yacd 或本地 UI
- 调用 `dashboard_open.py`

## 使用方法

```python
from linktunnel.unified_gui.modules.proxy_module import ProxyModule
from linktunnel.unified_gui.core.config_manager import ConfigManager
from linktunnel.unified_gui.core.log_manager import LogManager

config_manager = ConfigManager(config_dir)
log_manager = LogManager()

proxy_module = ProxyModule(config_manager, log_manager)
```

## 配置示例

```json
{
  "proxy": {
    "api": "http://127.0.0.1:9090",
    "secret": "",
    "from_profile": true,
    "auto_refresh": false,
    "auto_refresh_interval": 5
  }
}
```

## 测试

运行测试：
```bash
python -m pytest tests/test_proxy_module.py -v
```

## 依赖

- PyQt6（可选，无则使用 tkinter）
- linktunnel.clash.client
- linktunnel.client_model
- linktunnel.proxy.mihomo_config
