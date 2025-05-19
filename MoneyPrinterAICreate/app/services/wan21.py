import os
import shutil
import sys
from time import sleep
from uuid import uuid4

from gradio_client import Client, file, handle_file
from loguru import logger

import asyncio

from app.config import config

tmp_path="tmp"

async def check_process(client, method, seg_id):
    while True:
        try:
            process = client.predict(api_name="/get_process_bar")
            logger.info(f"[seg{seg_id+1}]-{method}-{process['label']}")
            if process["value"] == 100:
                while True:
                    video_path = client.predict(api_name="/process_change")
                    value = video_path.get("value", {})
                    if video_path and value:
                        src_path = value.get("video")
                        dst_path = os.path.join(tmp_path, f"{str(uuid4())}.mp4")
                        shutil.move(src_path, dst_path)
                        logger.info(f"[seg{seg_id+1}]-{method}-[success]-output: {dst_path}")
                        break
                    await asyncio.sleep(60)
                break
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(e)
            if "Queue is full" in str(e):
                await asyncio.sleep(60)
    return dst_path


# 图片生成视频
async def i2v(prompt, img_path, seg_id):
    # test
    # await asyncio.sleep(5)

    # formal
    token = config.app.get("wan21_api_keys")[0]
    client = Client("https://wan-ai-wan-2-1.ms.show/", hf_token=token)
    client.predict(
        prompt=prompt,
        image=handle_file(img_path),
        watermark_wanx=False,
        model="wanx2.1-i2v-plus",
        seed=-1,
        api_name="/i2v_generation_async"
    )
    video_path = await check_process(client, "i2v", seg_id)
    return video_path


# 文字生成视频
async def t2v(prompt, seg_id):
    # # test
    # await asyncio.sleep(5)

    # formal
    try:
        token = config.app.get("wan21_api_keys")[0]
        client = Client("https://wan-ai-wan-2-1.ms.show/", token)
        client.predict(
            prompt=prompt,
            size="720*1280",
            watermark_wanx=False,
            model="wanx2.1-t2v-plus",
            seed=-1,
            api_name="/t2v_generation_async"
        )
        video_path = await check_process(client, "t2v", seg_id)
        return video_path
    except Exception as e:
        logger.error(e)
        return ""


if __name__ == '__main__':
    prompt = ""
    img = ''
    #path = i2v(prompt, img, '1')
    path = t2v(prompt, '1')
