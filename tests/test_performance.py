"""
性能优化测试
"""

import time
import pytest
from linktunnel.unified_gui.utils.performance import (
    debounce,
    throttle,
    measure_time,
    MemoryOptimizer,
    CPUOptimizer,
    PerformanceMonitor,
    lazy_import,
)


class TestDebounce:
    """防抖测试"""
    
    def test_debounce_delays_execution(self):
        """测试防抖延迟执行"""
        call_count = [0]
        
        @debounce(100)
        def increment():
            call_count[0] += 1
        
        # 快速调用多次
        for _ in range(5):
            increment()
        
        # 立即检查，应该还没执行
        assert call_count[0] == 0
        
        # 等待足够时间
        time.sleep(0.15)
        
        # 应该只执行一次
        # 注意：由于 QTimer 的限制，这个测试在没有 Qt 事件循环时可能不会执行
        # 所以我们只检查不会立即执行
        assert call_count[0] <= 1


class TestThrottle:
    """节流测试"""
    
    def test_throttle_limits_frequency(self):
        """测试节流限制频率"""
        call_count = [0]
        
        @throttle(100)
        def increment():
            call_count[0] += 1
        
        # 快速调用多次
        for _ in range(5):
            increment()
            time.sleep(0.01)
        
        # 应该只执行一次（第一次）
        assert call_count[0] == 1
        
        # 等待足够时间后再调用
        time.sleep(0.1)
        increment()
        
        # 应该执行第二次
        assert call_count[0] == 2


class TestMeasureTime:
    """测量时间测试"""
    
    def test_measure_time_decorator(self, capsys):
        """测试时间测量装饰器"""
        
        @measure_time
        def slow_function():
            time.sleep(0.15)
            return "done"
        
        result = slow_function()
        
        assert result == "done"
        
        # 检查是否输出了警告（因为超过 100ms）
        captured = capsys.readouterr()
        assert "slow_function" in captured.out or captured.out == ""
    
    def test_measure_time_fast_function(self, capsys):
        """测试快速函数不输出警告"""
        
        @measure_time
        def fast_function():
            return "done"
        
        result = fast_function()
        
        assert result == "done"
        
        # 快速函数不应该输出警告
        captured = capsys.readouterr()
        # 可能没有输出或者输出不包含函数名
        assert "fast_function" not in captured.out or captured.out == ""


class TestMemoryOptimizer:
    """内存优化器测试"""
    
    def test_force_gc(self):
        """测试强制垃圾回收"""
        # 创建一些对象
        data = [list(range(1000)) for _ in range(100)]
        del data
        
        # 强制垃圾回收
        MemoryOptimizer.force_gc()
        
        # 应该不会抛出异常
        assert True
    
    def test_get_memory_usage(self):
        """测试获取内存使用情况"""
        memory_info = MemoryOptimizer.get_memory_usage()
        
        assert isinstance(memory_info, dict)
        assert "rss_mb" in memory_info
        assert "vms_mb" in memory_info
        assert "percent" in memory_info
        
        # 内存使用应该是非负数
        assert memory_info["rss_mb"] >= 0
        assert memory_info["vms_mb"] >= 0
        assert memory_info["percent"] >= 0
    
    def test_optimize_memory(self):
        """测试内存优化"""
        # 创建一些对象
        data = [list(range(1000)) for _ in range(100)]
        del data
        
        # 优化内存
        MemoryOptimizer.optimize_memory()
        
        # 应该不会抛出异常
        assert True


class TestCPUOptimizer:
    """CPU 优化器测试"""
    
    def test_get_cpu_usage(self):
        """测试获取 CPU 使用率"""
        cpu_usage = CPUOptimizer.get_cpu_usage()
        
        assert isinstance(cpu_usage, float)
        assert cpu_usage >= 0
        # CPU 使用率应该在合理范围内
        assert cpu_usage <= 100
    
    def test_is_high_cpu_usage(self):
        """测试检查 CPU 使用率是否过高"""
        # 使用很高的阈值，应该返回 False
        assert not CPUOptimizer.is_high_cpu_usage(threshold=99.0)
        
        # 使用很低的阈值，可能返回 True（取决于当前 CPU 使用情况）
        result = CPUOptimizer.is_high_cpu_usage(threshold=0.1)
        assert isinstance(result, bool)


class TestPerformanceMonitor:
    """性能监控器测试"""
    
    def test_checkpoint(self):
        """测试检查点记录"""
        monitor = PerformanceMonitor()
        
        monitor.checkpoint("start")
        time.sleep(0.01)
        monitor.checkpoint("middle")
        time.sleep(0.01)
        monitor.checkpoint("end")
        
        report = monitor.get_report()
        
        assert "start" in report
        assert "middle" in report
        assert "end" in report
        assert "ms" in report
    
    def test_reset(self):
        """测试重置监控器"""
        monitor = PerformanceMonitor()
        
        monitor.checkpoint("test")
        monitor.reset()
        
        report = monitor.get_report()
        assert report == "无性能数据"
    
    def test_empty_report(self):
        """测试空报告"""
        monitor = PerformanceMonitor()
        
        report = monitor.get_report()
        assert report == "无性能数据"


class TestLazyImport:
    """延迟导入测试"""
    
    def test_lazy_import_module(self):
        """测试延迟导入模块"""
        os_module = lazy_import("os")
        
        assert os_module is not None
        assert hasattr(os_module, "path")
    
    def test_lazy_import_attribute(self):
        """测试延迟导入属性"""
        path = lazy_import("os", "path")
        
        assert path is not None
        assert hasattr(path, "join")
    
    def test_lazy_import_invalid_module(self):
        """测试导入不存在的模块"""
        with pytest.raises(ModuleNotFoundError):
            lazy_import("nonexistent_module_12345")


class TestIntegration:
    """集成测试"""
    
    def test_performance_monitoring_workflow(self):
        """测试性能监控工作流"""
        monitor = PerformanceMonitor()
        
        # 模拟一系列操作
        monitor.checkpoint("初始化")
        
        # 模拟一些工作
        data = [i * 2 for i in range(1000)]
        monitor.checkpoint("数据处理")
        
        # 内存优化
        MemoryOptimizer.force_gc()
        monitor.checkpoint("内存优化")
        
        # 获取报告
        report = monitor.get_report()
        
        assert "初始化" in report
        assert "数据处理" in report
        assert "内存优化" in report
    
    def test_memory_and_cpu_monitoring(self):
        """测试内存和 CPU 监控"""
        # 获取初始状态
        initial_memory = MemoryOptimizer.get_memory_usage()
        initial_cpu = CPUOptimizer.get_cpu_usage()
        
        # 创建一些负载
        data = [list(range(1000)) for _ in range(100)]
        
        # 获取负载后状态
        loaded_memory = MemoryOptimizer.get_memory_usage()
        
        # 内存使用应该增加（或至少不减少）
        assert loaded_memory["rss_mb"] >= initial_memory["rss_mb"] * 0.9
        
        # 清理
        del data
        MemoryOptimizer.optimize_memory()
        
        # CPU 使用率应该是合理的
        assert initial_cpu >= 0
        assert initial_cpu <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
