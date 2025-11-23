from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.template_model import TemplateModel, TemplateStatus
from app.models.template_schema import TemplateCreate, TemplateUpdate


class TemplateService:
    """
    模板管理服务
    负责处理模板的创建、查询、更新和删除等操作
    """
    
    @staticmethod
    def get_template_by_id(db: Session, template_id: int) -> Optional[TemplateModel]:
        """
        根据ID获取模板
        
        Args:
            db: 数据库会话
            template_id: 模板ID
            
        Returns:
            模板对象，如果不存在则返回None
        """
        return db.query(TemplateModel).filter(
            TemplateModel.id == template_id,
            TemplateModel.status == TemplateStatus.ACTIVE
        ).first()
    
    @staticmethod
    def get_all_active_templates(db: Session) -> list[TemplateModel]:
        """
        获取所有激活状态的模板
        
        Args:
            db: 数据库会话
            
        Returns:
            激活状态的模板列表
        """
        return db.query(TemplateModel).filter(
            TemplateModel.status == TemplateStatus.ACTIVE
        ).all()
    
    @staticmethod
    def create_template(db: Session, template_data: TemplateCreate) -> TemplateModel:
        """
        创建新模板
        
        Args:
            db: 数据库会话
            template_data: 模板创建数据
            
        Returns:
            创建的模板对象
            
        Raises:
            HTTPException: 如果模板名称已存在
        """
        # 检查模板名称是否已存在
        existing_template = db.query(TemplateModel).filter(
            TemplateModel.template_name == template_data.template_name
        ).first()
        
        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模板名称已存在"
            )
        
        # 创建新模板
        template_dict = template_data.model_dump()
        # 如果前端没有提供操作人，则默认设置为'admin'
        if not template_dict.get('operator'):
            template_dict['operator'] = 'admin'
        
        db_template = TemplateModel(**template_dict)
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return db_template
    
    @staticmethod
    def update_template(db: Session, template_id: int, template_data: TemplateUpdate) -> TemplateModel:
        """
        更新模板
        
        Args:
            db: 数据库会话
            template_id: 模板ID
            template_data: 模板更新数据
            
        Returns:
            更新后的模板对象
            
        Raises:
            HTTPException: 如果模板不存在或名称冲突
        """
        # 查找模板
        db_template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
        if not db_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )
        
        # 如果更新模板名称，检查是否已存在
        update_data = template_data.model_dump(exclude_unset=True)
        if 'template_name' in update_data and update_data['template_name'] != db_template.template_name:
            existing_template = db.query(TemplateModel).filter(
                TemplateModel.template_name == update_data['template_name'],
                TemplateModel.id != template_id
            ).first()
            if existing_template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="模板名称已存在"
                )
        
        # 更新模板信息
        # 如果前端没有提供操作人，则默认设置为'admin'
        update_data['operator'] = 'admin'
        
        for field, value in update_data.items():
            setattr(db_template, field, value)
        
        db.commit()
        db.refresh(db_template)
        
        return db_template