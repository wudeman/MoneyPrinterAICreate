from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DictStatus(str, Enum):
    """字典状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class DictBase(BaseModel):
    """字典基础模型"""
    dict_name: str = Field(..., description="字典名称")
    dict_key: str = Field(..., description="字典键")
    dict_value: str = Field(..., description="字典值")
    dict_type: str = Field(..., description="字典类型")
    description: Optional[str] = Field(None, description="字典描述")
    sort_order: Optional[int] = Field(0, description="排序序号")


class DictCreate(DictBase):
    """创建字典请求模型"""
    operator: Optional[str] = Field(None, description="操作人")


class DictUpdate(BaseModel):
    """更新字典请求模型"""
    dict_name: Optional[str] = Field(None, description="字典名称")
    dict_key: Optional[str] = Field(None, description="字典键")
    dict_value: Optional[str] = Field(None, description="字典值")
    dict_type: Optional[str] = Field(None, description="字典类型")
    description: Optional[str] = Field(None, description="字典描述")
    sort_order: Optional[int] = Field(None, description="排序序号")
    status: Optional[DictStatus] = Field(None, description="状态")
    operator: Optional[str] = Field(None, description="操作人")


class DictResponse(DictBase):
    """字典响应模型"""
    id: int = Field(..., description="字典ID")
    status: DictStatus = Field(..., description="状态")
    operator: str = Field(..., description="操作人")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class DictListResponse(BaseModel):
    """字典列表响应模型"""
    items: list[DictResponse] = Field(..., description="字典列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页数量")