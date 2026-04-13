#!/usr/bin/env python
"""测试现代化 UI"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("linktunnel Unified GUI - 现代化 UI 测试")
print("=" * 60)

try:
    from PyQt6.QtWidgets import QApplication
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.modern_main_window import ModernMainWindow
    
    print("\n✓ 导入成功")
    print("✓ 创建应用程序...")
    
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    
    print("✓ 创建现代化主窗口...")
    window = ModernMainWindow(config_manager)
    
    print("✓ 显示窗口...")
    window.show()
    
    print("\n" + "=" * 60)
    print("✓ 现代化 UI 已启动！")
    print("=" * 60)
    print("\n功能特性:")
    print("  • 现代化设计 - 蓝色主题、卡片式布局")
    print("  • 智能导航 - 搜索、快速访问")
    print("  • 响应式布局 - 自适应窗口大小")
    print("  • 动画效果 - 平滑过渡")
    print("  • 快捷键支持 - Ctrl+T 切换主题")
    print("\n按 Ctrl+K 打开命令面板")
    print("关闭窗口以退出程序\n")
    
    sys.exit(app.exec())

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
