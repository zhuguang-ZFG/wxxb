#!/usr/bin/env python
"""简单的性能测试脚本"""

import sys
sys.path.insert(0, 'src')

from linktunnel.unified_gui.utils.performance import (
    MemoryOptimizer,
    CPUOptimizer,
    PerformanceMonitor,
)

print("=" * 60)
print("性能优化模块测试")
print("=" * 60)

# 测试内存优化器
print("\n1. 测试内存优化器")
print("-" * 60)
memory_info = MemoryOptimizer.get_memory_usage()
print(f"内存使用: {memory_info['rss_mb']:.1f} MB")
print(f"虚拟内存: {memory_info['vms_mb']:.1f} MB")
print(f"内存占用: {memory_info['percent']:.1f}%")

print("\n执行垃圾回收...")
MemoryOptimizer.force_gc()
print("✓ 垃圾回收完成")

print("\n执行内存优化...")
MemoryOptimizer.optimize_memory()
print("✓ 内存优化完成")

# 测试 CPU 优化器
print("\n2. 测试 CPU 优化器")
print("-" * 60)
cpu_usage = CPUOptimizer.get_cpu_usage()
print(f"CPU 使用率: {cpu_usage:.1f}%")

is_high = CPUOptimizer.is_high_cpu_usage(threshold=50.0)
print(f"CPU 使用率是否过高 (>50%): {is_high}")

# 测试性能监控器
print("\n3. 测试性能监控器")
print("-" * 60)
monitor = PerformanceMonitor()

monitor.checkpoint("开始")

# 模拟一些工作
import time
time.sleep(0.05)
monitor.checkpoint("工作 1")

time.sleep(0.03)
monitor.checkpoint("工作 2")

time.sleep(0.02)
monitor.checkpoint("结束")

print(monitor.get_report())

print("\n" + "=" * 60)
print("✓ 所有测试通过！")
print("=" * 60)
