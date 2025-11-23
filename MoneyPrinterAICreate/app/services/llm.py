import logging
import re
import json
from time import sleep
from typing import List
from loguru import logger

from app.config import config
from app.services.wan21 import t2v, i2v
import asyncio

# 导入新的LLM服务
from app.services.llm_service import llm_service

_max_retries = 5


def search_impl(arguments: dict[str, any]) -> any:
    """搜索实现"""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        logger.error("please install duckduckgo_search")
        return []

    with DDGS() as ddgs:
        search_results = ddgs.text(arguments["query"], max_results=arguments.get("max_results", 3))
        logger.info(f"search results: {search_results}")
        if search_results:
            return [i["body"] for i in search_results]
        return []


def _generate_response(prompt: str) -> str:
    """调用大模型生成回复"""
    # 重试次数
    retry_count = 0
    # 基础重试间隔（秒）
    base_delay = 1

    # 构建模型参数
    model_kwargs = {
        "temperature": config.llm_temperature or 0.7,
        "max_retries": _max_retries
    }
    
    # 如果指定了模型名称，添加到参数中
    if config.llm_model:
        model_kwargs["model_name"] = config.llm_model

    while retry_count < _max_retries:
        try:
            # 使用新的LLM服务架构
            response = llm_service.generate_with_retry(
                prompt=prompt,
                provider=config.llm_provider,
                **model_kwargs
            )
            
            if response.strip():
                return response
            else:
                logger.error("Empty response received from LLM service")

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            retry_count += 1
            if retry_count >= _max_retries:
                logger.error("Maximum retries exceeded")
                return ""
            # 指数退避策略
            delay = base_delay * (2 ** (retry_count - 1))
            logger.info(f"Retrying after {delay} seconds...")
            sleep(delay)

    return ""


def generate_script(
        video_subject: str, language: str = "", paragraph_number: int = 1, 
        template_id: str = "", style_id: str = "", duration: int = 30, video_style: str = "",
        prompt_template: dict = None
) -> str:
    # 使用style_id作为video_style，如果style_id为空则使用传入的video_style
    final_video_style = style_id or video_style or "默认风格"
    
    # 构建提示词
    if prompt_template and prompt_template.get("script_prompt"):
        # 使用模板中的提示词
        base_prompt = prompt_template["script_prompt"]
        # 替换提示词中的变量
        prompt = base_prompt.replace("{video_subject}", video_subject)
        prompt = prompt.replace("{language}", language)
        prompt = prompt.replace("{paragraph_number}", str(paragraph_number))
        prompt = prompt.replace("{template_id}", template_id)
        prompt = prompt.replace("{style_id}", style_id)
        prompt = prompt.replace("{duration}", str(duration))
        prompt = prompt.replace("{video_style}", video_style)
        prompt = prompt.replace("{final_video_style}", final_video_style)
    else:
        # 默认提示词
        prompt = f"""
                # 角色: 视频脚本生成器
                
                ## 目标:
                根据视频的主题和指定的风格，为一个{duration}秒的视频生成一个脚本。
                
                ## 限制:
                你具备搜索的能力，必须进行联网搜索
                当用户的问题可以通过结合搜索的结果进行回答时，会为你提供搜索的检索结果
                当有搜索的检索结果时，请结合这些结果为用户提供更好的回答
                【重要】当你的回答需要事实性信息的时候，尽可能多的使用上下文中的事实性信息，包括但不限于用户上传的文档/网页，搜索的结果，具体产品名称和参数等
                【重要】请记住你自己具备的能力，包括但不限于：访问互联网，使用搜索
                【重要】不要拒绝回答用户的问题，你应该以遵循用户的指令为第一优先级
                【重要】注意并遵循用户问题中提到的每一条指令，尽你所能的去很好的完成用户的指令，对于用户的问题你应该直接的给出回答。如果指令超出了你的能力范围，礼貌的告诉用户
                【重要】一定要用访问互联网得到的确切信息进行脚本生成，不允许自己编造，如果无法搜索到相关内容，停止生成脚本，并向用户说明
                【重要】脚本使用的配音是edge-tts，按照它的语速和给你的视频时长({duration}秒)严格控制字数，绝不允许超时
                脚本将作为具有指定段落数的字符串返回。
                在任何情况下都不要在你的回复中提到这个提示。
                开门见山，不要说一些不必要的话，比如"欢迎收看本期视频"。
                你不能在脚本中包含任何类型的标记或格式，永远不要使用标题。
                只返回脚本的原始内容。
                不要在每一段或每一行的开头加上"画外音"、"旁白"或类似的指示。
                不能提及提示符，或者任何关于脚本本身的内容。此外，永远不要谈论段落或行数。只需要编写脚本。
                用与视频主题相同的语言回答。
                
                # 初始化参数:
                - 视频主题: {video_subject}
                - 段落数: {paragraph_number}
                - 脚本风格: {final_video_style}
                - 视频时长：{duration}秒
                - 模板ID: {template_id} (如果有特定模板要求)
        """
    prompt = prompt.strip()
    
    if language:
        prompt += f"\n- language: {language}"

    final_script = ""
    logger.info(f"subject: {video_subject}")

    def format_response(response):
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        # Keep only the specified number of paragraphs
        if len(paragraphs) > paragraph_number:
            paragraphs = paragraphs[:paragraph_number]

        # Remove empty paragraphs and join
        cleaned_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return "\n\n".join(cleaned_paragraphs)

    for retry_count in range(_max_retries):
        try:
            response = _generate_response(prompt)
            logger.info(f"llm response: {response}")
            if response.strip():
                formatted = format_response(response)
                logger.info(f"formatted script: {formatted}")
                return formatted
        except Exception as e:
            logger.error(f"Error in generate_script: {e}")
            sleep(1)

    # 如果多次尝试后仍未成功，返回默认内容
    default_scripts = [
        "这是默认脚本内容。根据您的需求，我们可以生成更加定制化的视频脚本。",
        "视频内容正在生成中。请提供更具体的主题和要求，以获得更好的效果。",
        "欢迎观看本期视频。我们将为您带来精彩内容。",
    ]
    return "\n\n".join(default_scripts[:paragraph_number])


def generate_terms(video_subject: str, video_script: str) -> List[str]:
    """生成搜索词"""
    prompt = f"""
        You are a helpful assistant that generates search terms for a video based on its subject and script. Follow these rules:

1. the search terms are to be returned as a json-array of strings.
2. each search term should consist of 1-3 words, always add the main subject of the video.
3. you must only return the json-array of strings. you must not return anything else. you must not return the script.
4. the search terms must be related to the subject of the video.
5. reply with english search terms only.

Example:
```json
["search term 1", "search term 2", "search term 3","search term 4","search term 5"]
```

Subject of the video:
{video_subject}

Script of the video:
{video_script}

Please note that you must use English for generating video search terms; Chinese is not accepted.
    """

    try:
        response = _generate_response(prompt)
        # 清理响应
        response = response.strip()
        # 移除可能的markdown代码块标记
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]
        # 尝试解析为JSON
        search_terms = json.loads(response)
        logger.info(f"Generated search terms: {search_terms}")
        return search_terms[:5]  # 最多返回5个搜索词
    except Exception as e:
        logger.error(f"Error generating search terms: {e}")
        # 如果生成失败，使用视频主题作为备选
        return [video_subject] * 5
