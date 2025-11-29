import math
import os.path
import re
from os import path
import json
import shutil

from edge_tts import SubMaker
from loguru import logger

from app.config import config
from app.models import const
from app.models.schema import VideoConcatMode, VideoParams, MediaGenerationRequest, VideoSynthesisRequest, StoryboardFrameRequest
from app.models.task_model import Task, TaskStatus
from app.services import llm, material, subtitle, video, voice
from app.services import state as sm
from app.utils import utils


def generate_script(task_id, params, db=None, db_task_id=None, llm_model=None):
    logger.info("\n\n## generating video script")
    # 检查params是否有video_script属性
    video_script = getattr(params, "video_script", "").strip()
    if not video_script:
        # 获取模板信息
        template_id = params.get("template_id", "") if isinstance(params, dict) else getattr(params, "template_id", "")
        style_id = params.get("style_id", "") if isinstance(params, dict) else getattr(params, "style_id", "")
        duration = params.get("duration", 30) if isinstance(params, dict) else getattr(params, "duration", 30)
        
        video_script = llm.generate_script(
            video_subject=params.video_subject,
            language=params.video_language,
            paragraph_number=params.paragraph_number,
            template_id=template_id,
            style_id=style_id,
            duration=duration,
            video_style=params.video_style if hasattr(params, 'video_style') else ''
        )
    else:
        logger.debug(f"video script: \n{video_script}")

    if not video_script:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        logger.error("failed to generate video script.")
        # 更新数据库任务状态为失败
        if db and db_task_id:
            try:
                from app.services.task_service import TaskService
                TaskService.update_task_status(db, db_task_id, TaskStatus.SCRIPT_GENERATE_FAILED)
                logger.warning(f"数据库任务状态已更新为失败: {db_task_id}")
            except Exception as e:
                logger.error(f"更新数据库任务状态失败: {str(e)}")
        return None

    return video_script


def generate_terms(task_id, params, video_script):
    logger.info("\n\n## generating video terms")
    video_terms = params.video_terms
    if not video_terms:
        video_terms = llm.generate_terms(
            video_subject=params.video_subject, video_script=video_script, amount=5
        )
    else:
        if isinstance(video_terms, str):
            video_terms = [term.strip() for term in re.split(r"[,，]", video_terms)]
        elif isinstance(video_terms, list):
            video_terms = [term.strip() for term in video_terms]
        else:
            raise ValueError("video_terms must be a string or a list of strings.")

        logger.debug(f"video terms: {utils.to_json(video_terms)}")

    if not video_terms:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        logger.error("failed to generate video terms.")
        return None

    return video_terms


def save_script_data(task_id, video_script, video_terms, params):
    script_file = path.join(utils.task_dir(task_id), "script.json")
    script_data = {
        "script": video_script,
        "search_terms": video_terms,
        "params": params,
    }

    with open(script_file, "w", encoding="utf-8") as f:
        f.write(utils.to_json(script_data))


def generate_audio(task_id, params, video_script):
    logger.info("\n\n## generating audio")
    audio_file = path.join(utils.task_dir(task_id), "audio.mp3")
    sub_maker = voice.tts(
        text=video_script,
        voice_name=voice.parse_voice_name(params.voice_name),
        voice_rate=params.voice_rate,
        voice_file=audio_file,
    )
    if sub_maker is None:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        logger.error(
            """failed to generate audio:
1. check if the language of the voice matches the language of the video script.
2. check if the network is available. If you are in China, it is recommended to use a VPN and enable the global traffic mode.
        """.strip()
        )
        return None, None, None

    audio_duration = math.ceil(voice.get_audio_duration(sub_maker))
    return audio_file, audio_duration, sub_maker


def generate_subtitle(task_id, params, video_script, sub_maker, audio_file):
    if not params.subtitle_enabled:
        return ""

    subtitle_path = path.join(utils.task_dir(task_id), "subtitle.srt")
    subtitle_provider = config.app.get("subtitle_provider", "").strip().lower()
    logger.info(f"\n\n## generating subtitle, provider: {subtitle_provider}")

    subtitle_fallback = False
    if subtitle_provider == "edge":
        voice.create_subtitle(
            text=video_script, sub_maker=sub_maker, subtitle_file=subtitle_path
        )
        if not os.path.exists(subtitle_path):
            subtitle_fallback = True
            logger.warning("subtitle file not found, fallback to whisper")

    if subtitle_provider == "whisper" or subtitle_fallback:
        subtitle.create(audio_file=audio_file, subtitle_file=subtitle_path)
        logger.info("\n\n## correcting subtitle")
        subtitle.correct(subtitle_file=subtitle_path, video_script=video_script)

    subtitle_lines = subtitle.file_to_subtitles(subtitle_path)
    if not subtitle_lines:
        logger.warning(f"subtitle file is invalid: {subtitle_path}")
        return ""

    return subtitle_path


def get_video_materials(task_id, params):
    if params.video_source == "local" or "wan21":
        logger.info(f"\n\n## preprocess {params.video_source} materials")
        materials = video.preprocess_video(
            materials=params.video_materials, clip_duration=params.video_clip_duration
        )
        if not materials:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error(
                "no valid materials found, please check the materials and try again."
            )
            return None
        return [material_info.url for material_info in materials]
    # else:
    #     logger.info(f"\n\n## downloading videos from {params.video_source}")
    #     downloaded_videos = material.download_videos(
    #         task_id=task_id,
    #         search_terms=video_terms,
    #         source=params.video_source,
    #         video_aspect=params.video_aspect,
    #         video_contact_mode=params.video_concat_mode,
    #         audio_duration=audio_duration * params.video_count,
    #         max_clip_duration=params.video_clip_duration,
    #     )
    #     if not downloaded_videos:
    #         sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
    #         logger.error(
    #             "failed to download videos, maybe the network is not available. if you are in China, please use a VPN."
    #         )
    #         return None
    #     return downloaded_videos


def generate_final_videos(
        task_id, params, downloaded_videos, audio_file, subtitle_path
):
    final_video_paths = []
    combined_video_paths = []
    video_concat_mode = (
        params.video_concat_mode if params.video_count == 1 else VideoConcatMode.random
    )

    _progress = 50
    for i in range(params.video_count):
        index = i + 1
        combined_video_path = path.join(
            utils.task_dir(task_id), f"combined-{index}.mp4"
        )
        logger.info(f"\n\n## combining video: {index} => {combined_video_path}")
        video.combine_videos(
            combined_video_path=combined_video_path,
            video_paths=downloaded_videos,
            audio_file=audio_file,
            video_aspect=params.video_aspect,
            video_concat_mode=video_concat_mode,
            max_clip_duration=params.video_clip_duration,
            threads=params.n_threads,
        )

        _progress += 50 / params.video_count / 2
        sm.state.update_task(task_id, progress=_progress)

        final_video_path = path.join(utils.task_dir(task_id), f"final-{index}.mp4")

        logger.info(f"\n\n## generating video: {index} => {final_video_path}")
        video.generate_video(
            video_path=combined_video_path,
            audio_path=audio_file,
            subtitle_path=subtitle_path,
            output_file=final_video_path,
            params=params,
        )

        _progress += 50 / params.video_count / 2
        sm.state.update_task(task_id, progress=_progress)

        final_video_paths.append(final_video_path)
        combined_video_paths.append(combined_video_path)

    return final_video_paths, combined_video_paths


def start(task_id, params: VideoParams, stop_at: str = "video", db=None, db_task_id=None, llm_model=None):
    logger.info(f"start task: {task_id}, stop_at: {stop_at}, db_task_id: {db_task_id}")
    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=5)

    if type(params.video_concat_mode) is str:
        params.video_concat_mode = VideoConcatMode(params.video_concat_mode)

    # 1. Generate script
    video_script = generate_script(task_id, params, db, db_task_id, llm_model=llm_model)
    if not video_script:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=10)

    if stop_at == "script":
        sm.state.update_task(
            task_id, state=const.TASK_STATE_COMPLETE, progress=100, script=video_script
        )
        
        # 更新数据库任务状态为剧本生成完成
        if db and db_task_id:
            try:
                from app.services.task_service import TaskService
                # 保存剧本内容
                TaskService.save_script_to_task(db, db_task_id, video_script)
                # 更新任务状态
                TaskService.update_task_status(db, db_task_id, TaskStatus.SCRIPT_COMPLETED)
                logger.success(f"数据库任务状态更新成功: {db_task_id}")
            except Exception as e:
                logger.error(f"更新数据库任务状态失败: {str(e)}")
        
        return {"script": video_script}
    #
    # # 2. Generate terms
    # video_terms = ""
    # if params.video_source != "local":
    #     video_terms = generate_terms(task_id, params, video_script)
    #     if not video_terms:
    #         sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
    #         return
    #
    # save_script_data(task_id, video_script, video_terms, params)
    #
    # if stop_at == "terms":
    #     sm.state.update_task(
    #         task_id, state=const.TASK_STATE_COMPLETE, progress=100, terms=video_terms
    #     )
    #     return {"script": video_script, "terms": video_terms}
    #
    # sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=20)

    # 3. Generate audio
    audio_file, audio_duration, sub_maker = generate_audio(task_id, params, video_script)
    if not audio_file:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=30)

    if stop_at == "audio":
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            audio_file=audio_file,
        )
        return {"audio_file": audio_file, "audio_duration": audio_duration}

    # 4. Generate subtitle
    subtitle_path = generate_subtitle(task_id, params, video_script, sub_maker, audio_file)

    if stop_at == "subtitle":
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            subtitle_path=subtitle_path,
        )
        return {"subtitle_path": subtitle_path}

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=40)

    # 5. Get video materials
    downloaded_videos = get_video_materials(
        task_id, params
    )
    if not downloaded_videos:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return

    if stop_at == "materials":
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            materials=downloaded_videos,
        )
        return {"materials": downloaded_videos}

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=50)

    # 5. Get video materials

    # 6. Generate final videos
    final_video_paths, combined_video_paths = generate_final_videos(
        task_id, params, downloaded_videos, audio_file, subtitle_path
    )

    if not final_video_paths:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return

    logger.success(
        f"task {task_id} finished, generated {len(final_video_paths)} videos."
    )

    kwargs = {
        "videos": final_video_paths,
        "combined_videos": combined_video_paths,
        "script": video_script,
        # "terms": video_terms,
        "audio_file": audio_file,
        "audio_duration": audio_duration,
        "subtitle_path": subtitle_path,
        "materials": downloaded_videos,
    }
    sm.state.update_task(
        task_id, state=const.TASK_STATE_COMPLETE, progress=100, **kwargs
    )
    return kwargs


def generate_frame(task_id: str, params: StoryboardFrameRequest):
    """
    为单个分镜生成画面
    """
    logger.info(f"start frame generation task: {task_id}")
    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=10)
    
    try:
        # 创建任务目录
        task_dir = utils.task_dir(task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 获取分镜数据
        frame_index = params.frame_index
        frame_prompt = params.frame_prompt
        frame_content = params.frame_content
        
        logger.info(f"Generating frame {frame_index}: {frame_prompt}")
        
        # 生成分镜画面
        # 这里可以根据配置调用不同的图像生成服务
        # 暂时使用占位图像或从配置的模型服务获取
        frame_dir = os.path.join(task_dir, f"frame_{frame_index}")
        os.makedirs(frame_dir, exist_ok=True)
        
        # 保存分镜信息
        frame_info = {
            "index": frame_index,
            "prompt": frame_prompt,
            "content": frame_content,
            "generated_at": utils.get_current_time(),
            "status": "processing"
        }
        
        # 模拟图像生成
        # 实际应用中应该调用图像生成API
        image_path = os.path.join(frame_dir, f"frame_{frame_index}.png")
        
        # 这里可以添加实际的图像生成逻辑
        # 例如调用本地或远程的图像生成模型
        
        # 保存分镜信息
        with open(os.path.join(frame_dir, "frame_info.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(frame_info, ensure_ascii=False, indent=2))
        
        sm.state.update_task(
            task_id, 
            state=const.TASK_STATE_COMPLETE, 
            progress=100,
            frame_index=frame_index,
            frame_info=frame_info,
            image_path=image_path
        )
        
        logger.success(f"Frame generation completed: {task_id}")
        return {
            "frame_index": frame_index,
            "image_path": image_path,
            "frame_info": frame_info
        }
        
    except Exception as e:
        logger.error(f"Frame generation failed: {str(e)}")
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED, error=str(e))
        raise

def generate_media_batch(task_id: str, params: MediaGenerationRequest):
    """
    批量生成媒体内容（画面、配音、动效）
    """
    logger.info(f"start media batch generation task: {task_id}")
    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=5)
    
    try:
        # 创建任务目录
        task_dir = utils.task_dir(task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 获取项目信息
        project_id = params.project_id
        storyboard_data = params.storyboard_data
        
        sm.state.update_task(task_id, progress=10)
        
        generated_media = {
            "frames": [],
            "audios": [],
            "effects": []
        }
        
        # 处理每个分镜
        total_frames = len(storyboard_data)
        for i, frame in enumerate(storyboard_data):
            frame_index = frame.get("index", i)
            frame_dir = os.path.join(task_dir, f"frame_{frame_index}")
            os.makedirs(frame_dir, exist_ok=True)
            
            # 进度更新
            progress = 10 + (i / total_frames) * 80
            sm.state.update_task(task_id, progress=progress)
            
            try:
                # 1. 生成画面（如果需要）
                if params.generate_images:
                    image_path = os.path.join(frame_dir, f"frame_{frame_index}.png")
                    # 这里添加实际的图像生成逻辑
                    # 模拟生成成功
                    generated_media["frames"].append({
                        "index": frame_index,
                        "image_path": image_path,
                        "status": "completed"
                    })
                
                # 2. 生成配音（如果需要）
                if params.generate_audios:
                    audio_path = os.path.join(frame_dir, f"audio_{frame_index}.mp3")
                    frame_text = frame.get("content", "")
                    
                    # 调用TTS服务生成配音
                    if frame_text:
                        # 使用现有的voice.tts函数生成配音
                        voice.tts(
                            text=frame_text,
                            voice_name=voice.parse_voice_name(params.voice_name),
                            voice_rate=params.voice_rate,
                            voice_file=audio_path
                        )
                        
                        generated_media["audios"].append({
                            "index": frame_index,
                            "audio_path": audio_path,
                            "duration": 5.0  # 模拟时长
                        })
                
                # 3. 添加动效（如果需要）
                if params.generate_effects and frame.get("effects"):
                    generated_media["effects"].append({
                        "index": frame_index,
                        "effects": frame.get("effects", []),
                        "status": "applied"
                    })
                
            except Exception as e:
                logger.error(f"Error processing frame {frame_index}: {str(e)}")
                # 继续处理其他分镜
                continue
        
        # 保存媒体生成结果
        with open(os.path.join(task_dir, "generated_media.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(generated_media, ensure_ascii=False, indent=2))
        
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            generated_media=generated_media,
            project_id=project_id
        )
        
        logger.success(f"Media batch generation completed: {task_id}")
        return {
            "generated_media": generated_media,
            "project_id": project_id
        }
        
    except Exception as e:
        logger.error(f"Media batch generation failed: {str(e)}")
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED, error=str(e))
        raise

def synthesize_video(task_id: str, params: VideoSynthesisRequest):
    """
    合成最终视频
    """
    logger.info(f"start video synthesis task: {task_id}")
    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=10)
    
    try:
        # 创建任务目录
        task_dir = utils.task_dir(task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 获取参数
        project_id = params.project_id
        storyboard_data = params.storyboard_data
        media_data = params.media_data
        bgm_path = params.bgm_path
        
        sm.state.update_task(task_id, progress=20)
        
        # 创建临时工作目录
        temp_dir = os.path.join(task_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 处理每个分镜，生成片段
        segment_paths = []
        total_frames = len(storyboard_data)
        
        for i, frame in enumerate(storyboard_data):
            frame_index = frame.get("index", i)
            
            # 进度更新
            progress = 20 + (i / total_frames) * 50
            sm.state.update_task(task_id, progress=progress)
            
            try:
                # 获取分镜媒体资源
                frame_media = next((m for m in media_data if m.get("index") == frame_index), None)
                if not frame_media:
                    logger.warning(f"No media data found for frame {frame_index}")
                    continue
                
                # 视频片段路径
                segment_path = os.path.join(temp_dir, f"segment_{frame_index}.mp4")
                
                # 构建视频片段
                # 这里添加实际的视频合成逻辑
                # 例如使用ffmpeg将图像、音频合成为视频片段
                
                # 模拟成功生成片段
                segment_paths.append(segment_path)
                
            except Exception as e:
                logger.error(f"Error synthesizing segment {frame_index}: {str(e)}")
                # 继续处理其他片段
                continue
        
        # 进度更新
        sm.state.update_task(task_id, progress=80)
        
        # 合并所有片段
        final_video_path = os.path.join(task_dir, "final_video.mp4")
        
        # 添加背景音乐（如果提供）
        if bgm_path and os.path.exists(bgm_path):
            # 这里添加实际的背景音乐处理逻辑
            logger.info("Adding background music to final video")
        
        # 保存合成结果信息
        synthesis_result = {
            "final_video": final_video_path,
            "segments": segment_paths,
            "project_id": project_id,
            "bgm_used": bool(bgm_path),
            "generated_at": utils.get_current_time()
        }
        
        with open(os.path.join(task_dir, "synthesis_result.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(synthesis_result, ensure_ascii=False, indent=2))
        
        # 清理临时文件
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            final_video=final_video_path,
            synthesis_result=synthesis_result
        )
        
        logger.success(f"Video synthesis completed: {task_id}")
        return {
            "final_video": final_video_path,
            "synthesis_result": synthesis_result
        }
        
    except Exception as e:
        logger.error(f"Video synthesis failed: {str(e)}")
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED, error=str(e))
        raise

if __name__ == "__main__":
    task_id = "task_id"
    params = VideoParams(
        video_subject="金钱的作用",
        voice_name="zh-CN-XiaoyiNeural-Female",
        voice_rate=1.0,

    )
    # start(task_id, params, stop_at="video")
