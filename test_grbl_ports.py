#!/usr/bin/env python
"""测试 Grbl 模块串口列表"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("Grbl 模块 - 串口列表测试")
print("=" * 60)

try:
    from linktunnel.serial_util import list_serial_ports
    
    print("\n✓ 导入成功")
    print("✓ 列出可用的串口...")
    
    ports = list_serial_ports()
    
    print(f"\n发现 {len(ports)} 个串口:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device}")
        print(f"     描述: {port.description}")
        print(f"     硬件ID: {port.hwid}")
        print()
    
    if len(ports) == 0:
        print("⚠ 未发现任何串口设备")
        print("  请检查:")
        print("  • USB 设备是否已连接")
        print("  • 驱动程序是否已安装")
        print("  • 设备管理器中是否显示串口")
    else:
        print("✓ 串口列表正常")
    
    # 现在测试 Grbl 模块
    print("\n" + "=" * 60)
    print("测试 Grbl 模块...")
    print("=" * 60)
    
    from PyQt6.QtWidgets import QApplication
    from linktunnel.unified_gui.core.config_manager import ConfigManager
    from linktunnel.unified_gui.core.log_manager import LogManager
    from linktunnel.unified_gui.modules.grbl_module import GrblModule
    
    print("\n✓ 导入 Grbl 模块成功")
    
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    log_manager = LogManager()
    
    print("✓ 创建 Grbl 模块...")
    grbl = GrblModule(config_manager, log_manager)
    
    print("✓ Grbl 模块创建成功")
    print(f"✓ 模块名称: {grbl.get_module_name()}")
    print(f"✓ 显示名称: {grbl.get_display_name()}")
    
    # 检查串口下拉框
    if hasattr(grbl, '_port_combo'):
        port_count = grbl._port_combo.count()
        print(f"\n✓ 串口下拉框中有 {port_count} 个项目:")
        for i in range(port_count):
            print(f"  {i+1}. {grbl._port_combo.itemText(i)}")
    else:
        print("\n⚠ 未找到串口下拉框")
    
    print("\n" + "=" * 60)
    print("✓ 测试完成！")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
