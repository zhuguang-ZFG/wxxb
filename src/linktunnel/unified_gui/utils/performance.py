"""
性能优化工具
"""

from __future__ import annotations

import gc
import time
from functools import wraps
from typing import Callable, Any


def debounce(wait_ms: int) -> Callable:
    """
    防抖装饰器 - 延迟执行函数，如果在等待期间再次调用则重置计时器
    
    Args:
        wait_ms: 等待时间（毫秒）
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        timer = None
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            
            try:
                from PyQt6.QtCore import QTimer
                
                if timer is not None:
                    timer.stop()
                
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: func(*args, **kwargs))
                timer.start(wait_ms)
            except ImportError:
                # tkinter 版本直接执行
                func(*args, **kwargs)
        
        return wrapper
    return decorator


def throttle(wait_ms: int) -> Callable:
    """
    节流装饰器 - 限制函数执行频率
    
    Args:
        wait_ms: 最小间隔时间（毫秒）
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        last_call_time = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            time_since_last_call = (current_time - last_call_time[0]) * 1000
            
            if time_since_last_call >= wait_ms:
                last_call_time[0] = current_time
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def measure_time(func: Callable) -> Callable:
    """
    测量函数执行时间的装饰器
    
    Args:
        func: 要测量的函数
    
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        
        # 如果执行时间超过 100ms，记录警告
        if elapsed_ms > 100:
            print(f"⚠️ {func.__name__} 执行时间: {elapsed_ms:.2f}ms")
        
        return result
    
    return wrapper


class MemoryOptimizer:
    """内存优化器"""
    
    @staticmethod
    def force_gc() -> None:
        """强制垃圾回收"""
        gc.collect()
    
    @staticmethod
    def get_memory_usage() -> dict[str, Any]:
        """
        获取内存使用情况
        
        Returns:
            包含内存信息的字典
        """
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # 物理内存（MB）
                "vms_mb": memory_info.vms / 1024 / 1024,  # 虚拟内存（MB）
                "percent": process.memory_percent(),  # 内存占用百分比
            }
        except ImportError:
            return {
                "rss_mb": 0,
                "vms_mb": 0,
                "percent": 0,
            }
    
    @staticmethod
    def optimize_memory() -> None:
        """优化内存使用"""
        # 强制垃圾回收
        gc.collect()
        
        # 清理未使用的缓存
        try:
            import sys
            if hasattr(sys, 'intern'):
                # Python 3.x
                pass
        except Exception:
            pass


class CPUOptimizer:
    """CPU 优化器"""
    
    @staticmethod
    def get_cpu_usage() -> float:
        """
        获取 CPU 使用率
        
        Returns:
            CPU 使用率百分比
        """
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            return process.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0
    
    @staticmethod
    def is_high_cpu_usage(threshold: float = 50.0) -> bool:
        """
        检查是否 CPU 使用率过高
        
        Args:
            threshold: CPU 使用率阈值（百分比）
        
        Returns:
            是否超过阈值
        """
        return CPUOptimizer.get_cpu_usage() > threshold


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self._start_time = time.perf_counter()
        self._checkpoints = {}
    
    def checkpoint(self, name: str) -> None:
        """
        记录检查点
        
        Args:
            name: 检查点名称
        """
        elapsed = (time.perf_counter() - self._start_time) * 1000
        self._checkpoints[name] = elapsed
    
    def get_report(self) -> str:
        """
        获取性能报告
        
        Returns:
            性能报告字符串
        """
        if not self._checkpoints:
            return "无性能数据"
        
        lines = ["性能报告:"]
        prev_time = 0.0
        
        for name, elapsed in self._checkpoints.items():
            delta = elapsed - prev_time
            lines.append(f"  {name}: {elapsed:.2f}ms (+{delta:.2f}ms)")
            prev_time = elapsed
        
        return "\n".join(lines)
    
    def reset(self) -> None:
        """重置监控器"""
        self._start_time = time.perf_counter()
        self._checkpoints.clear()


def lazy_import(module_name: str, attribute: str = None):
    """
    延迟导入模块
    
    Args:
        module_name: 模块名称
        attribute: 属性名称（可选）
    
    Returns:
        导入的模块或属性
    """
    import importlib
    
    module = importlib.import_module(module_name)
    
    if attribute:
        return getattr(module, attribute)
    
    return module
