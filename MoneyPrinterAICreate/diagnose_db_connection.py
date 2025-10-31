#!/usr/bin/env python3
"""
数据库连接诊断脚本
用于诊断数据库连接问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from app.config.config import _cfg

def diagnose_db_config():
    """诊断数据库配置"""
    print("=== 数据库配置诊断 ===")
    
    # 获取数据库配置
    db_config = _cfg.get("database", {})
    print(f"数据库配置: {db_config}")
    
    DB_HOST = db_config.get("host", "localhost")
    DB_PORT = db_config.get("port", 3306)
    DB_USER = db_config.get("user", "root")
    DB_PASSWORD = db_config.get("password", "")
    DB_NAME = db_config.get("db_name", "media")
    DB_CHARSET = db_config.get("charset", "utf8mb4")
    
    print(f"主机: {DB_HOST}")
    print(f"端口: {DB_PORT}")
    print(f"用户名: {DB_USER}")
    print(f"密码: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '空'}")
    print(f"数据库名: {DB_NAME}")
    print(f"字符集: {DB_CHARSET}")
    
    return DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET

def test_mysql_connection(host, port, user, password, db_name, charset):
    """测试MySQL连接"""
    print("\n=== MySQL连接测试 ===")
    
    try:
        # 测试基本连接（不指定数据库）
        print("1. 测试基本连接（不指定数据库）...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset=charset,
            connect_timeout=10
        )
        print("✅ 基本连接成功")
        connection.close()
        
        # 测试连接到指定数据库
        print("2. 测试连接到指定数据库...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset=charset,
            connect_timeout=10
        )
        print("✅ 数据库连接成功")
        connection.close()
        
        return True
    except pymysql.err.OperationalError as e:
        print(f"❌ MySQL连接失败: {e}")
        if e.args[0] == 2003:
            print("   可能的原因:")
            print("   - MySQL服务器未启动")
            print("   - 主机地址或端口不正确")
            print("   - 防火墙阻止了连接")
            print("   - MySQL服务器配置不允许远程连接")
        elif e.args[0] == 1045:
            print("   可能的原因:")
            print("   - 用户名或密码不正确")
        elif e.args[0] == 1049:
            print("   可能的原因:")
            print("   - 数据库不存在")
        return False
    except Exception as e:
        print(f"❌ 连接测试出现未知错误: {e}")
        return False

def check_mysql_server_status():
    """检查MySQL服务器状态"""
    print("\n=== MySQL服务器状态检查 ===")
    import subprocess
    
    try:
        # 尝试检查MySQL服务状态（Windows）
        result = subprocess.run(["sc", "query", "mysql"], capture_output=True, text=True, timeout=10)
        if "RUNNING" in result.stdout:
            print("✅ MySQL服务正在运行")
        elif "STOPPED" in result.stdout:
            print("❌ MySQL服务已停止")
        else:
            print("⚠️  无法确定MySQL服务状态")
    except Exception as e:
        print(f"⚠️  无法检查MySQL服务状态: {e}")

if __name__ == "__main__":
    print("数据库连接诊断工具")
    print("=" * 30)
    
    # 诊断配置
    host, port, user, password, db_name, charset = diagnose_db_config()
    
    # 检查MySQL服务器状态
    check_mysql_server_status()
    
    # 测试连接
    success = test_mysql_connection(host, port, user, password, db_name, charset)
    
    if success:
        print("\n🎉 数据库连接诊断完成，连接正常！")
    else:
        print("\n💥 数据库连接诊断完成，存在问题需要解决。")
        print("\n建议解决方案:")
        print("1. 确保MySQL服务器已启动")
        print("2. 检查配置文件中的数据库连接参数是否正确")
        print("3. 确保MySQL用户具有正确的权限")
        print("4. 检查防火墙设置")