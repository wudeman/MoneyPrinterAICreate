#!/usr/bin/env python3
"""
数据库迁移脚本：为llm_model表添加is_default字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.config.database import engine

def migrate_db():
    """执行数据库迁移"""
    try:
        with engine.connect() as conn:
            # 检查字段是否已存在（MySQL/TiDB兼容语法）
            check_column_query = text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'llm_model' AND COLUMN_NAME = 'is_default'")
            result = conn.execute(check_column_query)
            columns = [row[0] for row in result]
            
            if not columns:
                # 添加is_default字段，默认值为0（false）
                add_column_query = text("ALTER TABLE llm_model ADD COLUMN is_default INTEGER DEFAULT 0 COMMENT '是否默认：1-是，0-否'")
                conn.execute(add_column_query)
                conn.commit()
                print("✅ 成功为llm_model表添加is_default字段")
            else:
                print("ℹ️ is_default字段已存在，无需重复添加")
    except Exception as e:
        print(f"❌ 数据库迁移失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_db()