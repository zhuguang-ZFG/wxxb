# 代理节点管理功能

## 概述

添加了完整的代理节点管理系统，支持：
- 节点验证和健康检查
- 从 GitHub 自动拉取节点
- 从订阅 URL 拉取节点
- 每日自动更新和清理
- 失效节点自动清除

## 功能特性

### 1. 节点验证
- **单个验证**: 验证单个节点的可用性
- **批量验证**: 并行验证所有节点
- **超时控制**: 可配置的验证超时时间
- **状态跟踪**: 记录每个节点的验证状态和时间

### 2. 节点来源
- **手动添加**: 直接添加节点 URL
- **GitHub 拉取**: 从 GitHub 仓库拉取节点列表
- **订阅 URL**: 从订阅 URL 拉取节点
- **来源标记**: 每个节点记录其来源

### 3. 自动更新
- **每日更新**: 每天凌晨 2 点自动更新
- **验证所有节点**: 自动验证所有节点的可用性
- **清除失效**: 自动清除 7 天以上失效的节点
- **后台运行**: 不阻塞主线程

### 4. 缓存管理
- **本地缓存**: 节点数据保存在 `~/.linktunnel/proxy_nodes/`
- **持久化**: 节点信息和状态持久化存储
- **快速加载**: 启动时快速加载缓存数据

## 使用方法

### 基本使用

#### 1. 添加节点
```python
from linktunnel.proxy.node_manager import ProxyNodeManager

manager = ProxyNodeManager()

# 手动添加节点
manager.add_node("my_node", "https://example.com/subscribe")
```

#### 2. 验证节点
```python
# 验证单个节点
valid = manager.verify_node("my_node")

# 验证所有节点
results = manager.verify_all_nodes()
```

#### 3. 从 GitHub 拉取
```python
# 从 GitHub 仓库拉取节点
new_nodes = manager.fetch_from_github("user/proxy-nodes")
```

#### 4. 从订阅拉取
```python
# 从订阅 URL 拉取节点
new_nodes = manager.fetch_from_subscription("https://example.com/subscribe")
```

#### 5. 清除失效节点
```python
# 清除 7 天以上失效的节点
removed = manager.cleanup_invalid_nodes()
```

### UI 使用

#### 节点管理对话框
1. 打开"节点管理"对话框
2. 添加、验证、删除节点
3. 从 GitHub 或订阅 URL 拉取节点

#### 自动更新
1. 启用"每日自动更新"复选框
2. 选择更新时间
3. 系统将在指定时间自动更新和验证节点

## 文件结构

### 新增文件
- `src/linktunnel/proxy/node_manager.py` - 节点管理器核心模块
- `src/linktunnel/unified_gui/modules/proxy_module_enhanced.py` - 增强的代理模块 UI

### 缓存目录
```
~/.linktunnel/proxy_nodes/
├── nodes.json      # 节点信息
└── status.json     # 节点状态
```

## API 参考

### ProxyNodeManager

#### 初始化
```python
manager = ProxyNodeManager(cache_dir=None)
```

#### 节点管理
```python
# 添加节点
manager.add_node(name, url, source="manual")

# 移除节点
manager.remove_node(name)

# 获取所有节点
nodes = manager.get_nodes()

# 获取有效节点
valid = manager.get_valid_nodes()

# 获取失效节点
invalid = manager.get_invalid_nodes()
```

#### 验证
```python
# 验证单个节点
valid = manager.verify_node(name, timeout=10.0)

# 验证所有节点
results = manager.verify_all_nodes(timeout=10.0)
```

#### 拉取
```python
# 从 GitHub 拉取
new_nodes = manager.fetch_from_github(repo, file_path="nodes.txt")

# 从订阅拉取
new_nodes = manager.fetch_from_subscription(url)
```

#### 清理
```python
# 清除失效节点
removed = manager.cleanup_invalid_nodes()
```

#### 自动更新
```python
# 启动每日更新任务
manager.schedule_daily_update(callback=None)
```

## 配置示例

### GitHub 仓库格式
节点列表文件 (nodes.txt):
```
node1|https://example.com/sub1
node2|https://example.com/sub2
https://example.com/sub3
```

### 订阅 URL 格式
```
node1|https://example.com/sub1
node2|https://example.com/sub2
https://example.com/sub3
```

## 验证流程

1. **URL 验证**: 检查 URL 格式是否有效
2. **连接测试**: 尝试连接到 URL
3. **状态检查**: 检查 HTTP 状态码
4. **结果记录**: 记录验证结果和时间

## 自动更新流程

1. **计算下次更新时间**: 每天凌晨 2 点
2. **等待**: 直到下次更新时间
3. **验证所有节点**: 并行验证所有节点
4. **清除失效**: 清除 7 天以上失效的节点
5. **回调通知**: 调用回调函数通知更新完成
6. **重复**: 循环执行

## 错误处理

- **网络错误**: 记录错误信息，标记节点为失效
- **超时**: 节点验证超时时标记为失效
- **无效 URL**: 拒绝添加无效 URL 的节点
- **缓存错误**: 自动恢复，使用空缓存

## 性能优化

- **并行验证**: 使用线程池并行验证多个节点
- **缓存**: 本地缓存节点数据，减少网络请求
- **防抖**: UI 搜索和筛选使用防抖
- **后台任务**: 自动更新在后台线程运行

## 安全考虑

- **超时保护**: 所有网络请求都有超时限制
- **异常处理**: 完善的异常处理机制
- **线程安全**: 使用锁保护共享数据
- **验证**: 验证 URL 格式和 HTTP 状态码

## 日志

所有操作都会记录到日志：
```
logger.info("已添加节点: node_name")
logger.error("节点验证失败: error_message")
logger.info("从 GitHub 拉取了 N 个新节点")
```

## 示例代码

### 完整示例
```python
from linktunnel.proxy.node_manager import ProxyNodeManager

# 创建管理器
manager = ProxyNodeManager()

# 添加节点
manager.add_node("test", "https://example.com/sub")

# 验证节点
valid = manager.verify_node("test")
print(f"节点有效: {valid}")

# 从 GitHub 拉取
new_nodes = manager.fetch_from_github("user/proxy-nodes")
print(f"拉取了 {len(new_nodes)} 个新节点")

# 验证所有节点
results = manager.verify_all_nodes()
print(f"验证结果: {results}")

# 获取有效节点
valid_nodes = manager.get_valid_nodes()
print(f"有效节点: {valid_nodes}")

# 启动每日更新
def on_update(result):
    print(f"更新完成: {result}")

manager.schedule_daily_update(callback=on_update)
```

## 故障排除

### 节点验证失败
- 检查网络连接
- 检查 URL 是否正确
- 检查超时时间是否过短
- 查看日志获取详细错误信息

### 自动更新不工作
- 检查是否启用了自动更新
- 检查系统时间是否正确
- 查看日志获取详细错误信息

### 缓存问题
- 删除 `~/.linktunnel/proxy_nodes/` 目录
- 重新启动应用
- 重新添加节点

## 总结

代理节点管理功能提供了完整的节点管理解决方案，包括：
- ✓ 节点验证和健康检查
- ✓ 自动拉取和更新
- ✓ 失效节点自动清除
- ✓ 每日自动更新
- ✓ 本地缓存和持久化

这个功能大大简化了代理节点的管理工作，提高了系统的可靠性。
