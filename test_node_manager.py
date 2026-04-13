#!/usr/bin/env python3
"""测试代理节点管理器"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_node_manager():
    """测试节点管理器"""
    try:
        from linktunnel.proxy.node_manager import ProxyNodeManager
        
        print("✓ ProxyNodeManager 导入成功")
        
        # 创建管理器
        cache_dir = Path.home() / ".linktunnel" / "test_proxy_nodes"
        manager = ProxyNodeManager(cache_dir=cache_dir)
        print("✓ 节点管理器创建成功")
        
        # 测试添加节点
        print("\n--- 测试添加节点 ---")
        manager.add_node("test1", "https://example.com/sub1")
        manager.add_node("test2", "https://example.com/sub2")
        print("✓ 已添加 2 个测试节点")
        
        # 获取节点
        nodes = manager.get_nodes()
        print(f"✓ 节点总数: {len(nodes)}")
        for name, info in nodes.items():
            print(f"  - {name}: {info['url']} (来源: {info['source']})")
        
        # 测试验证节点
        print("\n--- 测试验证节点 ---")
        print("验证 test1...")
        valid = manager.verify_node("test1", timeout=5)
        print(f"✓ test1 验证结果: {'有效' if valid else '失效'}")
        
        # 获取状态
        status = manager.get_status()
        print(f"✓ 节点状态:")
        for name, st in status.items():
            print(f"  - {name}: {st}")
        
        # 测试获取有效/失效节点
        print("\n--- 测试节点分类 ---")
        valid_nodes = manager.get_valid_nodes()
        invalid_nodes = manager.get_invalid_nodes()
        print(f"✓ 有效节点: {len(valid_nodes)} 个")
        print(f"✓ 失效节点: {len(invalid_nodes)} 个")
        
        # 测试移除节点
        print("\n--- 测试移除节点 ---")
        manager.remove_node("test1")
        print("✓ 已移除 test1")
        
        nodes = manager.get_nodes()
        print(f"✓ 剩余节点数: {len(nodes)}")
        
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
    success = test_node_manager()
    sys.exit(0 if success else 1)
