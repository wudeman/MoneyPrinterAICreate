"""LLM服务层，提供统一的模型访问接口"""

from typing import Dict, Any, Generator, AsyncGenerator, Optional
from loguru import logger
from app.services.llm_engine.factory import LLMFactory
from app.services.llm_engine.base import BaseLLM


class LLMService:       
    """
    LLM模型服务类
    提供统一的接口访问不同的LLM模型
    """
    
    def __init__(self):
        """初始化LLM模型服务"""
        self.factory = LLMFactory()
    
    def get_llm_instance(self, provider: str = "openai", **kwargs) -> BaseLLM:
        """
        获取LLM实例
        
        Args:
            provider: 模型提供商，可选值："openai", "deepseek", "azure"
            **kwargs: 模型配置参数
            
        Returns:
            BaseLLM: LLM实例
        """
        try:
            return self.factory.get_llm(provider, **kwargs)
        except Exception as e:
            logger.error(f"Failed to get LLM instance: {e}")
            raise
    
    def generate_text(self, prompt: str, provider: str = "openai", stream: bool = False, **kwargs) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 输入提示文本
            provider: 模型提供商
            stream: 是否使用流式响应
            **kwargs: 模型配置参数
            
        Returns:
            str: 生成的文本响应
        """
        llm = self.get_llm_instance(provider, **kwargs)
        
        if stream:
            # 如果是流式响应，收集所有片段
            response = ""
            for chunk in llm.stream_generate(prompt, **kwargs):
                response += chunk
            return response
        else:
            # 非流式响应
            return llm.generate(prompt, **kwargs)
    
    async def async_generate_text(self, prompt: str, provider: str = "openai", stream: bool = False, **kwargs) -> str:
        """
        异步生成文本响应
        
        Args:
            prompt: 输入提示文本
            provider: 模型提供商
            stream: 是否使用流式响应
            **kwargs: 模型配置参数
            
        Returns:
            str: 生成的文本响应
        """
        llm = self.get_llm_instance(provider, **kwargs)
        
        if stream:
            # 如果是流式响应，收集所有片段
            response = ""
            async for chunk in llm.async_stream_generate(prompt, **kwargs):
                response += chunk
            return response
        else:
            # 非流式响应
            return await llm.async_generate(prompt, **kwargs)
    
    def stream_text(self, prompt: str, provider: str = "openai", **kwargs) -> Generator[str, None, None]:
        """
        流式生成文本响应
        
        Args:
            prompt: 输入提示文本
            provider: 模型提供商
            **kwargs: 模型配置参数
            
        Yields:
            str: 流式响应片段
        """
        llm = self.get_llm_instance(provider, **kwargs)
        yield from llm.stream_generate(prompt, **kwargs)
    
    async def async_stream_text(self, prompt: str, provider: str = "openai", **kwargs) -> AsyncGenerator[str, None]:
        """
        异步流式生成文本响应
        
        Args:
            prompt: 输入提示文本
            provider: 模型提供商
            **kwargs: 模型配置参数
            
        Yields:
            str: 流式响应片段
        """
        llm = self.get_llm_instance(provider, **kwargs)
        async for chunk in llm.async_stream_generate(prompt, **kwargs):
            yield chunk
    
    def get_default_text_model(self) -> BaseLLM:
        """
        获取默认文本模型实例
        兼容现有代码
        
        Returns:
            BaseLLM: 默认LLM实例
        """
        return self.get_llm_instance("openai")
    
    def generate_with_retry(self, prompt: str, provider: str = "openai", max_retries: int = 3, **kwargs) -> str:
        """
        带重试的文本生成
        
        Args:
            prompt: 输入提示文本
            provider: 模型提供商
            max_retries: 最大重试次数
            **kwargs: 模型配置参数
            
        Returns:
            str: 生成的文本响应
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                return self.generate_text(prompt, provider, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Generation attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                if retry_count > max_retries:
                    break
        
        logger.error(f"All {max_retries + 1} generation attempts failed")
        raise last_error


# 创建全局服务实例
llm_service = LLMService()


def get_llm_service() -> LLMService:
    """
    获取LLM服务实例的函数
    提供依赖注入支持
    
    Returns:
        LLMService: LLM服务实例
    """
    return llm_service