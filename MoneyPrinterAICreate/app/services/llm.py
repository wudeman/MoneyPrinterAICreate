import logging
import re
import json
from time import sleep
from typing import List
from loguru import logger
from openai import OpenAI
from openai import AzureOpenAI
from openai.types.chat import ChatCompletion

from app.config import config
from app.services.wan21 import t2v, i2v
import asyncio

_max_retries = 5


# search 工具的具体实现，这里我们只需要返回参数即可
def search_impl(arguments: dict[str, any]) -> any:
    """
    在使用 Moonshot AI 提供的 search 工具的场合，只需要原封不动返回 arguments 即可，
    不需要额外的处理逻辑。

    但如果你想使用其他模型，并保留联网搜索的功能，那你只需要修改这里的实现（例如调用搜索
    和获取网页内容等），函数签名不变，依然是 work 的。

    这最大程度保证了兼容性，允许你在不同的模型间切换，并且不需要对代码有破坏性的修改。
    """
    return arguments


def _generate_response(prompt: str) -> str:
    content = ""
    llm_provider = config.app.get("llm_provider", "openai")
    logger.info(f"llm provider: {llm_provider}")
    if llm_provider == "g4f":
        model_name = config.app.get("g4f_model_name", "")
        if not model_name:
            model_name = "gpt-3.5-turbo-16k-0613"
        import g4f

        content = g4f.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
    else:
        api_version = ""  # for azure
        if llm_provider == "moonshot":
            api_key = config.app.get("moonshot_api_key")
            model_name = config.app.get("moonshot_model_name")
            base_url = "https://api.moonshot.cn/v1"
        elif llm_provider == "ollama":
            # api_key = config.app.get("openai_api_key")
            api_key = "ollama"  # any string works but you are required to have one
            model_name = config.app.get("ollama_model_name")
            base_url = config.app.get("ollama_base_url", "")
            if not base_url:
                base_url = "http://localhost:11434/v1"
        elif llm_provider == "openai":
            api_key = config.app.get("openai_api_key")
            model_name = config.app.get("openai_model_name")
            base_url = config.app.get("openai_base_url", "")
            if not base_url:
                base_url = "https://api.openai.com/v1"
        elif llm_provider == "oneapi":
            api_key = config.app.get("oneapi_api_key")
            model_name = config.app.get("oneapi_model_name")
            base_url = config.app.get("oneapi_base_url", "")
        elif llm_provider == "azure":
            api_key = config.app.get("azure_api_key")
            model_name = config.app.get("azure_model_name")
            base_url = config.app.get("azure_base_url", "")
            api_version = config.app.get("azure_api_version", "2024-02-15-preview")
        elif llm_provider == "gemini":
            api_key = config.app.get("gemini_api_key")
            model_name = config.app.get("gemini_model_name")
            base_url = "***"
        elif llm_provider == "qwen":
            api_key = config.app.get("qwen_api_key")
            model_name = config.app.get("qwen_model_name")
            base_url = "***"
        elif llm_provider == "cloudflare":
            api_key = config.app.get("cloudflare_api_key")
            model_name = config.app.get("cloudflare_model_name")
            account_id = config.app.get("cloudflare_account_id")
            base_url = "***"
        elif llm_provider == "deepseek":
            api_key = config.app.get("deepseek_api_key")
            model_name = config.app.get("deepseek_model_name")
            base_url = config.app.get("deepseek_base_url")
            if not base_url:
                base_url = "https://api.deepseek.com"
        elif llm_provider == "ernie":
            api_key = config.app.get("ernie_api_key")
            secret_key = config.app.get("ernie_secret_key")
            base_url = config.app.get("ernie_base_url")
            model_name = "***"
            if not secret_key:
                raise ValueError(
                    f"{llm_provider}: secret_key is not set, please set it in the config.toml file."
                )
        else:
            raise ValueError(
                "llm_provider is not set, please set it in the config.toml file."
            )

        if not api_key:
            raise ValueError(
                f"{llm_provider}: api_key is not set, please set it in the config.toml file."
            )
        if not model_name:
            raise ValueError(
                f"{llm_provider}: model_name is not set, please set it in the config.toml file."
            )
        if not base_url:
            raise ValueError(
                f"{llm_provider}: base_url is not set, please set it in the config.toml file."
            )

        if llm_provider == "qwen":
            import dashscope
            from dashscope.api_entities.dashscope_response import GenerationResponse

            dashscope.api_key = api_key
            response = dashscope.Generation.call(
                model=model_name, messages=[{"role": "user", "content": prompt}]
            )
            if response:
                if isinstance(response, GenerationResponse):
                    status_code = response.status_code
                    if status_code != 200:
                        raise Exception(
                            f'[{llm_provider}] returned an error response: "{response}"'
                        )

                    content = response["output"]["text"]
                    return content.replace("\n", "")
                else:
                    raise Exception(
                        f'[{llm_provider}] returned an invalid response: "{response}"'
                    )
            else:
                raise Exception(f"[{llm_provider}] returned an empty response")

        if llm_provider == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=api_key, transport="rest")

            generation_config = {
                "temperature": 0.5,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
            ]

            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            try:
                response = model.generate_content(prompt)
                candidates = response.candidates
                generated_text = candidates[0].content.parts[0].text
            except (AttributeError, IndexError) as e:
                print("Gemini Error:", e)

            return generated_text

        if llm_provider == "cloudflare":
            import requests

            response = requests.post(
                f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_name}",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "messages": [
                        {"role": "system", "content": "You are a friendly assistant"},
                        {"role": "user", "content": prompt},
                    ]
                },
            )
            result = response.json()
            logger.info(result)
            return result["result"]["response"]

        if llm_provider == "ernie":
            import requests

            params = {
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": secret_key,
            }
            access_token = (
                requests.post("https://aip.baidubce.com/oauth/2.0/token", params=params)
                .json()
                .get("access_token")
            )
            url = f"{base_url}?access_token={access_token}"

            payload = json.dumps(
                {
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "top_p": 0.8,
                    "penalty_score": 1,
                    "disable_search": False,
                    "enable_citation": False,
                    "response_format": "text",
                }
            )
            headers = {"Content-Type": "application/json"}

            response = requests.request(
                "POST", url, headers=headers, data=payload
            ).json()
            return response.get("result")

        if llm_provider == "azure":
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=base_url,
            )
        else:
            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

        if llm_provider == "moonshot":
            response = client.chat.completions.create(
                model="moonshot-v1-auto",
                messages=[{"role": "system", "content": "你是具备联网搜索能力的 Kimi。"},
                          {"role": "user", "content": prompt}],
                temperature=0.3,
                tools=[
                    {
                        "type": "builtin_function",
                        "function": {
                            "name": "$web_search",
                        },
                    }
                ]
            )
        else:
            response = client.chat.completions.create(
                model=model_name, messages=[{"role": "user", "content": prompt}]
            )

        if response:
            messages = [{"role": "system", "content": "你是 Kimi。"}, {"role": "user", "content": prompt}]
            if isinstance(response, ChatCompletion):
                # 检查是否触发了工具调用
                if response.choices[0].finish_reason == "tool_calls":
                    messages.append(
                        response.choices[
                            0].message)  # <-- 我们将 Kimi 大模型返回给我们的 assistant 消息也添加到上下文中，以便于下次请求时 Kimi 大模型能理解我们的诉求
                    for tool_call in response.choices[0].message.tool_calls:  # <-- tool_calls 可能是多个，因此我们使用循环逐个执行
                        tool_call_name = tool_call.function.name
                        tool_call_arguments = json.loads(
                            tool_call.function.arguments)  # <-- arguments 是序列化后的 JSON Object，我们需要使用 json.loads 反序列化一下
                        if tool_call_name == "$web_search":
                            tool_result = search_impl(tool_call_arguments)
                        else:
                            tool_result = f"Error: unable to find tool by name '{tool_call_name}'"

                        # 使用函数执行结果构造一个 role=tool 的 message，以此来向模型展示工具调用的结果；
                        # 注意，我们需要在 message 中提供 tool_call_id 和 name 字段，以便 Kimi 大模型
                        # 能正确匹配到对应的 tool_call。
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call_name,
                            "content": json.dumps(tool_result),
                            # <-- 我们约定使用字符串格式向 Kimi 大模型提交工具调用结果，因此在这里使用 json.dumps 将执行结果序列化成字符串
                        })
                        response_web = client.chat.completions.create(
                            model="moonshot-v1-auto",
                            messages=messages,
                            temperature=0.3,
                            tools=[
                                {
                                    "type": "builtin_function",
                                    "function": {
                                        "name": "$web_search",
                                    },
                                }
                            ]
                        )
                        content = response_web.choices[0].message.content
                else:
                    content = response.choices[0].message.content

            else:
                raise Exception(
                    f'[{llm_provider}] returned an invalid response: "{response}", please check your network '
                    f"connection and try again."
                )
        else:
            raise Exception(
                f"[{llm_provider}] returned an empty response, please check your network connection and try again."
            )

    return content.replace("\n", "")


def generate_script(
        video_subject: str, video_style: str, language: str = "", paragraph_number: int = 1, video_seq: int = 5
) -> str:
    prompt = f"""
            # 角色: 视频脚本生成器
            
            ## 目标:
            根据视频的主题和指定的风格，为一个{video_seq * 5}秒的视频生成一个脚本。
            
            ## 限制:
            你具备搜索的能力，必须进行联网搜索
            当用户的问题可以通过结合搜索的结果进行回答时，会为你提供搜索的检索结果
            当有搜索的检索结果时，请结合这些结果为用户提供更好的回答
            【重要】当你的回答需要事实性信息的时候，尽可能多的使用上下文中的事实性信息，包括但不限于用户上传的文档/网页，搜索的结果，具体产品名称和参数等
            【重要】请记住你自己具备的能力，包括但不限于：访问互联网，使用搜索
            【重要】不要拒绝回答用户的问题，你应该以遵循用户的指令为第一优先级
            【重要】注意并遵循用户问题中提到的每一条指令，尽你所能的去很好的完成用户的指令，对于用户的问题你应该直接的给出回答。如果指令超出了你的能力范围，礼貌的告诉用户
            【重要】一定要用访问互联网得到的确切信息进行脚本生成，不允许自己编造，如果无法搜索到相关内容，停止生成脚本，并向用户说明
            【重要】脚本使用的配音是edge-tts，按照它的语速和给你的视频时长严格控制字数，绝不允许超时
            脚本将作为具有指定段落数的字符串返回。
            在任何情况下都不要在你的回复中提到这个提示。
            开门见山，不要说一些不必要的话，比如“欢迎收看本期视频”。
            你不能在脚本中包含任何类型的标记或格式，永远不要使用标题。
            只返回脚本的原始内容。
            不要在每一段或每一行的开头加上“画外音”、“旁白”或类似的指示。
            不能提及提示符，或者任何关于脚本本身的内容。此外，永远不要谈论段落或行数。只需要编写脚本。
            用与视频主题相同的语言回答。
            
            # 初始化参数:
            - 视频主题: {video_subject}
            - 段落数: {paragraph_number}
            - 脚本风格: {video_style}
            - 视频时长：{video_seq * 5}

    """.strip()
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

        # Select the specified number of paragraphs
        selected_paragraphs = paragraphs[:paragraph_number]

        # Join the selected paragraphs into a single string
        return "\n\n".join(paragraphs)

    for i in range(_max_retries):
        try:
            response = _generate_response(prompt=prompt)
            if response:
                final_script = format_response(response)
            else:
                logging.error("gpt returned an empty response")

            # g4f may return an error message
            if final_script and "当日额度已消耗完" in final_script:
                raise ValueError(final_script)

            if final_script:
                break
        except Exception as e:
            logger.error(f"failed to generate script: {e}")

        if i < _max_retries:
            logger.warning(f"failed to generate video script, trying again... {i + 1}")

    logger.success(f"completed: \n{final_script}")
    return final_script.strip()


def generate_outline(video_script: str, video_seq: str) -> dict:

    prompt = f"""
    你是一个短视频创作者，你需要根据给出的文案，为短视频编写分镜。
    文案：{video_script}
    分镜段数：{video_seq}
    
    你需要做的事情是：
    1. 编写指定段数的视频分镜，分镜内每段视频长5秒
    2. 为每段视频内容编写视频生成的提示语，要详细描述，灵活选择文字生视频(t2v)或图片生视频(i2v)功能
    3. 【非常重要】视频画面的提示词要详细描述，提示词是包含主体（画面主要部分）、修饰词（主体细节特征的补充）、环境描述（环境描写，环境内容）、镜头（画面镜头）的一段话。
    4. 对于无人物分镜，只需要写出你想生成什么，你的画面有什么，不允许直接复制文案内容去生成，先描述主体，再加一些对主体的修饰词，最后加一些你需要的环境和细节，以及镜头。
    5. 严格按以下json格式输出，不要换行，不允许是数组，只输出json内容：
    {{"(第n段分镜编号，从0开始，仅保留数字)":{{"prompt":"提示词内容","method":"t2v","img":"图片内容描述"}}
    如：{{"0":{{"prompt":"提示词内容","method":"t2v","img":"图片内容描述"}}
    
    你的功能有：
    1. 可以调用文字生视频、图片生视频功能，生成的每个视频时长只有5秒。对于文字生视频功能，你只需要给它提供提示词，它就可以为你生成。对于图片生视频功能，你需要给它上传一张图片和提示词，它就可以为你生成。
    2. 有工具能为你将生成的视频拼接起来。
    
    限制：
    1. 你只需要关注制作短视频的每个视频素材的画面内容和顺序安排
    2. 【非常重要】指示生成视频时，不允许它生成任何与文字、数字、英文字母有关的画面素材，但允许生成简单图案
    3. 【非常重要】只输出json数组，不允许输出其他内容
    """.strip()

    outline = {}
    for i in range(_max_retries):
        try:
            response = _generate_response(prompt=prompt)
            if response:
                logger.info(f"response: {response}")
                outline = response.strip("```json").strip("```").strip("\r\n").strip("[").strip("]")
                outline = json.loads(outline)
                #print(outline)
                if outline:
                    # g4f may return an error message
                    if "当日额度已消耗完" in outline:
                        raise ValueError(outline)
                    break
            else:
                logging.error("gpt returned an empty response")

        except Exception as e:
            logger.error(f"failed to generate outline: {e}")

        if i < _max_retries:
            logger.warning(f"failed to generate video outline, trying again... {i + 1}")

    return outline


async def generate_material_video(prompt: str, method: str, id: int, img: str = "") -> str:
    output_path = ""
    if method == "t2v":
        output_path = await t2v(prompt, id)
    if method == "i2v":
        output_path = await i2v(prompt, img, id)
    return output_path


def generate_terms(video_subject: str, video_script: str, amount: int = 5) -> List[str]:
    prompt = f"""
# Role: Video Search Terms Generator

## Goals:
Generate {amount} search terms for stock videos, depending on the subject of a video.

## Constrains:
1. the search terms are to be returned as a json-array of strings.
2. each search term should consist of 1-3 words, always add the main subject of the video.
3. you must only return the json-array of strings. you must not return anything else. you must not return the script.
4. the search terms must be related to the subject of the video.
5. reply with english search terms only.

## Output Example:
["search term 1", "search term 2", "search term 3","search term 4","search term 5"]

## Context:
### Video Subject
{video_subject}

### Video Script
{video_script}

Please note that you must use English for generating video search terms; Chinese is not accepted.
""".strip()

    logger.info(f"subject: {video_subject}")

    search_terms = []
    response = ""
    for i in range(_max_retries):
        try:
            response = _generate_response(prompt)
            search_terms = json.loads(response)
            if not isinstance(search_terms, list) or not all(
                    isinstance(term, str) for term in search_terms
            ):
                logger.error("response is not a list of strings.")
                continue

        except Exception as e:
            logger.warning(f"failed to generate video terms: {str(e)}")
            if response:
                match = re.search(r"\[.*]", response)
                if match:
                    try:
                        search_terms = json.loads(match.group())
                    except Exception as e:
                        logger.warning(f"failed to generate video terms: {str(e)}")
                        pass

        if search_terms and len(search_terms) > 0:
            break
        if i < _max_retries:
            logger.warning(f"failed to generate video terms, trying again... {i + 1}")

    logger.success(f"completed: \n{search_terms}")
    return search_terms


if __name__ == "__main__":
    # video_subject = "最新产品介绍"
    # video_style = "专业"
    # script = generate_script(
    #     video_subject=video_subject, video_style=video_style, language="zh-CN", paragraph_number=1
    # )
    # print("######################")
    # print(script)
    # sleep(20)
    outline = generate_outline(
        video_script=""
    )
    print("######################")
    print(outline)
