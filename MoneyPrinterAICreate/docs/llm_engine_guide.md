# LLM引擎接口使用指南

## 1. 架构概述

LLM引擎采用了灵活的抽象工厂模式，支持多种大语言模型提供商，主要组件包括：

- **抽象基类** (`LLMBase`): 定义统一的接口规范
- **模型适配器** (如`OpenAILLM`, `AzureOpenAILLM`): 实现特定提供商的API调用
- **工厂类** (`LLMFactory`): 负责创建和管理模型实例，支持缓存
- **服务层** (`LLMModelService`): 封装工厂调用，提供重试机制

## 2. 快速开始

### 2.1 基本使用

```python
from app.services.llm_model_service import llm_model_service

# 生成文本
response = llm_model_service.generate_text(
    prompt="写一首关于人工智能的诗",
    model_name="gpt-3.5-turbo",
    temperature=0.7
)
print(response)
```

### 2.2 异步使用

```python
import asyncio
from app.services.llm_model_service import llm_model_service

async def main():
    # 异步生成文本
    response = await llm_model_service.async_generate_text(
        prompt="写一首关于人工智能的诗",
        model_name="gpt-3.5-turbo"
    )
    print(response)

asyncio.run(main())
```

### 2.3 流式响应

```python
from app.services.llm_model_service import llm_model_service

# 流式生成文本
for chunk in llm_model_service.stream_text(
    prompt="写一首关于人工智能的诗",
    model_name="gpt-3.5-turbo"
):
    print(chunk, end="", flush=True)
print()
```

## 3. 配置说明

### 3.1 环境变量配置

支持通过环境变量配置默认参数：

- `LLM_PROVIDER`: 模型提供商，可选值：`openai`, `azure`, `deepseek`等
- `LLM_MODEL`: 默认模型名称
- `LLM_API_KEY`: API密钥
- `LLM_BASE_URL`: 自定义API基础URL
- `LLM_TEMPERATURE`: 默认温度参数
- `LLM_MAX_TOKENS`: 默认最大token数

### 3.2 运行时配置

也可以在调用时传入配置参数：

```python
response = llm_model_service.generate_text(
    prompt="你好",
    provider="openai",  # 指定提供商
    model_name="gpt-4",
    api_key="your-api-key",
    temperature=0.5,
    max_tokens=500
)
```

## 4. 支持的模型提供商

### 4.1 OpenAI

```python
response = llm_model_service.generate_text(
    prompt="你好",
    provider="openai",
    model_name="gpt-3.5-turbo",
    api_key="sk-..."
)
```

### 4.2 Azure OpenAI

```python
response = llm_model_service.generate_text(
    prompt="你好",
    provider="azure",
    model_name="gpt-35-turbo",
    api_key="your-azure-api-key",
    base_url="https://your-resource.openai.azure.com",
    deployment_name="your-deployment-name"
)
```

### 4.3 DeepSeek

```python
response = llm_model_service.generate_text(
    prompt="你好",
    provider="deepseek",
    model_name="deepseek-chat",
    api_key="your-deepseek-api-key"
)
```

## 5. 高级特性

### 5.1 重试机制

服务层内置了自动重试功能，当遇到临时性错误时会自动重试：

```python
# 默认重试3次，间隔1秒
response = llm_model_service.generate_text(
    prompt="你好",
    max_retries=5,  # 自定义重试次数
    retry_delay=2   # 自定义重试间隔（秒）
)
```

### 5.2 自定义模型适配器

可以注册自定义的模型适配器：

```python
from app.services.llm_engine.factory import LLMFactory
from app.services.llm_engine.base import LLMBase

class CustomLLM(LLMBase):
    def generate(self, prompt, **kwargs):
        # 实现自定义逻辑
        return "Custom response"
    
    async def async_generate(self, prompt, **kwargs):
        return "Custom async response"
    
    def stream_generate(self, prompt, **kwargs):
        yield "Custom"
        yield " "
        yield "stream"
    
    async def async_stream_generate(self, prompt, **kwargs):
        yield "Custom"
        yield " "
        yield "async stream"

# 注册自定义适配器
LLMFactory.register("custom", CustomLLM)

# 使用自定义适配器
response = llm_model_service.generate_text(
    prompt="你好",
    provider="custom"
)
```

## 6. 错误处理

在使用过程中可能遇到的错误：

- `ValueError`: 配置参数错误
- `APIError`: API调用失败
- `ConnectionError`: 网络连接问题

建议使用try-except进行错误处理：

```python
try:
    response = llm_model_service.generate_text(prompt="你好")
except Exception as e:
    print(f"生成失败: {e}")
```

## 7. 兼容性说明

为了兼容旧代码，保留了`LLMModelService`类的直接实例化方式：

```python
from app.services.llm_engine.llm import LLMModelService

# 旧方式仍然可用
llm_service = LLMModelService()
response = llm_service.generate_text("你好")
```

但推荐使用新的服务层单例：

```python
from app.services.llm_model_service import llm_model_service

# 推荐方式
response = llm_model_service.generate_text("你好")
```

## 8. 性能优化

- 工厂类会缓存LLM实例，避免重复初始化
- 可以调整重试参数以适应不同的网络环境
- 对于频繁调用，建议使用流式响应以获得更好的用户体验

---

通过这种灵活的架构设计，可以轻松集成新的LLM提供商，同时保持代码的一致性和可维护性。