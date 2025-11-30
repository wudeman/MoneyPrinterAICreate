"""即梦AI图生视频模型实现类"""

import json
import time
from typing import Dict, Any, Optional
from loguru import logger
from volcenginesdkcore import ApiClient, Configuration
from volcenginesdkveiapi.api import VEIAPIApi

from app.services.llm_engine.base import BaseLLM


class JianMengImg2VideoLLM(BaseLLM):
    """
    即梦AI图生视频模型实现类
    支持同步的视频生成
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化即梦AI图生视频模型实例
        
        Args:
            config: 模型配置参数，包含以下字段：
                - model_name: 模型名称，如"jimeng-video-gen-v3"
                - api_version: API版本
                - access_key_id: 火山引擎Access Key ID
                - secret_access_key: 火山引擎Secret Access Key
                - region: 区域标识
                - timeout: 请求超时时间
                - max_retries: 最大重试次数
        """
        super().__init__(config)
        
        # 即梦AI特有配置
        self.access_key_id = self.config.get('access_key_id')
        self.secret_access_key = self.config.get('secret_access_key')
        self.region = self.config.get('region', 'cn-beijing')
        
        # 初始化火山引擎API客户端
        configuration = Configuration()
        configuration.ak = self.access_key_id
        configuration.sk = self.secret_access_key
        configuration.region = self.region
        
        self.api_client = ApiClient(configuration=configuration)
        self.veiapi = VEIAPIApi(api_client=self.api_client)
        
        logger.info(f"即梦AI图生视频模型初始化完成，模型: {self.model_name}")
    
    def generate(self, image_url: str, prompt: str = "", **kwargs) -> str:
        """
        同步生成视频（阻塞模式）
        
        Args:
            image_url: 输入图像URL
            prompt: 输入提示文本（可选）
            **kwargs: 额外参数，会覆盖初始化时的配置
                - duration: 视频时长（秒）
                - style: 视频风格
                - seed: 随机种子
                - strength: 生成强度
                
        Returns:
            str: 生成的视频URL
        """
        # 准备请求参数
        request_kwargs = self._prepare_kwargs(**kwargs)
        retry_count = 0
        
        while True:
            try:
                # 构建请求参数
                params = {
                    "image_url": image_url,
                    "model_version": self.model_name,
                }
                
                # 添加可选参数
                if prompt:
                    params["prompt"] = prompt
                if "duration" in request_kwargs:
                    params["duration"] = request_kwargs["duration"]
                if "style" in request_kwargs:
                    params["style"] = request_kwargs["style"]
                if "seed" in request_kwargs:
                    params["seed"] = request_kwargs["seed"]
                if "strength" in request_kwargs:
                    params["strength"] = request_kwargs["strength"]
                
                logger.info(f"调用即梦AI图生视频API，参数: {params}")
                
                # 调用即梦AI API (使用VEIAPIApi的相应方法)
                # 注意：这里需要根据实际的API方法名称调整
                response = self.veiapi.create_sn_in_one_step(params)
                
                # 检查响应状态
                if hasattr(response, 'result') and response.result:
                    # 解析响应数据
                    result = response.result
                    video_url = result.get('video_url', '')
                    
                    if video_url:
                        logger.success(f"视频生成成功，URL: {video_url}")
                        return video_url
                    else:
                        logger.error("即梦AI API返回空视频URL")
                        return ""
                else:
                    error_msg = getattr(response, 'message', '未知错误')
                    logger.error(f"即梦AI API调用失败: {error_msg}")
                    return ""
                        
            except Exception as e:
                if not self._handle_error(e, retry_count):
                    # 如果不重试，返回空字符串
                    logger.error(f"即梦AI图生视频生成失败: {str(e)}")
                    return ""
                retry_count += 1
    
    def async_generate(self, image_url: str, prompt: str = "", **kwargs) -> str:
        """
        异步生成视频（阻塞模式）
        注意：即梦AI的API本身就是异步的，这里模拟异步调用
        
        Args:
            image_url: 输入图像URL
            prompt: 输入提示文本（可选）
            **kwargs: 额外参数
            
        Returns:
            str: 生成的视频URL
        """
        return self.generate(image_url, prompt, **kwargs)
    
    def stream_generate(self, image_url: str, prompt: str = "", **kwargs):
        """
        流式生成视频（即梦AI不支持流式生成）
        
        Args:
            image_url: 输入图像URL
            prompt: 输入提示文本（可选）
            **kwargs: 额外参数
            
        Yields:
            str: 视频生成进度或结果
        """
        # 即梦AI不支持流式生成，直接返回最终结果
        result = self.generate(image_url, prompt, **kwargs)
        yield result
    
    def async_stream_generate(self, image_url: str, prompt: str = "", **kwargs):
        """
        异步流式生成视频（即梦AI不支持流式生成）
        
        Args:
            image_url: 输入图像URL
            prompt: 输入提示文本（可选）
            **kwargs: 额外参数
            
        Yields:
            str: 视频生成进度或结果
        """
        # 即梦AI不支持流式生成，直接返回最终结果
        result = self.generate(image_url, prompt, **kwargs)
        yield result
