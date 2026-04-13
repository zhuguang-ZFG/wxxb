# 快速参考指南

## 项目结构

```
linktunnel/
├── src/
│   └── linktunnel/
│       ├── unified_gui/
│       │   ├── core/           # 核心模块
│       │   ├── modules/        # 功能模块
│       │   └── ui/             # UI 组件
│       ├── proxy/              # 代理管理
│       ├── grbl/               # Grbl 控制
│       └── ...
├── tests/                       # 测试文件
├── docs/                        # 文档
└── README.md
```

## 快速启动

### 安装
```bash
pip install -e .
```

### 运行应用
```bash
python -m linktunnel.unified_gui
```

### 运行测试
```bash
pytest tests/
```

## 主要功能

### 1. Grbl CNC 控制
- **位置**: `src/linktunnel/unified_gui/modules/grbl_module.py`
- **功能**: 设备连接、状态监控、G代码传输、手动控制、命令参考
- **命令**: 75+ 个 Grbl 命令

### 2. 代理管理
- **位置**: `src/linktunnel/unified_gui/modules/proxy_module.py`
- **功能**: API 连接、模式切换、节点管理、延迟测试
- **增强**: `proxy_module_enhanced.py` - 节点自动验证和更新

### 3. 节点管理
- **位置**: `src/linktunnel/proxy/node_manager.py`
- **功能**: 节点验证、GitHub 拉取、订阅拉取、自动更新
- **缓存**: `~/.linktunnel/proxy_nodes/`

### 4. 其他模块
- **串口工具**: 串口通信
- **网络中继**: 网络代理
- **BLE 扫描**: 蓝牙设备扫描
- **I2C 扫描**: I2C 设备扫描

## 常用命令

### Grbl 命令
```
$H      - 回零
$X      - 解锁
$       - 查看设置
?       - 查询状态
!       - 暂停
~       - 恢复
^X      - 软复位
```

### 代理模式
```
rule    - 规则模式
global  - 全局模式
direct  - 直连模式
```

## 配置文件

### 应用配置
- **位置**: `~/.linktunnel/config.json`
- **内容**: 主题、窗口大小、模块配置

### 代理配置
- **位置**: `~/.linktunnel/proxy_nodes/`
- **文件**: `nodes.json`, `status.json`

### Grbl 配置
- **位置**: 设备配置
- **参数**: $0-$132

## 常见问题

### Q: 应用启动失败
A: 检查 Python 版本 (3.14+) 和依赖包

### Q: 模块加载失败
A: 查看日志文件，检查模块配置

### Q: 节点验证失败
A: 检查网络连接和 URL 有效性

### Q: Grbl 连接失败
A: 检查串口设置和设备连接

## 文件清单

### 核心文件
- `src/linktunnel/unified_gui/core/fixed_main_window.py` - 主窗口
- `src/linktunnel/unified_gui/core/base_module.py` - 模块基类
- `src/linktunnel/unified_gui/core/config_manager.py` - 配置管理
- `src/linktunnel/unified_gui/core/log_manager.py` - 日志管理

### 模块文件
- `src/linktunnel/unified_gui/modules/grbl_module.py` - Grbl 模块
- `src/linktunnel/unified_gui/modules/proxy_module.py` - 代理模块
- `src/linktunnel/unified_gui/modules/serial_module.py` - 串口模块
- `src/linktunnel/unified_gui/modules/network_module.py` - 网络模块
- `src/linktunnel/unified_gui/modules/ble_module.py` - BLE 模块
- `src/linktunnel/unified_gui/modules/i2c_module.py` - I2C 模块

### 工具文件
- `src/linktunnel/proxy/node_manager.py` - 节点管理器
- `src/linktunnel/proxy/mihomo_config.py` - 代理配置
- `src/linktunnel/grbl/client.py` - Grbl 客户端
- `src/linktunnel/grbl/protocol.py` - Grbl 协议

### 文档文件
- `README.md` - 项目概览
- `GETTING_STARTED.md` - 快速开始
- `INSTALLATION_GUIDE.md` - 安装指南
- `USER_MANUAL.md` - 用户手册
- `API_REFERENCE.md` - API 参考
- `ARCHITECTURE.md` - 架构设计

## 开发指南

### 添加新模块
1. 继承 `BaseModule` 类
2. 实现必要的方法
3. 在 `fixed_main_window.py` 中注册
4. 添加测试文件

### 修改 UI
1. 编辑相应的模块文件
2. 使用 PyQt6 组件
3. 遵循现有的样式规范
4. 测试 UI 显示

### 添加新功能
1. 创建新的类或方法
2. 添加完整的文档字符串
3. 添加类型注解
4. 添加测试用例

## 性能优化

### 启动优化
- 延迟加载模块
- 缓存配置数据
- 异步初始化

### 运行优化
- 使用线程池
- 缓存网络请求
- 防抖 UI 更新

### 内存优化
- 及时释放资源
- 使用生成器
- 清理缓存

## 调试技巧

### 启用调试日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 查看日志文件
```bash
tail -f ~/.linktunnel/logs/app.log
```

### 运行单个测试
```bash
pytest tests/test_grbl_module.py -v
```

### 性能分析
```bash
python -m cProfile -s cumtime app.py
```

## 快捷键

### 应用快捷键
- `F5` - 刷新代理信息
- `Ctrl+Q` - 退出应用
- `Ctrl+,` - 打开设置

### 模块快捷键
- `Ctrl+H` - Grbl 回零
- `Ctrl+X` - Grbl 解锁
- `Ctrl+?` - 查询状态

## 资源链接

### 官方文档
- [Python 官方文档](https://docs.python.org/)
- [PyQt6 文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Grbl 文档](https://github.com/gnea/grbl/wiki)

### 相关项目
- [Grbl](https://github.com/gnea/grbl)
- [Mihomo](https://github.com/MetaCubeX/mihomo)
- [Clash](https://github.com/Dreamacro/clash)

## 联系方式

### 报告问题
- GitHub Issues
- 邮件支持
- 社区论坛

### 获取帮助
- 查看文档
- 搜索 FAQ
- 联系开发者

## 版本信息

- **当前版本**: 1.0.0 (即将发布)
- **Python 版本**: 3.14+
- **PyQt6 版本**: 6.11+
- **发布日期**: 2024-04-13

## 许可证

MIT License - 详见 LICENSE 文件

---

**最后更新**: 2024-04-13  
**维护者**: linktunnel 开发团队
