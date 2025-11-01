from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.llm_model import ModelType


class LLMModelBase(BaseModel):
    """大模型基础信息"""
    display_name: str = Field(..., description="模型展示名称")
    model_name: str = Field(..., description="模型名称")
    model_provider: Optional[str] = Field(None, description="模型供应商")
    base_url: Optional[str] = Field(None, description="调用地址")
    api_key: Optional[str] = Field(None, description="密钥")
    model_type: ModelType = Field(..., description="模型类型")
    support_reference_image: bool = Field(False, description="是否支持参考图")
    support_multiple_reference_images: bool = Field(False, description="是否支持多张参考图")
    support_first_frame: bool = Field(False, description="是否支持首帧")
    support_last_frame: bool = Field(False, description="是否支持尾帧")
    status: int = Field(1, description="状态：1-启用，0-禁用")


class LLMModelCreate(LLMModelBase):
    """创建大模型请求"""
    operator: Optional[str] = Field(None, description="操作人")


class LLMModelUpdate(BaseModel):
    """更新大模型请求"""
    display_name: Optional[str] = Field(None, description="模型展示名称")
    model_name: Optional[str] = Field(None, description="模型名称")
    model_provider: Optional[str] = Field(None, description="模型供应商")
    base_url: Optional[str] = Field(None, description="调用地址")
    api_key: Optional[str] = Field(None, description="密钥")
    model_type: Optional[ModelType] = Field(None, description="模型类型")
    support_reference_image: Optional[bool] = Field(None, description="是否支持参考图")
    support_multiple_reference_images: Optional[bool] = Field(None, description="是否支持多张参考图")
    support_first_frame: Optional[bool] = Field(None, description="是否支持首帧")
    support_last_frame: Optional[bool] = Field(None, description="是否支持尾帧")
    status: Optional[int] = Field(None, description="状态：1-启用，0-禁用")
    operator: Optional[str] = Field(None, description="操作人")


class LLMModelResponse(LLMModelBase):
    """大模型响应"""
    id: int
    operator: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LLMModelListResponse(BaseModel):
    """大模型列表响应"""
    models: List[LLMModelResponse]
    total: int


class LLMModelQuery(BaseModel):
    """大模型查询条件"""
    display_name: Optional[str] = Field(None, description="模型展示名称")
    model_name: Optional[str] = Field(None, description="模型名称")
    model_type: Optional[ModelType] = Field(None, description="模型类型")
    status: Optional[int] = Field(None, description="状态")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")