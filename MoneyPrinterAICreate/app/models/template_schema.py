from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TemplateStatus(str, Enum):
    """模板状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class TemplateBase(BaseModel):
    """模板基础模型"""
    template_name: str = Field(..., description="模板名称")
    script_prompt: Optional[str] = Field(None, description="剧本创作提示词")
    character_prompt: Optional[str] = Field(None, description="角色创建提示词")
    scene_prompt: Optional[str] = Field(None, description="场景创建提示词")
    shot_prompt: Optional[str] = Field(None, description="分镜制作提示词")
    image_description_prompt: Optional[str] = Field(None, description="画面描述生成提示词")
    bgm_prompt: Optional[str] = Field(None, description="背景音乐创造提示词")
    video_generation_prompt: Optional[str] = Field(None, description="视频画面生成提示词")


class TemplateCreate(TemplateBase):
    """创建模板请求模型"""
    operator: Optional[str] = Field(None, description="操作人")


class TemplateUpdate(BaseModel):
    """更新模板请求模型"""
    template_name: Optional[str] = Field(None, description="模板名称")
    script_prompt: Optional[str] = Field(None, description="剧本创作提示词")
    character_prompt: Optional[str] = Field(None, description="角色创建提示词")
    scene_prompt: Optional[str] = Field(None, description="场景创建提示词")
    shot_prompt: Optional[str] = Field(None, description="分镜制作提示词")
    image_description_prompt: Optional[str] = Field(None, description="画面描述生成提示词")
    bgm_prompt: Optional[str] = Field(None, description="背景音乐创造提示词")
    video_generation_prompt: Optional[str] = Field(None, description="视频画面生成提示词")
    status: Optional[TemplateStatus] = Field(None, description="状态")
    operator: Optional[str] = Field(None, description="操作人")


class TemplateResponse(TemplateBase):
    """模板响应模型"""
    id: int = Field(..., description="模板ID")
    status: TemplateStatus = Field(..., description="状态")
    operator: str = Field(..., description="操作人")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """模板列表响应模型"""
    items: list[TemplateResponse] = Field(..., description="模板列表")
    total: int = Field(..., description="总数")