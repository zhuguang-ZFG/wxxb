#!/usr/bin/env python3
"""测试Grbl模块UI，包括命令参考功能"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_grbl_module():
    """测试Grbl模块"""
    try:
        # 导入必要的模块
        from linktunnel.unified_gui.core.config_manager import ConfigManager
        from linktunnel.unified_gui.core.log_manager import LogManager
        from linktunnel.unified_gui.modules.grbl_module import GrblModule, GrblCommandHelper
        
        print("✓ Imports successful")
        
        # 创建配置和日志管理器
        config_manager = ConfigManager()
        log_manager = LogManager()
        
        print("✓ Managers created")
        
        # 创建Grbl模块
        grbl_module = GrblModule(config_manager, log_manager)
        
        print("✓ GrblModule created successfully")
        print(f"  - Module name: {grbl_module.get_module_name()}")
        print(f"  - Display name: {grbl_module.get_display_name()}")
        
        # 测试命令助手
        all_commands = GrblCommandHelper.get_all_commands()
        print(f"✓ Command categories: {len(all_commands)}")
        for category in all_commands:
            print(f"  - {category}: {len(all_commands[category])} commands")
        
        # 测试搜索
        search_results = GrblCommandHelper.search_commands("回零")
        print(f"✓ Search results for '回零': {len(search_results)} found")
        
        # 测试命令描述
        desc = GrblCommandHelper.get_command_description("$H")
        print(f"✓ Command description: {desc}")
        
        print("\n✓✓✓ All tests passed! ✓✓✓")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_grbl_module()
    sys.exit(0 if success else 1)
