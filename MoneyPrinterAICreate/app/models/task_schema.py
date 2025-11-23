from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.task_model import TaskStatus


class BGMInfo(BaseModel):
    """背景音乐信息"""
    music_description: Optional[str] = Field(None, description="音乐描述")
    music_url: Optional[str] = Field(None, description="音乐地址")
    volume: Optional[float] = Field(0.5, description="音量大小")


class CharacterInfo(BaseModel):
    """角色信息"""
    character_name: str = Field(..., description="角色名称")
    brief_description: Optional[str] = Field(None, description="简要描述")
    appearance_description: Optional[str] = Field(None, description="外观描述")
    recommended_voice: Optional[str] = Field(None, description="推荐音色")
    character_image_url: Optional[str] = Field(None, description="角色图片地址")


class SceneInfo(BaseModel):
    """场景信息"""
    scene_name: str = Field(..., description="场景名称")
    visual_elements: Optional[str] = Field(None, description="视觉元素")
    scene_image_url: Optional[str] = Field(None, description="场景图片地址")


class StoryboardInfo(BaseModel):
    """分镜信息"""
    scene_description: str = Field(..., description="画面描述")
    camera_design: Optional[str] = Field(None, description="镜头设计")
    voice_character: Optional[str] = Field(None, description="配音角色")
    dialogue_content: Optional[str] = Field(None, description="台词内容")


class StoryboardFrameInfo(BaseModel):
    """分镜画面信息"""
    frame_prompt: str = Field(..., description="画面提示词")
    frame_url: Optional[str] = Field(None, description="画面地址")


class StoryboardVideoInfo(BaseModel):
    """分镜视频信息"""
    video_prompt: str = Field(..., description="视频提示词")
    video_url: Optional[str] = Field(None, description="视频地址")
    duration: Optional[int] = Field(None, description="时长")


class VoiceInfo(BaseModel):
    """配音信息"""
    voice_content: str = Field(..., description="配音内容")
    voice_url: Optional[str] = Field(None, description="配音地址")
    voice_type: Optional[str] = Field(None, description="音色")
    volume: Optional[float] = Field(0.5, description="音量大小")
    speed: Optional[float] = Field(1.0, description="语速")


class SoundEffectInfo(BaseModel):
    """音效信息"""
    effect_prompt: str = Field(..., description="音效提示词")
    effect_url: Optional[str] = Field(None, description="音效地址")
    volume: Optional[float] = Field(0.5, description="音量大小")


class TaskBase(BaseModel):
    """任务基础模型"""
    video_idea: str = Field(..., description="视频创意")
    template_id: int = Field(..., description="视频模板ID")
    style_id: int = Field(..., description="视频风格ID")
    aspect_ratio: str = Field(..., description="视频比例")
    duration: int = Field(..., description="视频时长（秒）")
    bgm: Optional[BGMInfo] = Field(None, description="背景音信息")


class TaskCreate(TaskBase):
    """创建任务请求模型"""
    operator: Optional[str] = Field("admin", description="操作人")


class TaskUpdate(BaseModel):
    """更新任务请求模型"""
    video_idea: Optional[str] = Field(None, description="视频创意")
    template_id: Optional[int] = Field(None, description="视频模板ID")
    style_id: Optional[int] = Field(None, description="视频风格ID")
    aspect_ratio: Optional[str] = Field(None, description="视频比例")
    duration: Optional[int] = Field(None, description="视频时长（秒）")
    bgm: Optional[BGMInfo] = Field(None, description="背景音信息")
    script: Optional[str] = Field(None, description="剧本")
    character_list: Optional[List[CharacterInfo]] = Field(None, description="角色列表")
    scene_list: Optional[List[SceneInfo]] = Field(None, description="场景列表")
    storyboard_list: Optional[List[StoryboardInfo]] = Field(None, description="分镜列表")
    storyboard_frame_list: Optional[List[StoryboardFrameInfo]] = Field(None, description="分镜画面列表")
    storyboard_video_list: Optional[List[StoryboardVideoInfo]] = Field(None, description="分镜视频列表")
    voice_list: Optional[List[VoiceInfo]] = Field(None, description="配音列表")
    sound_effect_list: Optional[List[SoundEffectInfo]] = Field(None, description="音效列表")
    status: Optional[TaskStatus] = Field(None, description="任务状态")
    operator: Optional[str] = Field("admin", description="操作人")


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: int = Field(..., description="任务ID")
    script: Optional[str] = Field(None, description="剧本")
    character_list: Optional[List[CharacterInfo]] = Field(None, description="角色列表")
    scene_list: Optional[List[SceneInfo]] = Field(None, description="场景列表")
    storyboard_list: Optional[List[StoryboardInfo]] = Field(None, description="分镜列表")
    storyboard_frame_list: Optional[List[StoryboardFrameInfo]] = Field(None, description="分镜画面列表")
    storyboard_video_list: Optional[List[StoryboardVideoInfo]] = Field(None, description="分镜视频列表")
    voice_list: Optional[List[VoiceInfo]] = Field(None, description="配音列表")
    sound_effect_list: Optional[List[SoundEffectInfo]] = Field(None, description="音效列表")
    status: TaskStatus = Field(..., description="任务状态")
    operator: str = Field(..., description="操作人")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class TaskCreateResponse(BaseModel):
    """创建任务响应模型"""
    task_id: int = Field(..., description="创建的任务ID")
    message: str = Field(..., description="操作信息")