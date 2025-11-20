import os
import shutil
from typing import Optional, Dict, Any, Tuple
import logging

from app.config import config
from app.utils import utils

logger = logging.getLogger(__name__)

class BgmService:
    """
    背景音乐管理服务
    负责处理背景音乐的上传、保存、预览和删除等操作
    """
    
    def __init__(self):
        """
        初始化背景音乐服务
        """
        # 背景音乐存储根目录
        # 使用storage目录作为基础路径
        storage_dir = utils.storage_dir()
        self.bgm_root_dir = os.path.join(storage_dir, "bgm")
        # 确保目录存在
        os.makedirs(self.bgm_root_dir, exist_ok=True)
        
        # 预设背景音乐类型
        self.preset_bgm_types = {
            "none": {"name": "无背景音乐", "description": "不使用背景音乐"},
            "upbeat": {"name": "欢快", "description": "充满活力的欢快音乐"},
            "dramatic": {"name": "戏剧性", "description": "有张力的戏剧性音乐"},
            "emotional": {"name": "情感", "description": "温柔抒情的音乐"},
            "relaxing": {"name": "轻松", "description": "舒缓放松的音乐"}
        }
    
    def get_task_bgm_dir(self, task_id: str) -> str:
        """
        获取任务的背景音乐目录
        
        Args:
            task_id: 任务ID
            
        Returns:
            str: 背景音乐目录路径
        """
        task_bgm_dir = os.path.join(self.bgm_root_dir, task_id)
        os.makedirs(task_bgm_dir, exist_ok=True)
        return task_bgm_dir
    
    def save_bgm_file(self, task_id: str, file_content: bytes, file_ext: str) -> str:
        """
        保存背景音乐文件
        
        Args:
            task_id: 任务ID
            file_content: 文件内容
            file_ext: 文件扩展名
            
        Returns:
            str: 保存后的文件路径
        """
        try:
            # 获取任务背景音乐目录
            task_bgm_dir = self.get_task_bgm_dir(task_id)
            
            # 生成唯一文件名
            file_name = f"bgm_{utils.get_uuid()}{file_ext}"
            file_path = os.path.join(task_bgm_dir, file_name)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"背景音乐文件保存成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存背景音乐文件失败: {str(e)}")
            raise
    
    def get_bgm_file_path(self, task_id: str) -> Optional[str]:
        """
        获取任务的背景音乐文件路径
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[str]: 背景音乐文件路径，如果不存在返回None
        """
        task_bgm_dir = self.get_task_bgm_dir(task_id)
        
        # 检查常见的音频文件格式
        for ext in [".mp3", ".wav", ".ogg"]:
            file_path = os.path.join(task_bgm_dir, f"bgm{ext}")
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def delete_bgm_file(self, task_id: str) -> bool:
        """
        删除任务的背景音乐文件
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            task_bgm_dir = self.get_task_bgm_dir(task_id)
            
            # 删除整个目录
            if os.path.exists(task_bgm_dir):
                shutil.rmtree(task_bgm_dir)
                logger.info(f"背景音乐目录删除成功: {task_bgm_dir}")
            
            return True
        except Exception as e:
            logger.error(f"删除背景音乐文件失败: {str(e)}")
            return False
    
    def get_preset_bgm_types(self) -> Dict[str, Dict[str, str]]:
        """
        获取预设的背景音乐类型
        
        Returns:
            Dict[str, Dict[str, str]]: 预设背景音乐类型字典
        """
        return self.preset_bgm_types
    
    def validate_bgm_file(self, file_ext: str, file_size: int) -> Tuple[bool, str]:
        """
        验证背景音乐文件
        
        Args:
            file_ext: 文件扩展名
            file_size: 文件大小（字节）
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        # 验证文件类型
        allowed_extensions = ['.mp3', '.wav', '.ogg']
        if file_ext.lower() not in allowed_extensions:
            return False, f"只支持{', '.join(allowed_extensions)}格式的音频文件"
        
        # 验证文件大小（最大50MB）
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            return False, f"文件大小不能超过{max_size // (1024 * 1024)}MB"
        
        return True, ""
    
    def get_bgm_info(self, task_id: str) -> Dict[str, Any]:
        """
        获取背景音乐信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 背景音乐信息
        """
        file_path = self.get_bgm_file_path(task_id)
        
        if not file_path:
            return {
                "exists": False,
                "path": None,
                "filename": None,
                "size": 0
            }
        
        try:
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 获取文件名
            filename = os.path.basename(file_path)
            
            return {
                "exists": True,
                "path": file_path,
                "filename": filename,
                "size": file_size
            }
        except Exception as e:
            logger.error(f"获取背景音乐信息失败: {str(e)}")
            return {
                "exists": False,
                "path": None,
                "filename": None,
                "size": 0
            }

# 创建背景音乐服务实例
bgm_service = BgmService()