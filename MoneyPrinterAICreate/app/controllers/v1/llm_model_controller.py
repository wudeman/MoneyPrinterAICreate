from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.llm_schema import (
    LLMModelCreate,
    LLMModelUpdate,
    LLMModelResponse,
    LLMModelListResponse,
    LLMModelQuery
)
from app.services.llm_model_service import LLMModelService

# 创建路由器
router = APIRouter(
    prefix="/models",
    tags=["大模型管理"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add", response_model=LLMModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model: LLMModelCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的大模型
    
    Args:
        model: 大模型创建请求数据
        db: 数据库会话
        
    Returns:
        创建的大模型信息
    """
    try:
        db_model = LLMModelService.create_model(db, model)
        return LLMModelResponse.model_validate(db_model)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建模型失败: {str(e)}"
        )


@router.get("/{model_id}", response_model=LLMModelResponse)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取大模型信息
    
    Args:
        model_id: 模型ID
        db: 数据库会话
        
    Returns:
        大模型信息
    """
    try:
        db_model = LLMModelService.get_model(db, model_id)
        return LLMModelResponse.model_validate(db_model)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型失败: {str(e)}"
        )


@router.put("/{model_id}", response_model=LLMModelResponse)
async def update_model(
    model_id: int,
    model: LLMModelUpdate,
    db: Session = Depends(get_db)
):
    """
    更新大模型信息
    
    Args:
        model_id: 模型ID
        model: 模型更新数据
        db: 数据库会话
        
    Returns:
        更新后的模型信息
    """
    try:
        db_model = LLMModelService.update_model(db, model_id, model)
        return LLMModelResponse.model_validate(db_model)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新模型失败: {str(e)}"
        )


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    删除大模型
    
    Args:
        model_id: 模型ID
        db: 数据库会话
    """
    try:
        LLMModelService.delete_model(db, model_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除模型失败: {str(e)}"
        )


@router.post("/list", response_model=LLMModelListResponse)
async def list_models(
    query: LLMModelQuery,
    db: Session = Depends(get_db)
):
    """
    获取大模型列表，支持分页和筛选
    
    Args:
        query: 查询条件
        db: 数据库会话
        
    Returns:
        模型列表和总数
    """
    try:
        models, total = LLMModelService.list_models(db, query)
        model_responses = [
            LLMModelResponse.model_validate(model) for model in models
        ]
        return LLMModelListResponse(models=model_responses, total=total)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型列表失败: {str(e)}"
        )