from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON
from sqlalchemy.sql import func
import enum
from typing import Optional

from app.config.database import Base


class TaskStatus(int, enum.Enum):
    """任务状态枚举"""
    DELETED = -1        # 删除
    SCRIPT_GENERATING = 0   # 剧本生成中
    SCRIPT_COMPLETED = 1  # 剧本生成完成
    SCRIPT_FAILED = 2    # 剧本生成失败
    STORYBOARD_COMPLETED = 3  # 分镜生成完成
    STORYBOARD_FAILED = 4    # 分镜生成失败
    FRAMES_COMPLETED = 5     # 分镜画面生成完成
    FRAMES_FAILED = 6        # 分镜画面生成失败
    VIDEOS_COMPLETED = 7     # 分镜视频生成完成
    VIDEOS_FAILED = 8        # 分镜视频生成失败


class Task(Base):
    """任务表模型"""
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="任务ID")
    video_idea = Column(Text, comment="视频创意")
    template_id = Column(Integer, comment="视频模板ID")
    style_id = Column(Integer, comment="视频风格ID")
    aspect_ratio = Column(String(20), comment="视频比例")
    duration = Column(Integer, comment="视频时长（秒）")
    
    # JSON字段
    bgm = Column(JSON, comment="背景音（音乐描述，音乐地址，音量大小）")
    script = Column(Text, comment="剧本")
    character_list = Column(JSON, comment="角色列表")
    scene_list = Column(JSON, comment="场景列表")
    storyboard_list = Column(JSON, comment="分镜列表")
    storyboard_frame_list = Column(JSON, comment="分镜画面列表")
    storyboard_video_list = Column(JSON, comment="分镜视频列表")
    voice_list = Column(JSON, comment="配音列表")
    sound_effect_list = Column(JSON, comment="音效列表")
    
    # 状态和操作信息
    status = Column(Integer, default=1, comment="任务状态")
    operator = Column(String(100), comment="操作人")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), comment="更新时间")