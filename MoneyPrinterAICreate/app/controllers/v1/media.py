from fastapi import APIRouter, Request, HTTPException
from typing import List, Optional
from app.controllers.v1.base import new_router
from app.models.schema import (
    StoryboardFrameRequest,
    MediaGenerationRequest,
    VideoSynthesisRequest
)
import app.utils as utils
import logging
import os
import asyncio
from app.services import state as sm
import time

logger = logging.getLogger(__name__)
router = new_router()


@router.post("/generate-frame")
async def generate_frame(
    request: Request,
    body: StoryboardFrameRequest
):
    """
    生成单个分镜画面
    """
    task_id = utils.get_uuid()
    request_id = utils.get_request_id(request)
    
    try:
        # 验证参数
        if not body.frame_id:
            raise ValueError("frame_id 不能为空")
        
        if not body.prompt:
            raise ValueError("prompt 不能为空")
        
        # 创建任务
        task_data = {
            "task_id": task_id,
            "request_id": request_id,
            "type": "generate_frame",
            "params": body.model_dump()
        }
        
        sm.state.update_task(task_id, status="processing")
        
        # 这里应该调用实际的图像处理服务
        # 为了演示，我们使用模拟数据
        # 实际实现中，应该调用模型服务生成图像
        
        # 模拟处理延迟
        await asyncio.sleep(2)
        
        # 模拟生成的图像URL
        image_url = f"/api/v1/media/placeholder-image/{task_id}"
        
        result = {
            "frame_id": body.frame_id,
            "image_url": image_url,
            "status": "success"
        }
        
        sm.state.update_task(task_id, status="completed", result=result)
        
        return utils.get_response(200, result)
        
    except Exception as e:
        logger.error(f"生成画面失败: {str(e)}")
        sm.state.update_task(task_id, status="failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/generate-batch")
async def generate_batch_media(
    request: Request,
    body: MediaGenerationRequest
):
    """
    批量生成媒体（画面和音频）
    """
    task_id = utils.get_uuid()
    request_id = utils.get_request_id(request)
    
    try:
        # 验证参数
        if not body.storyboard_id:
            raise ValueError("storyboard_id 不能为空")
        
        if not body.frames or len(body.frames) == 0:
            raise ValueError("frames 不能为空")
        
        # 创建任务
        task_data = {
            "task_id": task_id,
            "request_id": request_id,
            "type": "generate_batch_media",
            "params": body.model_dump()
        }
        
        sm.state.update_task(task_id, status="processing", progress=0)
        
        # 模拟批量处理
        total_frames = len(body.frames)
        results = []
        
        for i, frame in enumerate(body.frames):
            # 模拟处理每个帧
            await asyncio.sleep(0.5)
            
            # 模拟生成的媒体URL
            image_url = f"/api/v1/media/placeholder-image/{task_id}_{i}"
            audio_url = f"/api/v1/media/placeholder-audio/{task_id}_{i}"
            
            results.append({
                "frame_id": frame.frame_id,
                "image_url": image_url,
                "audio_url": audio_url,
                "status": "success"
            })
            
            # 更新进度
            progress = int((i + 1) / total_frames * 100)
            sm.state.update_task(task_id, progress=progress)
        
        # 创建预览视频URL
        preview_url = f"/api/v1/media/placeholder-video/{task_id}"
        
        final_result = {
            "storyboard_id": body.storyboard_id,
            "results": results,
            "preview_url": preview_url,
            "status": "completed"
        }
        
        sm.state.update_task(task_id, status="completed", result=final_result)
        
        return utils.get_response(200, final_result)
        
    except Exception as e:
        logger.error(f"批量生成媒体失败: {str(e)}")
        sm.state.update_task(task_id, status="failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/synthesize-video")
async def synthesize_video(
    request: Request,
    body: VideoSynthesisRequest
):
    """
    视频合成
    """
    task_id = utils.get_uuid()
    request_id = utils.get_request_id(request)
    
    try:
        # 验证参数
        if not body.storyboard_id:
            raise ValueError("storyboard_id 不能为空")
        
        # 创建任务
        task_data = {
            "task_id": task_id,
            "request_id": request_id,
            "type": "synthesize_video",
            "params": body.model_dump()
        }
        
        sm.state.update_task(task_id, status="processing", progress=0)
        
        # 添加到任务队列异步处理
        task_manager.add_task(
            _process_video_synthesis,
            task_id=task_id,
            params=body
        )
        
        result = {
            "task_id": task_id,
            "status": "processing",
            "message": "视频合成任务已创建，正在处理中"
        }
        
        return utils.get_response(200, result)
        
    except Exception as e:
        logger.error(f"创建视频合成任务失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


async def _process_video_synthesis(task_id: str, params: VideoSynthesisRequest):
    """
    处理视频合成的实际逻辑
    """
    try:
        # 模拟视频合成的各个阶段
        stages = [
            (20, "正在处理素材..."),
            (50, "正在合成视频..."),
            (80, "正在添加特效和音频..."),
            (95, "正在渲染最终视频...")
        ]
        
        for progress, message in stages:
            sm.state.update_task(task_id, progress=progress, message=message)
            # 模拟处理时间
            await asyncio.sleep(3)
        
        # 模拟生成的最终视频URL
        video_url = f"/api/v1/media/placeholder-video/{task_id}_final"
        
        result = {
            "storyboard_id": params.storyboard_id,
            "video_url": video_url,
            "status": "completed"
        }
        
        sm.state.update_task(task_id, status="completed", progress=100, result=result, message="视频生成完成！")
        
    except Exception as e:
        logger.error(f"视频合成失败: {str(e)}")
        sm.state.update_task(task_id, status="failed", error=str(e), message=str(e))


@router.get("/placeholder-image/{image_id}")
async def get_placeholder_image(image_id: str):
    """
    获取占位图片（用于测试）
    """
    # 在实际应用中，这里应该返回真实生成的图片
    # 这里为了演示，返回一个简单的HTML作为占位符
    html_content = f"""
    <html>
    <body>
        <div style="width: 800px; height: 450px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #666;">
            图片预览 - {image_id}
        </div>
    </body>
    </html>
    """
    return utils.get_response(200, html_content, content_type="text/html")


@router.get("/placeholder-audio/{audio_id}")
async def get_placeholder_audio(audio_id: str):
    """
    获取占位音频（用于测试）
    """
    # 在实际应用中，这里应该返回真实生成的音频
    # 这里为了演示，返回一个简单的响应
    return utils.get_response(200, {"message": f"音频预览 - {audio_id}"})


@router.get("/placeholder-video/{video_id}")
async def get_placeholder_video(video_id: str):
    """
    获取占位视频（用于测试）
    """
    # 在实际应用中，这里应该返回真实生成的视频
    # 这里为了演示，返回一个简单的HTML作为占位符
    html_content = f"""
    <html>
    <body>
        <div style="width: 800px; height: 450px; background: #000; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 24px;">
            视频预览 - {video_id}
        </div>
    </body>
    </html>
    """
    return utils.get_response(200, html_content, content_type="text/html")


@router.get("/bgm-list")
async def get_bgm_list(type: Optional[str] = None):
    """
    获取背景音乐列表
    """
    # 模拟背景音乐列表
    bgm_list = [
        {"id": "bgm1", "name": "轻松背景音乐1", "url": "/assets/music/bgm1.mp3", "type": "relax"},
        {"id": "bgm2", "name": "轻松背景音乐2", "url": "/assets/music/bgm2.mp3", "type": "relax"},
        {"id": "bgm3", "name": "欢快背景音乐1", "url": "/assets/music/bgm3.mp3", "type": "happy"},
        {"id": "bgm4", "name": "欢快背景音乐2", "url": "/assets/music/bgm4.mp3", "type": "happy"},
        {"id": "bgm5", "name": "专业背景音乐1", "url": "/assets/music/bgm5.mp3", "type": "professional"}
    ]
    
    # 如果指定了类型，进行过滤
    if type:
        bgm_list = [bgm for bgm in bgm_list if bgm["type"] == type]
    
    return utils.get_response(200, bgm_list)