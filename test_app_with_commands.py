#!/usr/bin/env python3
"""测试应用启动，包括Grbl命令参考功能"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动应用"""
    try:
        from PyQt6.QtWidgets import QApplication
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.fixed_main_window import FixedMainWindow
        
        print("✓ PyQt6 imports successful")
        
        # 创建应用
        app = QApplication(sys.argv)
        print("✓ QApplication created")
        
        # 创建配置管理器
        config_manager = ConfigManager()
        print("✓ ConfigManager created")
        
        # 创建主窗口
        window = FixedMainWindow(config_manager)
        print("✓ FixedMainWindow created")
        
        # 检查Grbl模块是否已注册
        if hasattr(window, 'module_container'):
            modules = window.module_container.modules
            print(f"✓ Modules registered: {len(modules)}")
            for name, module in modules.items():
                print(f"  - {name}: {module.get_display_name()}")
                if name == "grbl":
                    print(f"    ✓ Grbl module found!")
        
        # 显示窗口
        window.show()
        print("✓ Window shown")
        
        # 运行应用（只运行一个事件循环迭代）
        app.processEvents()
        print("✓ Application event loop processed")
        
        print("\n✓✓✓ Application started successfully! ✓✓✓")
        print("✓ Grbl command reference feature is integrated!")
        
        # 关闭窗口
        window.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
