#!/usr/bin/env python
"""测试启动脚本"""

import sys
import os

print("=" * 60)
print("linktunnel Unified GUI 启动测试")
print("=" * 60)

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print(f"\nPython 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print(f"当前目录: {os.getcwd()}")

# 测试导入
print("\n测试导入...")

try:
    print("1. 测试 PyQt6...")
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    print(f"   ✓ PyQt6 已安装")
    print(f"   - Qt 版本: {QT_VERSION_STR}")
    print(f"   - PyQt 版本: {PYQT_VERSION_STR}")
except ImportError as e:
    print(f"   ✗ PyQt6 未安装: {e}")
    print("\n请运行: pip install PyQt6")
    sys.exit(1)

try:
    print("\n2. 测试核心模块...")
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    print("   ✓ ConfigManager")
    
    from linktunnel.unified_gui.core.log_manager import LogManager
    print("   ✓ LogManager")
    
    from linktunnel.unified_gui.core.main_window import MainWindow
    print("   ✓ MainWindow")
    
except ImportError as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. 测试配置管理器...")
try:
    config_manager = ConfigManager()
    print(f"   ✓ 配置管理器创建成功")
except Exception as e:
    print(f"   ✗ 配置管理器创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. 测试日志管理器...")
try:
    log_manager = LogManager()
    print(f"   ✓ 日志管理器创建成功")
except Exception as e:
    print(f"   ✗ 日志管理器创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. 测试主窗口创建...")
try:
    app = QApplication(sys.argv)
    window = MainWindow(config_manager)
    print(f"   ✓ 主窗口创建成功")
    print(f"   - 窗口标题: {window.windowTitle()}")
    print(f"   - 窗口大小: {window.width()}x{window.height()}")
except Exception as e:
    print(f"   ✗ 主窗口创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ 所有测试通过！")
print("=" * 60)

print("\n启动应用程序...")
try:
    window.show()
    print("✓ 窗口已显示")
    print("\n提示: 关闭窗口以退出程序")
    sys.exit(app.exec())
except Exception as e:
    print(f"✗ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
