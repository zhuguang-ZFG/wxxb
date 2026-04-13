#!/usr/bin/env python3
"""演示 GitHub 热点节点自动拉取功能"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_hotspot_nodes():
    """演示热点节点拉取"""
    try:
        from linktunnel.proxy.node_manager import ProxyNodeManager
        
        print("=" * 70)
        print("GitHub 热点节点自动拉取功能演示")
        print("=" * 70)
        
        # 创建管理器
        cache_dir = Path.home() / ".linktunnel" / "demo_hotspot"
        manager = ProxyNodeManager(cache_dir=cache_dir)
        print("\n✓ 节点管理器初始化完成")
        
        # 演示 1: 搜索热点仓库
        print("\n" + "=" * 70)
        print("演示 1: 搜索 GitHub 热点代理仓库")
        print("=" * 70)
        print("\n搜索条件:")
        print("  - 关键词: proxy")
        print("  - 语言: python")
        print("  - 星标数: > 100")
        print("  - 排序: 按星标数降序")
        print("\n正在搜索...")
        
        repos = manager.search_github_hotspot_repos(keyword="proxy", language="python")
        
        print(f"\n✓ 搜索完成! 找到 {len(repos)} 个热点仓库\n")
        
        if repos:
            print("热点仓库列表 (前 5 个):")
            print("-" * 70)
            for i, repo in enumerate(repos[:5], 1):
                print(f"\n{i}. {repo['full_name']}")
                print(f"   ⭐ 星标数: {repo['stars']}")
                print(f"   🔗 URL: {repo['url']}")
                print(f"   📝 描述: {repo['description'][:60]}..." if repo['description'] else "   📝 描述: 无")
        
        # 演示 2: 从热点仓库拉取节点
        print("\n" + "=" * 70)
        print("演示 2: 从热点仓库自动拉取节点")
        print("=" * 70)
        print("\n拉取策略:")
        print("  - 遍历每个热点仓库")
        print("  - 尝试多个常见文件名 (nodes.txt, nodes.json, README.md 等)")
        print("  - 自动解析节点列表")
        print("  - 自动去重")
        print("\n正在拉取...")
        
        new_nodes = manager.fetch_from_github_hotspot(keyword="proxy", language="python")
        
        print(f"\n✓ 拉取完成! 获得 {len(new_nodes)} 个新节点\n")
        
        if new_nodes:
            print("拉取的节点示例 (前 10 个):")
            print("-" * 70)
            for i, node in enumerate(new_nodes[:10], 1):
                print(f"{i:2d}. {node}")
        
        # 演示 3: 节点统计
        print("\n" + "=" * 70)
        print("演示 3: 节点统计和分析")
        print("=" * 70)
        
        nodes = manager.get_nodes()
        status = manager.get_status()
        
        print(f"\n总节点数: {len(nodes)}")
        
        # 按来源统计
        sources = {}
        for name, info in nodes.items():
            source = info.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        print("\n按来源统计:")
        print("-" * 70)
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source:20s}: {count:3d} 个")
        
        # 节点状态统计
        valid_count = sum(1 for s in status.values() if s.get("valid") is True)
        invalid_count = sum(1 for s in status.values() if s.get("valid") is False)
        unchecked_count = sum(1 for s in status.values() if s.get("valid") is None)
        
        print("\n节点状态统计:")
        print("-" * 70)
        print(f"  ✓ 有效节点:   {valid_count:3d} 个")
        print(f"  ✗ 失效节点:   {invalid_count:3d} 个")
        print(f"  ? 未检查:     {unchecked_count:3d} 个")
        
        # 演示 4: 自动拉取
        print("\n" + "=" * 70)
        print("演示 4: 自动拉取热点节点")
        print("=" * 70)
        print("\n自动拉取流程:")
        print("  1. 搜索 GitHub 热点仓库")
        print("  2. 从每个仓库拉取节点")
        print("  3. 验证所有节点")
        print("  4. 清除失效节点")
        print("  5. 记录日志")
        print("\n执行自动拉取...")
        
        result = manager.auto_fetch_hotspot_nodes()
        
        print(f"\n✓ 自动拉取完成!")
        print(f"  - 搜索到的仓库数: {result['repos']}")
        print(f"  - 拉取的新节点数: {result['nodes']}")
        print(f"  - 拉取时间: {result['timestamp']}")
        
        # 演示 5: 验证节点
        print("\n" + "=" * 70)
        print("演示 5: 验证节点有效性")
        print("=" * 70)
        print("\n验证策略:")
        print("  - 并行验证所有节点")
        print("  - 超时时间: 10 秒")
        print("  - 检查 HTTP 状态码")
        print("\n正在验证前 5 个节点...")
        
        nodes_list = list(nodes.keys())[:5]
        for node_name in nodes_list:
            print(f"\n验证节点: {node_name}")
            valid = manager.verify_node(node_name, timeout=5)
            status_text = "✓ 有效" if valid else "✗ 失效"
            print(f"  结果: {status_text}")
        
        # 演示 6: 清理失效节点
        print("\n" + "=" * 70)
        print("演示 6: 清理失效节点")
        print("=" * 70)
        print("\n清理策略:")
        print("  - 清除 7 天以上失效的节点")
        print("  - 保留最近失效的节点")
        print("  - 自动记录日志")
        
        removed = manager.cleanup_invalid_nodes()
        print(f"\n✓ 清理完成! 清除了 {len(removed)} 个失效节点")
        
        if removed:
            print("\n清除的节点:")
            for node in removed[:5]:
                print(f"  - {node}")
        
        # 最终统计
        print("\n" + "=" * 70)
        print("最终统计")
        print("=" * 70)
        
        final_nodes = manager.get_nodes()
        final_status = manager.get_status()
        
        final_valid = sum(1 for s in final_status.values() if s.get("valid") is True)
        final_invalid = sum(1 for s in final_status.values() if s.get("valid") is False)
        
        print(f"\n总节点数: {len(final_nodes)}")
        print(f"有效节点: {final_valid}")
        print(f"失效节点: {final_invalid}")
        
        # 清理演示数据
        print("\n" + "=" * 70)
        print("清理演示数据")
        print("=" * 70)
        
        import shutil
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print(f"\n✓ 已清理演示缓存: {cache_dir}")
        
        print("\n" + "=" * 70)
        print("✓✓✓ 演示完成! ✓✓✓")
        print("=" * 70)
        print("\n功能总结:")
        print("  ✓ 自动搜索 GitHub 热点仓库")
        print("  ✓ 智能拉取代理节点")
        print("  ✓ 自动验证节点有效性")
        print("  ✓ 定期清除失效节点")
        print("  ✓ 完整的日志记录")
        print("\n这个功能可以:")
        print("  • 自动获取最新的代理节点")
        print("  • 验证节点的可用性")
        print("  • 定期更新和清理")
        print("  • 提高系统的可靠性")
        print("\n" + "=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_hotspot_nodes()
    sys.exit(0 if success else 1)
