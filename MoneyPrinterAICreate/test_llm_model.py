#!/usr/bin/env python3
"""
大模型管理模块测试脚本
用于验证数据库连接和基本CRUD操作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine, Base
from app.models.llm_model import LLMModel, ModelType
from app.services.llm_model_service import LLMModelService
from app.models.llm_schema import LLMModelCreate, LLMModelUpdate, LLMModelQuery

def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    try:
        # 测试连接
        with engine.connect() as conn:
            print("✅ 数据库连接成功")
            
        # 重新创建表（仅测试用）
        print("创建测试表...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ 测试表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_create_model(db: Session):
    """测试创建模型"""
    print("\n=== 测试创建模型 ===")
    try:
        # 创建测试模型
        model_data = LLMModelCreate(
            display_name="测试文本模型",
            model_name="test-text-model-v1",
            base_url="http://localhost:8000/v1",
            api_key="test-api-key",
            model_type=ModelType.TEXT,
            support_reference_image=False,
            support_multiple_reference_images=False,
            support_first_frame=False,
            support_last_frame=False,
            status=1,
            operator="测试用户"
        )
        
        model = LLMModelService.create_model(db, model_data)
        print(f"✅ 模型创建成功: {model}")
        return model
    except Exception as e:
        print(f"❌ 模型创建失败: {e}")
        return None

def test_get_model(db: Session, model_id: int):
    """测试获取模型"""
    print("\n=== 测试获取模型 ===")
    try:
        model = LLMModelService.get_model(db, model_id)
        print(f"✅ 模型获取成功: {model}")
        return model
    except Exception as e:
        print(f"❌ 模型获取失败: {e}")
        return None

def test_update_model(db: Session, model_id: int):
    """测试更新模型"""
    print("\n=== 测试更新模型 ===")
    try:
        update_data = LLMModelUpdate(
            display_name="更新后的测试模型",
            base_url="http://localhost:8000/v2",
            status=0,
            operator="更新用户"
        )
        
        model = LLMModelService.update_model(db, model_id, update_data)
        print(f"✅ 模型更新成功: {model}")
        return model
    except Exception as e:
        print(f"❌ 模型更新失败: {e}")
        return None

def test_list_models(db: Session):
    """测试获取模型列表"""
    print("\n=== 测试获取模型列表 ===")
    try:
        query = LLMModelQuery(
            page=1,
            page_size=10
        )
        
        models, total = LLMModelService.list_models(db, query)
        print(f"✅ 获取模型列表成功，总数: {total}")
        for model in models:
            print(f"  - {model}")
        return models
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return []

def test_delete_model(db: Session, model_id: int):
    """测试删除模型"""
    print("\n=== 测试删除模型 ===")
    try:
        LLMModelService.delete_model(db, model_id)
        print(f"✅ 模型删除成功")
        return True
    except Exception as e:
        print(f"❌ 模型删除失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试大模型管理模块...")
    
    # 测试数据库连接
    if not test_database_connection():
        print("数据库连接失败，测试终止")
        return
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 测试创建模型
        model = test_create_model(db)
        if not model:
            return
        
        # 测试获取模型
        test_get_model(db, model.id)
        
        # 测试更新模型
        test_update_model(db, model.id)
        
        # 测试获取模型列表
        test_list_models(db)
        
        # 测试删除模型
        test_delete_model(db, model.id)
        
        # 验证删除后的列表
        print("\n=== 验证删除后列表 ===")
        query = LLMModelQuery(page=1, page_size=10)
        models, total = LLMModelService.list_models(db, query)
        print(f"删除后模型总数: {total}")
        
        print("\n🎉 所有测试完成！")
        
    finally:
        # 清理测试数据
        try:
            Base.metadata.drop_all(bind=engine)
            print("\n✅ 测试数据清理完成")
        except Exception as e:
            print(f"⚠️  测试数据清理失败: {e}")
        
        # 关闭会话
        db.close()
        print("✅ 数据库会话已关闭")


if __name__ == "__main__":
    main()