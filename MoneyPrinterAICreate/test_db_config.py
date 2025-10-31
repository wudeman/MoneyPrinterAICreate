#!/usr/bin/env python3
"""
测试数据库配置是否正确加载（使用应用程序自己的配置加载方法）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_config():
    """测试数据库配置"""
    print("=== 测试数据库配置加载 ===")
    
    try:
        # 使用应用程序自己的配置加载方法
        from app.config.config import _cfg
        print("✅ 成功导入应用程序配置模块")
    except Exception as e:
        print(f"❌ 导入应用程序配置模块失败: {e}")
        return False
    
    # 获取数据库配置
    db_config = _cfg.get("database", {})
    print(f"数据库配置: {db_config}")
    
    if not db_config:
        print("❌ 未找到数据库配置")
        return False
    
    required_keys = ["host", "port", "user", "password", "db_name"]
    for key in required_keys:
        if key not in db_config:
            print(f"❌ 缺少必要的数据库配置项: {key}")
            return False
        # 隐藏敏感信息
        display_value = db_config[key]
        if key == 'password' and display_value:
            display_value = '*' * len(str(display_value))
        print(f"✅ 数据库配置项 {key}: {display_value}")
    
    print("\n✅ 数据库配置检查通过")
    return True

if __name__ == "__main__":
    success = test_database_config()
    if not success:
        sys.exit(1)