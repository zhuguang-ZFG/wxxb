#!/usr/bin/env python3
"""测试Grbl命令参考功能"""

import sys
sys.path.insert(0, '.')

try:
    from linktunnel.unified_gui.modules.grbl_module import GrblModule, GrblCommandHelper, GRBL_COMMANDS
    
    print("✓ Grbl module imported successfully")
    print(f"✓ Commands available: {len(GRBL_COMMANDS)} categories")
    
    # 测试命令助手
    all_cmds = GrblCommandHelper.get_all_commands()
    print(f"✓ Total command categories: {len(all_cmds)}")
    
    # 测试搜索功能
    results = GrblCommandHelper.search_commands("回零")
    print(f"✓ Search for '回零': {len(results)} results")
    for category, cmd, desc in results:
        print(f"  - [{category}] {cmd}: {desc}")
    
    # 测试命令描述
    desc = GrblCommandHelper.get_command_description("$H")
    print(f"✓ Command description for '$H': {desc}")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
