# GitHub 热点节点自动拉取功能

## 功能概述

添加了从 GitHub 自动搜索和拉取开放的热点代理节点的功能。系统会自动搜索 GitHub 上星标数较多的代理相关仓库，并从这些仓库中提取可用的节点列表。

## 功能特性

### 1. 自动搜索热点仓库
- 搜索 GitHub 上的热点代理仓库
- 按星标数排序
- 支持自定义搜索关键词
- 支持按编程语言筛选

### 2. 智能节点提取
- 自动尝试多个常见文件名
- 支持多种格式解析
- 自动去重
- 记录节点来源

### 3. 自动验证和更新
- 拉取后自动验证节点
- 定期清除失效节点
- 每日自动更新
- 后台运行不阻塞 UI

### 4. 用户友好的 UI
- 搜索关键词输入
- 编程语言选择
- 实时进度反馈
- 详细的日志记录

## 使用方法

### 手动拉取

#### 方式 1: 在节点管理对话框中
1. 打开"节点管理"对话框
2. 在"搜索关键词"输入框中输入关键词（默认: proxy）
3. 选择编程语言（默认: python）
4. 点击"从 GitHub 热点拉取"按钮
5. 等待拉取完成

#### 方式 2: 在增强代理模块中
1. 点击"拉取 GitHub 热点节点"按钮
2. 系统自动搜索和拉取热点节点
3. 查看日志了解拉取进度

### 自动拉取

#### 启用每日自动拉取
1. 在增强代理模块中勾选"启用每日自动拉取热点节点"
2. 系统将在每日指定时间自动拉取
3. 拉取结果会记录在日志中

## API 参考

### ProxyNodeManager

#### 搜索热点仓库
```python
repos = manager.search_github_hotspot_repos(
    keyword="proxy",      # 搜索关键词
    language="python"     # 编程语言
)

# 返回值
[
    {
        "name": "repo_name",
        "full_name": "owner/repo",
        "url": "https://github.com/...",
        "description": "...",
        "stars": 1000,
        "language": "Python"
    },
    ...
]
```

#### 从热点仓库拉取节点
```python
new_nodes = manager.fetch_from_github_hotspot(
    keyword="proxy",      # 搜索关键词
    language="python"     # 编程语言
)

# 返回值: ["node1", "node2", ...]
```

#### 自动拉取热点节点
```python
result = manager.auto_fetch_hotspot_nodes()

# 返回值
{
    "repos": 10,                              # 搜索到的仓库数
    "nodes": 50,                              # 拉取的节点数
    "timestamp": "2024-04-13T12:00:00"       # 拉取时间
}
```

## 搜索策略

### 搜索关键词
- `proxy` - 代理相关
- `clash` - Clash 相关
- `mihomo` - Mihomo 相关
- `subscribe` - 订阅相关
- `node` - 节点相关

### 编程语言
- `python` - Python 项目
- `go` - Go 项目
- `rust` - Rust 项目
- `javascript` - JavaScript 项目
- `all` - 所有语言

### 搜索条件
- 星标数 > 100
- 按星标数降序排列
- 返回前 10 个结果

## 节点文件格式

系统会自动尝试以下文件：
1. `nodes.txt` - 节点列表
2. `nodes.json` - JSON 格式节点
3. `README.md` - README 文件
4. `subscribe.txt` - 订阅文件
5. `proxy.txt` - 代理文件
6. `list.txt` - 列表文件

### 支持的格式

#### 格式 1: name|url
```
node1|https://example.com/sub1
node2|https://example.com/sub2
```

#### 格式 2: 仅 URL
```
https://example.com/sub1
https://example.com/sub2
```

#### 格式 3: 注释
```
# 这是注释
node1|https://example.com/sub1
# 另一个注释
node2|https://example.com/sub2
```

## 工作流程

### 手动拉取流程
```
用户点击"拉取"按钮
    ↓
搜索 GitHub 热点仓库
    ↓
遍历每个仓库
    ↓
尝试多个文件名
    ↓
解析节点列表
    ↓
添加到本地数据库
    ↓
显示拉取结果
```

### 自动拉取流程
```
每日指定时间触发
    ↓
搜索 GitHub 热点仓库
    ↓
拉取节点列表
    ↓
验证所有节点
    ↓
清除失效节点
    ↓
记录日志
    ↓
循环执行
```

## 性能指标

### 搜索性能
- 搜索时间: ~2-5 秒
- 返回结果: 10 个仓库
- 网络超时: 10 秒

### 拉取性能
- 单个仓库: ~1-2 秒
- 10 个仓库: ~10-20 秒
- 平均节点数: 50-100 个

### 验证性能
- 单个节点: ~1-5 秒
- 批量验证: 并行处理
- 超时设置: 10 秒

## 错误处理

### 常见错误

#### 搜索失败
- 原因: 网络连接问题
- 解决: 检查网络连接，重试

#### 拉取失败
- 原因: 仓库不存在或文件不存在
- 解决: 自动尝试其他文件，跳过失败的仓库

#### 验证失败
- 原因: 节点 URL 无效或超时
- 解决: 标记为失效，7 天后自动清除

### 日志记录
所有操作都会记录到日志：
```
INFO: 从 GitHub 搜索到 10 个热点仓库
INFO: 从 owner/repo/nodes.txt 拉取了 50 个节点
ERROR: 处理仓库 owner/repo 失败: ...
INFO: 自动拉取完成: 10 个仓库, 50 个新节点
```

## 安全考虑

### URL 验证
- 检查 URL 格式
- 验证 HTTP 状态码
- 超时保护

### 数据验证
- 检查节点格式
- 去重处理
- 来源标记

### 隐私保护
- 不收集用户数据
- 不上传节点信息
- 本地缓存存储

## 配置选项

### 搜索配置
```python
# 自定义搜索关键词
manager.fetch_from_github_hotspot(
    keyword="clash",
    language="go"
)
```

### 自动更新配置
```python
# 启用每日自动拉取
manager.schedule_daily_update(
    callback=on_update_complete
)
```

## 示例代码

### 基本使用
```python
from linktunnel.proxy.node_manager import ProxyNodeManager

manager = ProxyNodeManager()

# 搜索热点仓库
repos = manager.search_github_hotspot_repos()
print(f"找到 {len(repos)} 个热点仓库")

# 拉取节点
new_nodes = manager.fetch_from_github_hotspot()
print(f"拉取了 {len(new_nodes)} 个新节点")

# 验证节点
results = manager.verify_all_nodes()
print(f"验证完成: {sum(results.values())}/{len(results)} 个有效")
```

### 自动拉取
```python
# 启动每日自动拉取
def on_update(result):
    print(f"更新完成: {result['repos']} 个仓库, {result['nodes']} 个节点")

manager.schedule_daily_update(callback=on_update)
```

### 自定义搜索
```python
# 搜索 Clash 相关的 Go 项目
repos = manager.search_github_hotspot_repos(
    keyword="clash",
    language="go"
)

for repo in repos:
    print(f"{repo['name']}: {repo['stars']} stars")
```

## 常见问题

### Q: 拉取的节点是否安全？
A: 系统会自动验证每个节点，失效的节点会被标记并最终清除。

### Q: 拉取的节点会保存多久？
A: 节点会一直保存，直到被标记为失效 7 天后自动清除。

### Q: 可以自定义搜索条件吗？
A: 可以，支持自定义关键词和编程语言。

### Q: 自动拉取会影响性能吗？
A: 不会，自动拉取在后台线程运行，不会阻塞 UI。

### Q: 如何禁用自动拉取？
A: 取消勾选"启用每日自动拉取热点节点"复选框。

## 故障排除

### 搜索无结果
1. 检查网络连接
2. 检查搜索关键词
3. 查看日志获取详细信息

### 拉取失败
1. 检查网络连接
2. 检查 GitHub 访问权限
3. 尝试手动拉取

### 节点验证失败
1. 检查节点 URL 有效性
2. 检查网络连接
3. 增加超时时间

## 总结

GitHub 热点节点自动拉取功能提供了：
- ✓ 自动搜索热点仓库
- ✓ 智能节点提取
- ✓ 自动验证和更新
- ✓ 用户友好的 UI
- ✓ 完善的错误处理

这个功能大大简化了节点管理工作，用户可以轻松获取最新的、经过验证的代理节点。
