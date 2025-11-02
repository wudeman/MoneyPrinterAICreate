from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
import enum
from typing import Optional

from app.config.database import Base


class TemplateStatus(str, enum.Enum):
    """模板状态枚举"""
    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 停用


class TemplateModel(Base):
    """创作模板表"""
    __tablename__ = "creation_template"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="模板ID")
    template_name = Column(String(255), nullable=False, unique=True, comment="模板名称")
    script_prompt = Column(Text, nullable=True, comment="剧本创作提示词")
    character_prompt = Column(Text, nullable=True, comment="角色创建提示词")
    scene_prompt = Column(Text, nullable=True, comment="场景创建提示词")
    shot_prompt = Column(Text, nullable=True, comment="分镜制作提示词")
    image_description_prompt = Column(Text, nullable=True, comment="画面描述生成提示词")
    bgm_prompt = Column(Text, nullable=True, comment="背景音乐创造提示词")
    video_generation_prompt = Column(Text, nullable=True, comment="视频画面生成提示词")
    operator = Column(String(100), nullable=False, comment="操作人")
    status = Column(Enum(TemplateStatus), default=TemplateStatus.ACTIVE, comment="状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<TemplateModel(id={self.id}, template_name='{self.template_name}', status={self.status})>"