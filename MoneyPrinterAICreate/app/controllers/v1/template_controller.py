from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func

from app.config.database import get_db
from app.models.template_model import TemplateModel, TemplateStatus
from app.models.template_schema import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse
)

# 移除前缀，因为会在router.py中统一添加
router = APIRouter()


@router.post("", response_model=TemplateResponse, summary="创建模板")
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db)
):
    """创建新的创作模板"""
    # 检查模板名称是否已存在
    existing_template = db.query(TemplateModel).filter(
        TemplateModel.template_name == template.template_name
    ).first()
    if existing_template:
        raise HTTPException(status_code=400, detail="模板名称已存在")
    
    # 创建新模板，自动设置操作人
    template_data = template.dict()
    # 如果前端没有提供操作人，则默认设置为'admin'
    if not template_data.get('operator'):
        template_data['operator'] = 'admin'
    
    db_template = TemplateModel(**template_data)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.get("", response_model=TemplateListResponse, summary="获取模板列表")
def get_templates(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[TemplateStatus] = Query(None, description="模板状态筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取创作模板列表，支持分页、状态筛选和关键词搜索"""
    query = db.query(TemplateModel)
    
    # 状态筛选
    if status:
        query = query.filter(TemplateModel.status == status)
    
    # 关键词搜索（搜索模板名称）
    if keyword:
        query = query.filter(TemplateModel.template_name.like(f"%{keyword}%"))
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    templates = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return TemplateListResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=total
    )


@router.get("/{template_id}", response_model=TemplateResponse, summary="获取模板详情")
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取模板详情"""
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return template


@router.put("/{template_id}", response_model=TemplateResponse, summary="更新模板")
def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新模板信息"""
    # 查找模板
    db_template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 如果更新模板名称，检查是否已存在
    if template_update.template_name and template_update.template_name != db_template.template_name:
        existing_template = db.query(TemplateModel).filter(
            TemplateModel.template_name == template_update.template_name,
            TemplateModel.id != template_id
        ).first()
        if existing_template:
            raise HTTPException(status_code=400, detail="模板名称已存在")
    
    # 更新模板信息，自动设置操作人
    update_data = template_update.dict(exclude_unset=True)
    # 如果前端没有提供操作人，则默认设置为'admin'
    update_data['operator'] = 'admin'
    
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.delete("/{template_id}", summary="删除模板")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """删除模板"""
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db.delete(template)
    db.commit()
    
    return {"message": "模板删除成功"}


@router.get("/active/list", response_model=list[TemplateResponse], summary="获取活跃模板列表")
def get_active_templates(
    db: Session = Depends(get_db)
):
    """获取所有状态为激活的模板列表，用于前端选择"""
    templates = db.query(TemplateModel).filter(
        TemplateModel.status == TemplateStatus.ACTIVE
    ).order_by(TemplateModel.id.desc()).all()
    
    return [TemplateResponse.model_validate(t) for t in templates]