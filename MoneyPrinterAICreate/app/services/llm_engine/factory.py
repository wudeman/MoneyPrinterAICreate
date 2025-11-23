"""LLM工厂类，负责创建和管理不同的LLM模型实例"""

from typing import Dict, Any, Optional
from loguru import logger
from app.config import config as global_config

# 导入所有支持的LLM实现
from app.services.llm_engine.base import BaseLLM
from app.services.llm_engine.openai import OpenAILLM
from app.services.llm_engine.deepseek import DeepSeekLLM
from app.services.llm_engine.azure_openai import AzureOpenAILLM


class LLMFactory:
    """
    LLM工厂类，使用工厂模式创建不同的LLM模型实例
    支持根据配置或传入参数动态创建相应的模型实例
    """
    
    # 注册所有支持的LLM类型
    _llm_registry: Dict[str, type] = {
        "openai": OpenAILLM,
        "deepseek": DeepSeekLLM,
        "azure": AzureOpenAILLM
    }
    
    # 单例实例缓存
    _instances: Dict[str, BaseLLM] = {}
    
    @classmethod
    def register_llm(cls, provider: str, llm_class: type) -> None:
        """
        注册新的LLM实现类
        
        Args:
            provider: 提供商名称
            llm_class: LLM实现类
        """
        if not issubclass(llm_class, BaseLLM):
            raise TypeError(f"LLM class must inherit from BaseLLM")
        
        cls._llm_registry[provider.lower()] = llm_class
        logger.info(f"Registered LLM provider: {provider}")
    
    @classmethod
    def get_llm(cls, provider: Optional[str] = None, **kwargs) -> BaseLLM:
        """
        获取LLM实例
        
        Args:
            provider: 提供商名称，如果为None则使用全局配置
            **kwargs: 传递给LLM构造函数的参数
            
        Returns:
            BaseLLM: LLM实例
            
        Raises:
            ValueError: 如果提供商不支持
        """
        # 如果未指定提供商，使用全局配置
        if provider is None:
            provider = getattr(global_config, 'llm_provider', 'openai')
        
        provider = provider.lower()
        
        # 检查提供商是否支持
        if provider not in cls._llm_registry:
            supported = ", ".join(cls._llm_registry.keys())
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: {supported}")
        
        # 生成实例缓存键
        instance_key = f"{provider}:{cls._generate_config_key(kwargs)}"
        
        # 如果实例已存在且没有传入覆盖参数，返回缓存实例
        if instance_key not in cls._instances or kwargs:
            # 准备配置参数
            config = cls._prepare_config(provider, **kwargs)
            # 创建新实例
            llm_class = cls._llm_registry[provider]
            cls._instances[instance_key] = llm_class(config)
            logger.info(f"Created new {provider} LLM instance with model: {config.get('model_name')}")
        
        return cls._instances[instance_key]
    
    @classmethod
    def _prepare_config(cls, provider: str, **kwargs) -> Dict[str, Any]:
        """
        准备LLM配置参数
        
        Args:
            provider: 提供商名称
            **kwargs: 用户传入的参数
            
        Returns:
            Dict[str, Any]: 合并后的配置参数
        """
        # 从全局配置获取默认值
        config = {}
        
        if provider == "openai":
            config = {
                "model_name": getattr(global_config, 'llm_model', None) or "gpt-3.5-turbo",
                "base_url": getattr(global_config, 'openai_base_url', None),
                "api_key": getattr(global_config, 'openai_api_key', None),
                "temperature": getattr(global_config, 'llm_temperature', None) or 0.7,
            }
        elif provider == "azure":
            config = {
                "model_name": getattr(global_config, 'llm_model', None) or "gpt-35-turbo",
                "base_url": getattr(global_config, 'azure_endpoint', None),
                "api_key": getattr(global_config, 'azure_api_key', None),
                "api_version": getattr(global_config, 'azure_api_version', None),
                "temperature": getattr(global_config, 'llm_temperature', None) or 0.7,
            }
        elif provider == "deepseek":
            # DeepSeek默认配置
            config = {
                "model_name": kwargs.get("model_name", "deepseek-chat"),
                "base_url": kwargs.get("base_url", "https://api.deepseek.com"),
                "api_key": kwargs.get("api_key", ""),
                "temperature": kwargs.get("temperature", 0.7),
            }
        
        # 使用用户传入的参数覆盖默认值
        config.update(kwargs)
        return config
    
    @classmethod
    def _generate_config_key(cls, config: Dict[str, Any]) -> str:
        """
        根据配置生成缓存键
        
        Args:
            config: 配置字典
            
        Returns:
            str: 缓存键
        """
        # 只使用关键参数生成缓存键
        key_params = [
            "model_name", "base_url", "api_key", "temperature",
            "max_tokens", "timeout", "api_version"
        ]
        
        key_parts = []
        for param in key_params:
            if param in config:
                # 对于API密钥，只使用前8个字符用于缓存键，保护安全
                if param == "api_key" and config[param]:
                    value = config[param][:8] if len(config[param]) > 8 else config[param]
                else:
                    value = str(config[param])
                key_parts.append(f"{param}={value}")
        
        return ";".join(key_parts)
    
    @classmethod
    def clear_cache(cls) -> None:
        """
        清除所有缓存的LLM实例
        """
        cls._instances.clear()
        logger.info("Cleared all cached LLM instances")
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """
        获取所有支持的LLM提供商列表
        
        Returns:
            list: 支持的提供商名称列表
        """
        return list(cls._llm_registry.keys())