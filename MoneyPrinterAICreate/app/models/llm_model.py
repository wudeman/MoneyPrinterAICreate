from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
import enum
from typing import Optional

from app.config.database import Base


class ModelType(str, enum.Enum):
    """模型类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class LLMModel(Base):
    """大模型信息表"""
    __tablename__ = "llm_model"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="模型ID")
    display_name = Column(String(255), nullable=False, unique=True, comment="模型展示名称")
    model_name = Column(String(255), nullable=False, comment="模型名称")
    base_url = Column(Text, nullable=True, comment="调用地址")
    api_key = Column(Text, nullable=True, comment="密钥")
    model_type = Column(Enum(ModelType), nullable=False, comment="模型类型")
    support_reference_image = Column(Boolean, default=False, comment="是否支持参考图")
    support_multiple_reference_images = Column(Boolean, default=False, comment="是否支持多张参考图")
    support_first_frame = Column(Boolean, default=False, comment="是否支持首帧")
    support_last_frame = Column(Boolean, default=False, comment="是否支持尾帧")
    status = Column(Integer, default=1, comment="状态：1-启用，0-禁用")
    operator = Column(String(100), nullable=True, comment="操作人")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<LLMModel(id={self.id}, display_name='{self.display_name}', model_type={self.model_type})>"