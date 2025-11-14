from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.llm_model import LLMModel, ModelType
from app.models.llm_schema import (
    LLMModelCreate, 
    LLMModelUpdate, 
    LLMModelQuery,
    LLMModelResponse
)


class LLMModelService:
    """大模型管理服务"""
    
    @staticmethod
    def create_model(db: Session, model_data: LLMModelCreate) -> LLMModel:
        """创建新模型"""
        # 检查模型展示名称是否已存在
        existing_model = db.query(LLMModel).filter(
            LLMModel.display_name == model_data.display_name
        ).first()
        
        if existing_model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"模型展示名称 '{model_data.display_name}' 已存在"
            )
        
        # 为operator字段设置默认值"admin"
        model_dict = model_data.model_dump()
        if not model_dict.get('operator'):
            model_dict['operator'] = 'admin'
        
        # 创建模型实例
        db_model = LLMModel(**model_dict)
        
        # 如果设置为默认模型，先将其他同类型模型设为非默认
        if db_model.is_default == 1:
            db.query(LLMModel).filter(
                LLMModel.model_type == db_model.model_type
            ).update({"is_default": 0})
        
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def get_model(db: Session, model_id: int) -> Optional[LLMModel]:
        """根据ID获取模型"""
        model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型ID {model_id} 不存在"
            )
        return model
    
    @staticmethod
    def update_model(db: Session, model_id: int, model_data: LLMModelUpdate) -> LLMModel:
        """更新模型信息"""
        # 获取现有模型
        db_model = LLMModelService.get_model(db, model_id)
        
        # 如果要更新展示名称，检查是否与其他模型冲突
        update_data = model_data.model_dump(exclude_unset=True)
        if 'display_name' in update_data:
            existing_model = db.query(LLMModel).filter(
                LLMModel.display_name == update_data['display_name'],
                LLMModel.id != model_id
            ).first()
            if existing_model:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"模型展示名称 '{update_data['display_name']}' 已存在"
                )
        
        # 为operator字段设置默认值"admin"（如果没有提供）
        if 'operator' not in update_data:
            update_data['operator'] = 'admin'
        elif not update_data['operator']:
            update_data['operator'] = 'admin'
        
        # 如果要设置为默认模型，先将其他模型设为非默认
        if 'is_default' in update_data and update_data['is_default'] == 1:
            # 将其他同类型模型设为非默认
            db.query(LLMModel).filter(
                LLMModel.model_type == db_model.model_type,
                LLMModel.id != model_id
            ).update({"is_default": 0})
        
        # 更新模型字段
        for field, value in update_data.items():
            setattr(db_model, field, value)
        
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def delete_model(db: Session, model_id: int) -> bool:
        """删除模型"""
        db_model = LLMModelService.get_model(db, model_id)
        db.delete(db_model)
        db.commit()
        return True
    
    @staticmethod
    def list_models(db: Session, query: LLMModelQuery) -> tuple[List[LLMModel], int]:
        """获取模型列表，支持分页和筛选"""
        # 构建查询
        db_query = db.query(LLMModel)
        
        # 应用筛选条件
        if query.display_name:
            db_query = db_query.filter(
                LLMModel.display_name.like(f"%{query.display_name}%")
            )
        if query.model_name:
            db_query = db_query.filter(
                LLMModel.model_name.like(f"%{query.model_name}%")
            )
        if query.model_type:
            db_query = db_query.filter(LLMModel.model_type == query.model_type)
        if query.status is not None:
            db_query = db_query.filter(LLMModel.status == query.status)
        
        # 获取总数
        total = db_query.count()
        
        # 分页
        offset = (query.page - 1) * query.page_size
        models = db_query.offset(offset).limit(query.page_size).all()
        
        return models, total
    
    @staticmethod
    def get_active_models_by_type(db: Session, model_type: ModelType) -> List[LLMModel]:
        """根据类型获取所有启用状态的模型"""
        return db.query(LLMModel).filter(
            LLMModel.model_type == model_type,
            LLMModel.status == 1
        ).all()