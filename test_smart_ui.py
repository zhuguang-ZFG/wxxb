#!/usr/bin/env python
"""测试智能 UI"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("linktunnel Unified GUI - 智能 UI 测试")
print("=" * 60)

try:
    from PyQt6.QtWidgets import QApplication
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.smart_main_window import SmartMainWindow
    
    print("\n✓ 导入成功")
    print("✓ 创建应用程序...")
    
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    
    print("✓ 创建智能主窗口...")
    window = SmartMainWindow(config_manager)
    
    print("✓ 显示窗口...")
    window.show()
    
    print("\n" + "=" * 60)
    print("✓ 智能 UI 已启动！")
    print("=" * 60)
    print("\n功能特性:")
    print("  • 简洁清晰 - 左侧导航，右侧内容")
    print("  • 字体清晰 - 系统字体，易于阅读")
    print("  • 搜索功能 - 快速查找模块")
    print("  • 快捷键支持 - Ctrl+T 切换主题")
    print("  • 性能监控 - 自动优化内存")
    print("\n关闭窗口以退出程序\n")
    
    sys.exit(app.exec())

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
