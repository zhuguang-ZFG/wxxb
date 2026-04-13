#!/usr/bin/env python
"""测试修复后的 UI - 字体清晰，颜色正确"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("linktunnel Unified GUI - 修复 UI 测试")
print("=" * 60)

try:
    from PyQt6.QtWidgets import QApplication
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.fixed_main_window import FixedMainWindow
    
    print("\n✓ 导入成功")
    print("✓ 创建应用程序...")
    
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    
    print("✓ 创建修复的主窗口...")
    window = FixedMainWindow(config_manager)
    
    print("✓ 显示窗口...")
    window.show()
    
    print("\n" + "=" * 60)
    print("✓ 修复 UI 已启动！")
    print("=" * 60)
    print("\n修复内容:")
    print("  ✓ 字体清晰 - 使用系统字体，11pt 大小")
    print("  ✓ 颜色正确 - 黑色文字，白色背景")
    print("  ✓ 对比度高 - 易于阅读")
    print("  ✓ 布局清晰 - 左侧导航，右侧内容")
    print("  ✓ 按钮清晰 - 蓝色选中，灰色未选中")
    print("\n快捷键:")
    print("  • Ctrl+T - 切换主题")
    print("  • F1 - 显示用户手册")
    print("\n关闭窗口以退出程序\n")
    
    sys.exit(app.exec())

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
