# 即梦AI接入使用指南

## 简介

即梦AI是字节跳动旗下的AI生成服务，提供文生图和图生视频等能力。本指南将介绍如何在项目中接入和使用即梦AI服务。

## 安装依赖

首先需要安装火山引擎Python SDK：

```bash
pip install volcengine
```

## 配置说明

### 1. 获取访问凭证

1. 登录[火山引擎控制台](https://console.volcengine.com/)
2. 进入访问控制 -> 访问密钥页面
3. 创建并获取Access Key ID和Secret Access Key

### 2. 配置文件设置

在`config.toml`中添加即梦AI相关配置：

```toml
[jianmeng]
# 即梦AI文生图配置
text2image_model = "jimeng-img-gen-v3"
access_key_id = "your_access_key_id"
secret_access_key = "your_secret_access_key"
region = "cn-north-1"

# 即梦AI图生视频配置
img2video_model = "jimeng-video-gen-v3"
```

## 使用示例

### 文生图使用示例

```python
from app.services.llm_engine.factory import LLMFactory

# 创建即梦AI文生图实例
text2image_llm = LLMFactory.get_llm(
    provider="jianmeng_text2image",
    model_name="jimeng-img-gen-v3",
    access_key_id="your_access_key_id",
    secret_access_key="your_secret_access_key",
    region="cn-north-1"
)

# 生成图像
image_url = text2image_llm.generate(
    prompt="一只可爱的小猫在花园里玩耍",
    image_size="1024x1024",
    style="anime"
)

print(f"生成的图像URL: {image_url}")
```

### 图生视频使用示例

```python
from app.services.llm_engine.factory import LLMFactory

# 创建即梦AI图生视频实例
img2video_llm = LLMFactory.get_llm(
    provider="jianmeng_img2video",
    model_name="jimeng-video-gen-v3",
    access_key_id="your_access_key_id",
    secret_access_key="your_secret_access_key",
    region="cn-north-1"
)

# 生成视频
video_url = img2video_llm.generate(
    image_url="https://example.com/image.jpg",
    prompt="让小猫在花园里动起来",
    duration=5
)

print(f"生成的视频URL: {video_url}")
```

## 支持的参数

### 文生图参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| prompt | str | 图像生成提示词 |
| image_size | str | 图像尺寸，如"1024x1024" |
| style | str | 图像风格 |
| seed | int | 随机种子 |
| strength | float | 生成强度 |

### 图生视频参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| image_url | str | 输入图像URL |
| prompt | str | 视频生成提示词 |
| duration | int | 视频时长（秒） |
| style | str | 视频风格 |
| seed | int | 随机种子 |
| strength | float | 生成强度 |

## 错误处理

即梦AI的实现包含了错误重试机制，当遇到网络问题或API限流时会自动重试。可以通过配置`max_retries`参数来调整重试次数。

```python
text2image_llm = LLMFactory.get_llm(
    provider="jianmeng_text2image",
    model_name="jimeng-img-gen-v3",
    access_key_id="your_access_key_id",
    secret_access_key="your_secret_access_key",
    max_retries=3
)
```

## 注意事项

1. **API配额**：即梦AI有API调用频率限制，请合理使用
2. **费用**：使用即梦AI服务会产生费用，请关注计费说明
3. **区域设置**：确保region配置正确，目前主要支持`cn-north-1`
4. **密钥安全**：不要将Access Key ID和Secret Access Key硬编码在代码中，建议使用环境变量或配置文件

## 相关文档

- [即梦AI官方文档](https://www.volcengine.com/docs)
- [火山引擎视觉服务文档](https://www.volcengine.com/docs/6444)
- [Python SDK GitHub仓库](https://github.com/volcengine/volc-sdk-python)
