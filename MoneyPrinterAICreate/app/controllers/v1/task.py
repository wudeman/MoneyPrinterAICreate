from fastapi import Depends, HTTPException, BackgroundTasks, Request, UploadFile, File
from loguru import logger
from pydantic import BaseModel, Field
import uuid
import os
import re
import time
from typing import List, Optional

from app.controllers.v1.base import new_router
from app.controllers import base as base_controller
from app.models.schema import VideoParams, TaskResponse
from app.models.task_model import Task, TaskStatus
from app.models.task_schema import TaskCreate
from app.services.task_service import TaskService
from app.services import task as task_service
from app.services import state as state_service
from app.services import llm
from app.services import bgm_service
from app.utils import utils
from app.config.database import get_db
from sqlalchemy.orm import Session

router = new_router()

# 预设的分镜效果模板
EFFECT_TEMPLATES = [
    "",
    "特写镜头",
    "中景",
    "远景",
    "俯视角度",
    "仰视角度",
    "慢动作",
    "快速切换",
    "淡入淡出",
    "平移跟随"
]


class ScriptGenerateRequest(BaseModel):
    """剧本生成请求模型"""
    video_subject: str = Field(..., description="视频主题/创作灵感")
    template_id: str = Field("", description="模板ID")
    style_id: str = Field("", description="风格ID")
    video_language: str = Field("zh", description="视频语言")
    paragraph_number: int = Field(5, ge=1, le=20, description="段落数量")
    duration: int = Field(30, ge=10, le=300, description="视频时长(秒)")


class ScriptUpdateRequest(BaseModel):
    """剧本更新请求模型"""
    script: str = Field(..., description="剧本内容")


class ScriptGenerateResponse(BaseModel):
    """剧本生成响应模型"""
    task_id: str = Field(..., description="任务ID")
    script: str = Field(..., description="生成的剧本内容")


class CharacterModel(BaseModel):
    """角色模型"""
    name: str = Field(..., description="角色名称")
    description: str = Field(..., description="角色描述")


class SceneModel(BaseModel):
    """场景模型"""
    name: str = Field(..., description="场景名称")
    description: str = Field(..., description="场景描述")


class DesignUpdateRequest(BaseModel):
    """设计更新请求模型"""
    characters: List[CharacterModel] = Field(..., description="角色列表")
    scenes: List[SceneModel] = Field(..., description="场景列表")
    bgm_type: str = Field("none", description="背景音乐类型")


class StoryboardItem(BaseModel):
    """分镜项模型"""
    scene: str = Field(..., description="场景")
    characters: List[str] = Field(..., description="角色列表")
    actions: str = Field(..., description="动作描述")
    duration: int = Field(..., description="时长")
    description: str = Field(..., description="详细描述")
    effects: str = Field(..., description="特效")
    cameraAngle: Optional[str] = Field(None, description="摄像机角度")
    transition: Optional[str] = Field(None, description="转场效果")


class StoryboardUpdateRequest(BaseModel):
    """分镜更新请求模型"""
    storyboards: List[StoryboardItem] = Field(..., description="分镜列表")


class TaskController:
    """任务控制器"""
    
    @staticmethod
    @router.post("/tasks/script", response_model=TaskResponse)
    async def generate_script(
        background_tasks: BackgroundTasks,
        request: Request,
        body: ScriptGenerateRequest,
        db: Session = Depends(get_db)
    ):
        """生成视频剧本（原始接口）"""
        return await TaskController._generate_script_implementation(
            background_tasks, request, body, db
        )
    
    @staticmethod
    @router.post("/tasks/create-and-generate", response_model=ScriptGenerateResponse)
    async def create_and_generate_script(
        request: Request,
        body: dict,
        db: Session = Depends(get_db)
    ):
        """
        创建任务并同步生成剧本
        
        Args:
            request: FastAPI请求对象
            body: 请求体（兼容前端格式）
            db: 数据库会话
            
        Returns:
            ScriptGenerateResponse: 包含任务ID和生成的剧本内容
        """
        from app.services.template_service import TemplateService
        from app.services.llm_service import llm_service
        from app.services.task_service import TaskService
        from app.models.task_model import TaskStatus
        from fastapi import status
        from app.services.llm_model_service import LLMModelService
        
        task_id = utils.get_uuid()
        request_id = base_controller.get_task_id(request)
        
        try:
            # 转换前端请求格式
            video_idea = body.get("video_idea", "")
            template_id = body.get("template_id", None)
            style_id = body.get("style_id", None)
            duration = body.get("duration", 30)
            
            # 初始化服务
            template_service = TemplateService()
            llm_model_service = LLMModelService()
            
            # 1. 获取模板配置（必需）
            template = None
            if template_id:
                template = template_service.get_template_by_id(db, template_id)
                if not template:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"模板ID {template_id} 不存在或已停用"
                    )
                logger.info(f"模板加载成功: {template_id}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="模板ID不能为空"
                )
            
            # 2. 创建任务
            task_create = TaskCreate(
                video_idea=video_idea,
                template_id=template_id,
                style_id=style_id,
                aspect_ratio="16:9",  # 默认16:9
                duration=duration,
                operator="system"
            )
            
            # 保存任务到数据库
            db_task = TaskService.create_task(db, task_create)
            
            # 3. 获取默认的文档类型大模型配置
            default_text_model = llm_model_service.get_default_text_model(db)
            if not default_text_model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="未找到默认的文本类型大模型，请联系管理员配置"
                )
            logger.info(f"使用默认文本模型: {default_text_model.model_name}")
            
            # 4. 构建生成剧本的提示词
            prompt = template.script_prompt
            prompt += f"\n视频创意：'{video_idea}'"
            if duration:
                prompt += f"\n视频时长约为 {duration} 秒。"
            if style_id:
                prompt += f"\n使用风格ID: {style_id}。"
            
            # 5. 调用模型生成剧本
            logger.info(f"开始同步生成剧本，任务ID: {task_id}")
            try:
                # 使用llm_service的generate_text方法同步生成剧本
                video_script = llm_service.generate_text(
                    prompt=prompt,
                    provider=default_text_model.model_provider,
                    model_name=default_text_model.model_name,
                    base_url=default_text_model.base_url,
                    api_key=default_text_model.api_key,
                    stream=False  # 非流式生成
                )
                logger.success(f"剧本同步生成成功，任务ID: {task_id}")
            except Exception as e:
                logger.error(f"剧本生成失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"剧本生成失败: {str(e)}"
                )
            
            # 6. 更新任务剧本字段
            TaskService.save_script_to_task(db, db_task.id, video_script)
            TaskService.update_task_status(db, db_task.id, TaskStatus.SCRIPT_COMPLETED)
            logger.info(f"任务剧本字段更新成功，数据库任务ID: {db_task.id}")
            
            # 7. 更新状态服务中的任务信息
            state_service.state.update_task(
                task_id, 
                db_task_id=db_task.id,
                script=video_script,
                state="completed",
                progress=100
            )
            
            # 8. 返回任务ID和生成的剧本内容
            return ScriptGenerateResponse(
                task_id=task_id,
                script=video_script
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # 记录详细错误信息
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"创建并生成剧本时发生错误: {str(e)}")
            logger.error(f"错误堆栈: {error_trace}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"创建并生成剧本失败: {str(e)}"
            )
    
    @staticmethod
    async def _generate_script_implementation(
        background_tasks: BackgroundTasks,
        request: Request,
        body: ScriptGenerateRequest,
        db: Session = Depends(get_db)
    ):
        """
        生成视频剧本
        
        Args:
            background_tasks: 后台任务
            request: FastAPI请求对象
            body: 剧本生成请求参数
            db: 数据库会话
            
        Returns:
            TaskResponse: 包含任务ID的响应
        """
        from app.services.template_service import TemplateService
        from app.services.llm_model_service import LLMModelService
        from fastapi import status
        
        task_id = utils.get_uuid()
        request_id = base_controller.get_task_id(request)
        
        try:
            # 初始化服务
            template_service = TemplateService()
            llm_model_service = LLMModelService()
            
            # 1. 获取模板配置
            template = template_service.get_template_by_id(db, body.template_id)
            if body.template_id and not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"模板ID {body.template_id} 不存在或已停用"
                )
            
            # 2. 获取默认文本类型大模型配置
            default_text_model = llm_model_service.get_default_text_model(db)
            if not default_text_model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="未找到默认的文本类型大模型，请联系管理员配置"
                )
            
            # 构建视频参数
            params = VideoParams(
                video_subject=body.video_subject,
                video_style=body.style_id,  # 使用style_id作为video_style
                video_language=body.video_language,
                paragraph_number=body.paragraph_number
            )
            
            # 3. 使用TaskService创建数据库任务记录
            task_create = TaskCreate(
                video_idea=body.video_subject,
                template_id=body.template_id,
                style_id=body.style_id,
                aspect_ratio="16:9",  # 默认16:9
                duration=body.duration,
                operator="system"  # 可以从request中获取实际的操作用户
            )
            
            # 通过服务层创建任务，内部会处理状态设置和字段映射
            db_task = TaskService.create_task(db, task_create)
            
            task = {
                "task_id": task_id,
                "request_id": request_id,
                "params": {}
            }
            # 只添加必要的字段，避免序列化问题
            task["params"]["video_subject"] = body.video_subject
            task["template_id"] = body.template_id
            task["style_id"] = body.style_id
            task["duration"] = body.duration
            task["db_task_id"] = db_task.id  # 关联数据库任务ID
            
            # 更新任务状态
            state_service.state.update_task(task_id)
            
            # 将任务添加到后台执行
            background_tasks.add_task(
                task_service.start,
                task_id=task_id,
                params=params,
                stop_at="script",
                db=db,
                db_task_id=db_task.id,
                llm_model=default_text_model
            )
            
            logger.success(f"剧本生成任务创建成功，任务ID: {task_id}，数据库任务ID: {db_task.id}")
            return utils.get_response(200, task)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"{request_id}: {str(e)}"
            )
        except Exception as e:
            # 记录详细错误信息，包括完整堆栈
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"创建剧本生成任务时发生错误: {str(e)}")
            logger.error(f"错误堆栈: {error_trace}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"创建任务失败: {str(e)}"
            )
    
    @staticmethod
    @router.put("/tasks/{task_id}/script")
    async def update_script(task_id: str, request: ScriptUpdateRequest):
        """
        更新剧本内容
        
        Args:
            task_id: 任务ID
            request: 剧本更新请求参数
            
        Returns:
            dict: 操作结果
        """
        try:
            logger.info(f"更新剧本，任务ID: {task_id}")
            
            # 检查任务是否存在
            task = state_service.state.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 更新任务状态中的剧本
            state_service.state.update_task(task_id, script=request.script)
            
            # 保存剧本到文件
            from app.utils import utils
            import os
            import json
            
            script_file = os.path.join(utils.task_dir(task_id), "script.json")
            script_data = {
                "script": request.script,
                "search_terms": [],
                "params": task.get("params", {})
            }
            
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(script_data, ensure_ascii=False, indent=2))
            
            logger.success(f"剧本更新成功，任务ID: {task_id}")
            
            return {"status": "success", "message": "剧本更新成功"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新剧本时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"更新剧本失败: {str(e)}")
    
    @staticmethod
    @router.get("/tasks/{task_id}")
    def get_task_status(task_id: str):
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 任务状态信息，格式为 {"data": task_data}
        """
        try:
            logger.info(f"获取任务状态，任务ID: {task_id}")
            
            # 获取任务状态
            task = state_service.state.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 按照统一格式返回数据
            return utils.get_response(200, task)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取任务状态时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")
    
    @staticmethod
    @router.post("/tasks/{task_id}/storyboards")
    def save_storyboards(task_id: str, request: StoryboardUpdateRequest):
        """
        保存分镜数据
        
        Args:
            task_id: 任务ID
            request: 分镜更新请求参数
            
        Returns:
            dict: 操作结果
        """
        try:
            logger.info(f"保存分镜数据，任务ID: {task_id}")
            
            # 检查任务是否存在
            task = state_service.state.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 准备更新数据
            update_data = {
                "storyboards": [item.model_dump() for item in request.storyboards],
                "step": "storyboard",
                "updated_at": time.time()
            }
            
            # 更新任务状态
            state_service.state.update_task(task_id, **update_data)
            
            # 保存分镜到文件
            import json
            storyboard_file = os.path.join(utils.task_dir(task_id), "storyboards.json")
            with open(storyboard_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(update_data, ensure_ascii=False, indent=2))
            
            logger.success(f"分镜保存成功，任务ID: {task_id}")
            return utils.get_response(200, {"message": "分镜保存成功"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"保存分镜数据失败: {str(e)}")
            raise HTTPException(status_code=500, detail="保存分镜失败")

    @staticmethod
    @router.put("/tasks/{task_id}/design")
    def update_design(task_id: str, request: DesignUpdateRequest):
        """
        保存角色场景设计
        
        Args:
            task_id: 任务ID
            request: 设计更新请求参数
            
        Returns:
            dict: 操作结果
        """
        try:
            logger.info(f"保存角色场景设计，任务ID: {task_id}")
            
            # 检查任务是否存在
            task = state_service.state.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 验证输入数据
            if not request.characters or not request.scenes:
                raise HTTPException(status_code=400, detail="角色和场景不能为空")
            
            # 检查角色名称是否为空
            if any(not char.name.strip() for char in request.characters):
                raise HTTPException(status_code=400, detail="角色名称不能为空")
            
            # 检查场景名称是否为空
            if any(not scene.name.strip() for scene in request.scenes):
                raise HTTPException(status_code=400, detail="场景名称不能为空")
            
            # 准备更新数据
            update_data = {
                "characters": [char.model_dump() for char in request.characters],
                "scenes": [scene.model_dump() for scene in request.scenes],
                "bgm_type": request.bgm_type,
                "step": "character_scene_design"
            }
            
            # 更新任务状态
            state_service.state.update_task(task_id, **update_data)
            
            # 保存设计到文件
            design_file = os.path.join(utils.task_dir(task_id), "design.json")
            with open(design_file, "w", encoding="utf-8") as f:
                import json
                f.write(json.dumps(update_data, ensure_ascii=False, indent=2))
            
            logger.success(f"角色场景设计保存成功，任务ID: {task_id}")
            return utils.get_response(200, {"message": "角色场景设计保存成功"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"保存角色场景设计失败: {str(e)}")
            raise HTTPException(status_code=500, detail="保存设计失败")

    @staticmethod
    @router.post("/tasks/{task_id}/bgm")
    async def upload_bgm(task_id: str, file: UploadFile = File(...)):
        """
        上传背景音乐
        
        Args:
            task_id: 任务ID
            file: 背景音乐文件
            
        Returns:
            dict: 操作结果
        """
        try:
            logger.info(f"上传背景音乐，任务ID: {task_id}")
            
            # 检查任务是否存在
            task = state_service.state.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 获取文件信息
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            # 验证文件大小
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            # 使用bgm_service验证文件
            is_valid, error_msg = bgm_service.validate_bgm_file(file_ext, file_size)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # 读取文件内容
            content = await file.read()
            
            # 使用bgm_service保存文件
            file_path = bgm_service.save_bgm_file(task_id, content, file_ext)
            
            # 更新任务数据
            update_data = {
                "bgm_file": file_path,
                "bgm_filename": file.filename,
                "step": "character_scene_design"
            }
            state_service.state.update_task(task_id, **update_data)
            
            logger.success(f"背景音乐上传成功，任务ID: {task_id}")
            return utils.get_response(200, {
                "message": "背景音乐上传成功", 
                "file_path": file_path,
                "filename": file.filename,
                "size": file_size
            })
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"上传背景音乐失败: {str(e)}")
            raise HTTPException(status_code=500, detail="上传失败")
            
    @staticmethod
    @router.delete("/tasks/{task_id}/bgm")
    def delete_bgm(task_id: str):
        """
        删除任务的背景音乐文件
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 操作结果
        """
        try:
            logger.info(f"删除背景音乐，任务ID: {task_id}")
            
            # 检查任务是否存在
            task = state_service.state.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 使用bgm_service删除文件
            success = bgm_service.delete_bgm_file(task_id)
            
            if not success:
                raise HTTPException(status_code=500, detail="删除背景音乐失败")
            
            # 更新任务数据
            update_data = {
                "bgm_file": None,
                "bgm_filename": None
            }
            state_service.state.update_task(task_id, **update_data)
            
            logger.success(f"背景音乐删除成功，任务ID: {task_id}")
            return utils.get_response(200, {"message": "背景音乐删除成功"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除背景音乐失败: {str(e)}")
            raise HTTPException(status_code=500, detail="删除失败")
            
    @staticmethod
    @router.get("/bgm/types")
    def get_bgm_types():
        """
        获取系统预设的背景音乐类型列表
        
        Returns:
            dict: 背景音乐类型列表
        """
        try:
            logger.info("获取预设背景音乐类型")
            bgm_types = bgm_service.get_preset_bgm_types()
            return utils.get_response(200, {"types": bgm_types})
        except Exception as e:
            logger.error(f"获取背景音乐类型失败: {str(e)}")
            raise HTTPException(status_code=500, detail="获取失败")
    
    @staticmethod
    @router.get("/{task_id}/progress")
    def get_task_progress(task_id: str):
        """
        获取任务进度
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 任务进度信息
        """
        try:
            logger.info(f"获取任务进度，任务ID: {task_id}")
            
            # 验证任务是否存在
            task_data = state_service.state.get_task(task_id)
            if not task_data:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 构建进度信息
            progress = {
                "script_completed": bool(task_data.get('script')),
                "character_scene_completed": bool(task_data.get('characters')) and bool(task_data.get('scenes')),
                "storyboard_completed": bool(task_data.get('storyboards')),
                "model_completed": bool(task_data.get('models')),
                "content_generated": bool(task_data.get('generated_content')),
                "video_synthesized": bool(task_data.get('final_video'))
            }
            
            return utils.get_response(200, {"progress": progress})
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取任务进度失败: {str(e)}")
            raise HTTPException(status_code=500, detail="获取失败")
    
    @staticmethod
    @router.post("/script/storyboard")
    def generate_storyboards(script: str, characters: List[dict], scenes: List[dict]):
        """
        根据剧本内容自动生成分镜
        
        Args:
            script: 剧本内容
            characters: 角色列表
            scenes: 场景列表
            
        Returns:
            生成的分镜列表
        """
        try:
            logger.info(f"开始生成分镜，角色数量: {len(characters)}, 场景数量: {len(scenes)}")
            
            # 将剧本按段落分割
            paragraphs = [p.strip() for p in script.split('\n') if p.strip()]
            generated_storyboards = []
            
            # 为每个场景找到相关的段落
            for scene in scenes:
                scene_name = scene.get('name', '')
                if not scene_name:
                    continue
                    
                # 查找包含场景名的段落
                scene_paragraphs = []
                start_index = -1
                
                for i, paragraph in enumerate(paragraphs):
                    # 检查段落是否包含场景名或场景描述关键词
                    if scene_name in paragraph or any(keyword in paragraph.lower() for keyword in ['场景', '地点', '环境', '背景']):
                        if start_index == -1:
                            start_index = i
                        scene_paragraphs.append(paragraph)
                    elif start_index != -1 and len(scene_paragraphs) > 0:
                        # 如果已经找到了场景的起始，但当前段落不再相关，则结束当前场景的段落收集
                        # 但我们需要确保收集足够的内容
                        if len(scene_paragraphs) >= 2:
                            break
                        scene_paragraphs.append(paragraph)
                
                # 如果没有找到明确的场景段落关联，就分配一些通用段落
                if not scene_paragraphs and start_index == -1 and generated_storyboards == []:
                    # 为第一个场景分配前2-3个段落
                    scene_paragraphs = paragraphs[:min(3, len(paragraphs))]
                elif not scene_paragraphs:
                    # 为其他场景分配后续的段落
                    prev_end = sum(len(sb.get('actions', '').split(' ')) for sb in generated_storyboards)
                    # 尝试找到合适的段落继续点
                    if prev_end < len(paragraphs):
                        scene_paragraphs = paragraphs[prev_end:prev_end+2]
                
                # 为找到的场景段落生成分镜
                if scene_paragraphs:
                    # 每1-2个段落生成一个分镜
                    for i in range(0, len(scene_paragraphs), 1 + (i % 2)):
                        segment_paragraphs = scene_paragraphs[i:i+2]
                        actions_text = ' '.join(segment_paragraphs)
                        
                        # 识别角色
                        scene_characters = []
                        for char in characters:
                            char_name = char.get('name', '')
                            if char_name and any(char_name in p for p in segment_paragraphs):
                                scene_characters.append(char_name)
                        
                        # 简单的描述生成
                        description = f"{scene_name}场景中的画面"
                        if scene_characters:
                            description += f"，包含角色: {', '.join(scene_characters)}"
                        
                        # 随机选择一个效果，但保持一些分镜没有效果
                        effect_index = i % (len(EFFECT_TEMPLATES) * 2) // 2
                        effect = EFFECT_TEMPLATES[effect_index]
                        
                        # 生成分镜
                        storyboard = {
                            "scene": scene_name,
                            "characters": scene_characters,
                            "actions": actions_text[:200] + ('...' if len(actions_text) > 200 else ''),
                            "duration": 5 + (i % 6),  # 5-10秒随机
                            "description": description,
                            "effects": effect
                        }
                        generated_storyboards.append(storyboard)
            
            # 如果还没有生成分镜（可能是没有明确的场景关联），则使用回退策略
            if not generated_storyboards and paragraphs:
                # 每2-3个段落生成一个分镜
                for i in range(0, len(paragraphs), 2 + (i % 2)):
                    segment_paragraphs = paragraphs[i:i+3]
                    actions_text = ' '.join(segment_paragraphs)
                    
                    # 识别角色
                    scene_characters = []
                    for char in characters:
                        char_name = char.get('name', '')
                        if char_name and any(char_name in p for p in segment_paragraphs):
                            scene_characters.append(char_name)
                    
                    # 选择一个场景（如果有）
                    scene_name = scenes[0].get('name', '默认场景') if scenes else '默认场景'
                    
                    # 生成分镜
                    storyboard = {
                        "scene": scene_name,
                        "characters": scene_characters,
                        "actions": actions_text[:200] + ('...' if len(actions_text) > 200 else ''),
                        "duration": 6 + (i % 5),  # 6-10秒随机
                        "description": f"基于剧本生成的画面 {i//3 + 1}",
                        "effects": EFFECT_TEMPLATES[i % len(EFFECT_TEMPLATES)]
                    }
                    generated_storyboards.append(storyboard)
            
            logger.info(f"分镜生成完成，共生成 {len(generated_storyboards)} 个分镜")
            
            return utils.get_response(200, {"storyboards": generated_storyboards})
        
        except Exception as e:
            logger.error(f"生成分镜时出错: {str(e)}")
            raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


# 确保控制器被正确注册
__all__ = ["TaskController"]