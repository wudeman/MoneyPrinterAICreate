from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import get_db
from app.models.dict_model import DictModel, DictStatus
from app.models.dict_schema import (
    DictCreate, DictUpdate, DictResponse, DictListResponse
)


# 创建路由器
router = APIRouter()


@router.post("", response_model=DictResponse, summary="创建字典")
def create_dict(
    dict_data: DictCreate,
    db: Session = Depends(get_db)
):
    """创建新的字典项"""
    # 检查字典名称是否已存在
    existing_name = db.query(DictModel).filter(
        DictModel.dict_name == dict_data.dict_name
    ).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="字典名称已存在")
    
    # 检查字典键是否已存在
    existing_key = db.query(DictModel).filter(
        DictModel.dict_key == dict_data.dict_key
    ).first()
    if existing_key:
        raise HTTPException(status_code=400, detail="字典键已存在")
    
    # 创建新字典，自动设置操作人
    dict_data_dict = dict_data.dict()
    # 如果前端没有提供操作人，则默认设置为'admin'
    if not dict_data_dict.get('operator'):
        dict_data_dict['operator'] = 'admin'
    
    db_dict = DictModel(**dict_data_dict)
    db.add(db_dict)
    db.commit()
    db.refresh(db_dict)
    
    return db_dict


@router.get("", response_model=DictListResponse, summary="获取字典列表")
def get_dicts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[DictStatus] = Query(None, description="状态筛选"),
    dict_type: Optional[str] = Query(None, description="字典类型筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取字典列表，支持分页、状态筛选和关键词搜索"""
    query = db.query(DictModel)
    
    # 状态筛选
    if status:
        query = query.filter(DictModel.status == status)
    
    # 类型筛选
    if dict_type:
        query = query.filter(DictModel.dict_type == dict_type)
    
    # 关键词搜索（搜索字典名称、键、值、描述）
    if keyword:
        query = query.filter(
            (
                DictModel.dict_name.like(f"%{keyword}%") |
                DictModel.dict_key.like(f"%{keyword}%") |
                DictModel.dict_value.like(f"%{keyword}%") |
                (DictModel.description != None) & (DictModel.description.like(f"%{keyword}%"))
            )
        )
    
    # 计算总数
    total = query.count()
    
    # 按排序序号和ID排序，然后分页查询
    dicts = query.order_by(
        DictModel.sort_order.asc(),
        DictModel.id.asc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return DictListResponse(
        items=[DictResponse.model_validate(d) for d in dicts],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{dict_id}", response_model=DictResponse, summary="获取字典详情")
def get_dict(
    dict_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取字典详情"""
    dict_item = db.query(DictModel).filter(DictModel.id == dict_id).first()
    if not dict_item:
        raise HTTPException(status_code=404, detail="字典不存在")
    
    return dict_item


@router.put("/{dict_id}", response_model=DictResponse, summary="更新字典")
def update_dict(
    dict_id: int,
    dict_update: DictUpdate,
    db: Session = Depends(get_db)
):
    """更新字典信息"""
    # 查找字典
    db_dict = db.query(DictModel).filter(DictModel.id == dict_id).first()
    if not db_dict:
        raise HTTPException(status_code=404, detail="字典不存在")
    
    # 检查字典名称是否已存在（排除当前记录）
    if dict_update.dict_name and dict_update.dict_name != db_dict.dict_name:
        existing_name = db.query(DictModel).filter(
            DictModel.dict_name == dict_update.dict_name,
            DictModel.id != dict_id
        ).first()
        if existing_name:
            raise HTTPException(status_code=400, detail="字典名称已存在")
    
    # 检查字典键是否已存在（排除当前记录）
    if dict_update.dict_key and dict_update.dict_key != db_dict.dict_key:
        existing_key = db.query(DictModel).filter(
            DictModel.dict_key == dict_update.dict_key,
            DictModel.id != dict_id
        ).first()
        if existing_key:
            raise HTTPException(status_code=400, detail="字典键已存在")
    
    # 更新字典信息，自动设置操作人
    update_data = dict_update.dict(exclude_unset=True)
    # 强制设置操作为'admin'
    update_data['operator'] = 'admin'
    
    for field, value in update_data.items():
        setattr(db_dict, field, value)
    
    db.commit()
    db.refresh(db_dict)
    
    return db_dict


@router.delete("/{dict_id}", summary="删除字典")
def delete_dict(
    dict_id: int,
    db: Session = Depends(get_db)
):
    """删除字典"""
    dict_item = db.query(DictModel).filter(DictModel.id == dict_id).first()
    if not dict_item:
        raise HTTPException(status_code=404, detail="字典不存在")
    
    db.delete(dict_item)
    db.commit()
    
    return {"message": "字典删除成功"}


@router.get("/type/list", response_model=list[str], summary="获取所有字典类型列表")
def get_dict_types(
    db: Session = Depends(get_db)
):
    """获取所有不重复的字典类型列表"""
    types = db.query(DictModel.dict_type).distinct().all()
    return [t[0] for t in types]


@router.get("/active/list", response_model=list[DictResponse], summary="获取活跃字典列表")
def get_active_dicts(
    dict_type: Optional[str] = Query(None, description="字典类型筛选"),
    db: Session = Depends(get_db)
):
    """获取所有状态为激活的字典列表，可按类型筛选"""
    query = db.query(DictModel).filter(DictModel.status == DictStatus.ACTIVE)
    
    if dict_type:
        query = query.filter(DictModel.dict_type == dict_type)
    
    dicts = query.order_by(DictModel.sort_order.asc(), DictModel.id.asc()).all()
    return [DictResponse.model_validate(d) for d in dicts]