#!/usr/bin/env python3
"""测试 GitHub 热点节点拉取功能"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_hotspot_nodes():
    """测试热点节点拉取"""
    try:
        from linktunnel.proxy.node_manager import ProxyNodeManager
        
        print("✓ ProxyNodeManager 导入成功")
        
        # 创建管理器
        cache_dir = Path.home() / ".linktunnel" / "test_hotspot_nodes"
        manager = ProxyNodeManager(cache_dir=cache_dir)
        print("✓ 节点管理器创建成功")
        
        # 测试搜索热点仓库
        print("\n--- 测试搜索热点仓库 ---")
        print("搜索 proxy 相关的 Python 项目...")
        repos = manager.search_github_hotspot_repos(keyword="proxy", language="python")
        print(f"✓ 找到 {len(repos)} 个热点仓库")
        
        if repos:
            for i, repo in enumerate(repos[:3], 1):
                print(f"  {i}. {repo['full_name']}")
                print(f"     ⭐ {repo['stars']} stars")
                print(f"     📝 {repo['description'][:50]}...")
        
        # 测试从热点仓库拉取节点
        print("\n--- 测试从热点仓库拉取节点 ---")
        print("拉取节点...")
        new_nodes = manager.fetch_from_github_hotspot(keyword="proxy", language="python")
        print(f"✓ 拉取了 {len(new_nodes)} 个新节点")
        
        if new_nodes:
            print(f"  示例节点: {new_nodes[:3]}")
        
        # 测试自动拉取
        print("\n--- 测试自动拉取 ---")
        print("执行自动拉取...")
        result = manager.auto_fetch_hotspot_nodes()
        print(f"✓ 自动拉取完成:")
        print(f"  - 仓库数: {result['repos']}")
        print(f"  - 节点数: {result['nodes']}")
        print(f"  - 时间: {result['timestamp']}")
        
        # 获取所有节点
        print("\n--- 节点统计 ---")
        nodes = manager.get_nodes()
        print(f"✓ 总节点数: {len(nodes)}")
        
        # 按来源统计
        sources = {}
        for name, info in nodes.items():
            source = info.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        print("✓ 按来源统计:")
        for source, count in sources.items():
            print(f"  - {source}: {count} 个")
        
        # 清理测试数据
        print("\n--- 清理测试数据 ---")
        import shutil
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print(f"✓ 已清理测试缓存目录: {cache_dir}")
        
        print("\n✓✓✓ 所有测试通过! ✓✓✓")
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hotspot_nodes()
    sys.exit(0 if success else 1)
