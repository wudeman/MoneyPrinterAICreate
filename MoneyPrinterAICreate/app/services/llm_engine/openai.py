"""OpenAI模型实现类"""

import httpx
import json
import asyncio
from typing import Dict, Any, Generator, AsyncGenerator
from loguru import logger
from app.services.llm_engine.base import BaseLLM


class OpenAILLM(BaseLLM):
    """
    OpenAI模型实现类
    支持同步和异步的文本生成，以及流式响应
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化OpenAI模型实例
        
        Args:
            config: 模型配置参数，包含以下字段：
                - model_name: 模型名称，如"gpt-4", "gpt-3.5-turbo"
                - base_url: API请求地址，默认为"https://api.openai.com"
                - api_key: API密钥
                - temperature: 生成温度
                - max_tokens: 最大生成长度
                - timeout: 请求超时时间
                - max_retries: 最大重试次数
                - api_version: API版本（可选）
        """
        super().__init__(config)
        # OpenAI特有配置
        self.api_version = self.config.get('api_version', 'v1')
        # 构建API路径，确保base_url不为None
        base_url = self.base_url or "https://api.openai.com"
        self.chat_completions_url = f"{base_url.rstrip('/')}/{self.api_version}/chat/completions"
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        同步生成文本响应（阻塞模式）
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Returns:
            str: 生成的文本响应
        """
        # 准备请求参数
        request_kwargs = self._prepare_kwargs(**kwargs)
        retry_count = 0
        
        while True:
            try:
                # 创建请求头
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {request_kwargs['api_key']}"
                }
                
                # 构建请求体
                payload = {
                    "model": request_kwargs['model_name'],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": request_kwargs['temperature'],
                    "max_tokens": request_kwargs.get('max_tokens', 2000),
                    "stream": False
                }
                
                # 发送同步请求
                with httpx.Client(timeout=request_kwargs['timeout']) as client:
                    response = client.post(
                        self.chat_completions_url,
                        headers=headers,
                        json=payload
                    )
                    
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 解析响应
                    data = response.json()
                    if data.get('choices') and len(data['choices']) > 0:
                        return data['choices'][0]['message']['content']
                    else:
                        logger.error("OpenAI API returned empty response")
                        return ""
                        
            except Exception as e:
                if not self._handle_error(e, retry_count):
                    # 如果不重试，返回空字符串
                    return ""
                retry_count += 1
    
    async def async_generate(self, prompt: str, **kwargs) -> str:
        """
        异步生成文本响应（阻塞模式）
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Returns:
            str: 生成的文本响应
        """
        # 准备请求参数
        request_kwargs = self._prepare_kwargs(**kwargs)
        retry_count = 0
        
        while True:
            try:
                # 创建请求头
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {request_kwargs['api_key']}"
                }
                
                # 构建请求体
                payload = {
                    "model": request_kwargs['model_name'],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": request_kwargs['temperature'],
                    "max_tokens": request_kwargs.get('max_tokens', 2000),
                    "stream": False
                }
                
                # 发送异步请求
                async with httpx.AsyncClient(timeout=request_kwargs['timeout']) as client:
                    response = await client.post(
                        self.chat_completions_url,
                        headers=headers,
                        json=payload
                    )
                    
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 解析响应
                    data = response.json()
                    if data.get('choices') and len(data['choices']) > 0:
                        return data['choices'][0]['message']['content']
                    else:
                        logger.error("OpenAI API returned empty response")
                        return ""
                        
            except Exception as e:
                if not await self._async_handle_error(e, retry_count):
                    # 如果不重试，返回空字符串
                    return ""
                retry_count += 1
    
    def stream_generate(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        同步流式生成文本响应
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Yields:
            str: 流式响应片段
        """
        # 准备请求参数
        request_kwargs = self._prepare_kwargs(**kwargs)
        retry_count = 0
        
        while True:
            try:
                # 创建请求头
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {request_kwargs['api_key']}"
                }
                
                # 构建请求体
                payload = {
                    "model": request_kwargs['model_name'],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": request_kwargs['temperature'],
                    "max_tokens": request_kwargs.get('max_tokens', 2000),
                    "stream": True
                }
                
                # 发送同步流式请求
                with httpx.stream(
                    "POST",
                    self.chat_completions_url,
                    headers=headers,
                    json=payload,
                    timeout=request_kwargs['timeout']
                ) as response:
                    response.raise_for_status()
                    
                    # 处理流式响应
                    for chunk in response.iter_lines():
                        if chunk:
                            # 去除data:前缀
                            chunk = chunk.decode('utf-8')
                            if chunk.startswith('data: '):
                                chunk = chunk[6:]
                                
                            # 检查是否为结束标记
                            if chunk == '[DONE]':
                                break
                                
                            try:
                                # 解析JSON
                                data = json.loads(chunk)
                                if data.get('choices') and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse chunk: {chunk}")
                
                # 正常结束，不再重试
                break
                
            except Exception as e:
                if not self._handle_error(e, retry_count):
                    # 如果不重试，结束生成器
                    break
                retry_count += 1
    
    async def async_stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        异步流式生成文本响应
        
        Args:
            prompt: 输入提示文本
            **kwargs: 额外参数，会覆盖初始化时的配置
            
        Yields:
            str: 流式响应片段
        """
        # 准备请求参数
        request_kwargs = self._prepare_kwargs(**kwargs)
        retry_count = 0
        
        while True:
            try:
                # 创建请求头
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {request_kwargs['api_key']}"
                }
                
                # 构建请求体
                payload = {
                    "model": request_kwargs['model_name'],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": request_kwargs['temperature'],
                    "max_tokens": request_kwargs.get('max_tokens', 2000),
                    "stream": True
                }
                
                # 发送异步流式请求
                async with httpx.AsyncClient(timeout=request_kwargs['timeout']) as client:
                    async with client.stream(
                        "POST",
                        self.chat_completions_url,
                        headers=headers,
                        json=payload
                    ) as response:
                        response.raise_for_status()
                        
                        # 处理流式响应
                        async for chunk in response.aiter_lines():
                            if chunk:
                                # 去除data:前缀
                                chunk_str = chunk.decode('utf-8')
                                if chunk_str.startswith('data: '):
                                    chunk_str = chunk_str[6:]
                                    
                                # 检查是否为结束标记
                                if chunk_str == '[DONE]':
                                    break
                                    
                                try:
                                    # 解析JSON
                                    data = json.loads(chunk_str)
                                    if data.get('choices') and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse chunk: {chunk_str}")
                
                # 正常结束，不再重试
                break
                
            except Exception as e:
                if not await self._async_handle_error(e, retry_count):
                    # 如果不重试，结束生成器
                    break
                retry_count += 1