"""LLM抽象基类，定义所有大模型实现必须遵循的接口规范"""

import abc
import asyncio
from typing import Dict, Any, Optional, Union, AsyncGenerator, Generator
from loguru import logger


class BaseLLM(abc.ABC):
    """LLM抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LLM实例
        
        Args:
            config: 模型配置参数，包含以下可选字段：
                - model_name: 模型名称
                - base_url: API请求地址
                - api_key: API密钥
                - temperature: 生成温度
                - max_tokens: 最大生成长度
                - timeout: 请求超时时间
                - max_retries: 最大重试次数
        """
        self.config = config or {}
        self.model_name = self.config.get('model_name', '')
        self.base_url = self.config.get('base_url', '')
        self.api_key = self.config.get('api_key', '')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 2000)
        self.timeout = self.config.get('timeout', 60000)
        self.max_retries = self.config.get('max_retries', 5)
        self.provider = self.__class__.__name__.replace('LLM', '')
        
    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        同步生成文本响应（阻塞模式）
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Returns:
            str: 生成的文本响应
        """
        pass
    
    @abc.abstractmethod
    async def async_generate(self, prompt: str, **kwargs) -> str:
        """
        异步生成文本响应（阻塞模式）
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Returns:
            str: 生成的文本响应
        """
        pass
    
    @abc.abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        同步流式生成文本响应
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Yields:
            str: 流式响应片段
        """
        pass
    
    @abc.abstractmethod
    async def async_stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        异步流式生成文本响应
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Yields:
            str: 流式响应片段
        """
        pass
    
    def _prepare_kwargs(self, **kwargs) -> Dict[str, Any]:
        """
        准备调用参数，合并默认配置和传入参数
        
        Args:
            **kwargs: 传入的参数
            
        Returns:
            Dict[str, Any]: 合并后的参数
        """
        merged_kwargs = self.config.copy()
        merged_kwargs.update(kwargs)
        return merged_kwargs
    
    def _handle_error(self, error: Exception, retry_count: int) -> bool:
        """
        处理错误，决定是否重试
        
        Args:
            error: 发生的错误
            retry_count: 当前重试次数
            
        Returns:
            bool: 是否应该重试
        """
        logger.error(f"{self.provider} LLM error: {str(error)}")
        
        # 如果达到最大重试次数，不再重试
        if retry_count >= self.max_retries:
            logger.error(f"Maximum retries ({self.max_retries}) exceeded")
            return False
        
        # 指数退避策略
        delay = 1 * (2 ** retry_count)
        logger.info(f"Retrying after {delay} seconds... (Attempt {retry_count + 1}/{self.max_retries})")
        
        # 同步模式下使用sleep
        if isinstance(error, Exception):
            import time
            time.sleep(delay)
        
        return True
    
    async def _async_handle_error(self, error: Exception, retry_count: int) -> bool:
        """
        异步处理错误，决定是否重试
        
        Args:
            error: 发生的错误
            retry_count: 当前重试次数
            
        Returns:
            bool: 是否应该重试
        """
        logger.error(f"{self.provider} LLM error: {str(error)}")
        
        # 如果达到最大重试次数，不再重试
        if retry_count >= self.max_retries:
            logger.error(f"Maximum retries ({self.max_retries}) exceeded")
            return False
        
        # 指数退避策略
        delay = 1 * (2 ** retry_count)
        logger.info(f"Retrying after {delay} seconds... (Attempt {retry_count + 1}/{self.max_retries})")
        
        # 异步模式下使用asyncio.sleep
        await asyncio.sleep(delay)
        return True
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        获取模型提供商信息
        
        Returns:
            Dict[str, str]: 包含提供商和模型信息的字典
        """
        return {
            "provider": self.provider,
            "model_name": self.model_name
        }