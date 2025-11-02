from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
import enum
from typing import Optional

from app.config.database import Base


class DictStatus(str, enum.Enum):
    """字典状态枚举"""
    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 停用


class DictModel(Base):
    """字典管理表"""
    __tablename__ = "dict_management"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="字典ID")
    dict_name = Column(String(255), nullable=False, unique=True, comment="字典名称")
    dict_key = Column(String(100), nullable=False, unique=True, comment="字典键")
    dict_value = Column(String(500), nullable=False, comment="字典值")
    dict_type = Column(String(100), nullable=False, comment="字典类型")
    description = Column(String(500), nullable=True, comment="字典描述")
    sort_order = Column(Integer, default=0, comment="排序序号")
    status = Column(Enum(DictStatus), default=DictStatus.ACTIVE, comment="状态")
    operator = Column(String(100), nullable=False, comment="操作人")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<DictModel(id={self.id}, dict_name='{self.dict_name}', dict_type='{self.dict_type}', status={self.status})>"