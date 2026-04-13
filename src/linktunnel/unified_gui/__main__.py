"""
linktunnel Unified GUI 主入口

运行方式:
    python -m linktunnel.unified_gui
    或
    linktunnel-unified
"""

import sys


def main() -> int:
    """主函数入口"""
    try:
        # 检查 PyQt6 是否可用
        try:
            from PyQt6.QtWidgets import QApplication
            from linktunnel.unified_gui.core.main_window import MainWindow
            from linktunnel.unified_gui.core.config_manager import ConfigManager
            
            app = QApplication(sys.argv)
            app.setApplicationName("linktunnel Unified GUI")
            app.setOrganizationName("linktunnel")
            
            config_manager = ConfigManager()
            window = MainWindow(config_manager)
            window.show()
            
            return app.exec()
            
        except ImportError:
            print("错误: 未安装 PyQt6")
            print("请运行: pip install 'linktunnel[gui]'")
            return 1
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 0
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
