# MoneyPrinterAICreate
## 特点
本短视频生成器在GitHub开源项目
[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)的基础上，接入了万相通义 wan2.1 ai文生视频、图生视频作为剪辑素材的功能，素材更加丰富。支持分镜分镜与提示词修改，视频生成更可控。

## 界面
![set](https://github.com/user-attachments/assets/a39740fc-ba78-43a9-91c6-0be32312eef8)
![script](https://github.com/user-attachments/assets/e527bcc4-d9c8-4ef9-ad75-b182a8e7d009)
![videoset](https://github.com/user-attachments/assets/9ea38b4a-5341-42ea-b84f-5686ac1bbedc)
![material](https://github.com/user-attachments/assets/212d630c-df7a-4f76-bd44-2d2e1ae277ad)

## 工作流程
利用语言大模型生成视频文案和分镜、提示词（可人工修改），阿里最新的ai生成视频模型通义万相Wan2.1生成视频素材，最后自动拼接剪辑为带有字幕、配音、配乐的短视频。

## 隐私问题
wan21生成视频功能使用的是官方提供的试用api，上传的图片均会被收集，请注意不要上传个人隐私相关的图片。

## 使用说明
1. 按照[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)进行部署，若为windows，一键部署后将MoneyPrinterTurbo整个文件夹替换为MoneyPrinterAICreate，并修改start.bat，将MoneyPrinterTurbo改为MoneyPrinterAICreate。  
   免部署百度网盘：https://pan.baidu.com/s/1whNdwN9D6xlz4sUCCSFM3w?pwd=3ja4 提取码: 3ja4
3. 填写基础设置：
   - 大模型提供商  
   - wan21 API key   
        用于视频素材生成。在魔搭社区申请，目前免费使用。  
4. 填写视频主题
5. (可选) 填写视频风格，如：搞笑
   
(视频来源为本地文件，忽略步骤567)  

5. 调整素材块数量，默认为5段，1段5s。
6. 单击“点击使用AI根据主题生成视频文案”，
7. 单击“点击使用AI根据视频文案生成视频分镜”，生成的视频分镜（即提示词）会在“素材生成区”展示。
   
   其中，“提示词”用于指示wan21生成视频素材，不满意可人工修改，注意事项见下。

    大模型生成的分镜中可能包含用于生成素材的上传图片指示，可以选择性上传。

    点击“生成”，右侧预览区显示相应提醒，**耐心！！**等待，最快**10分钟**能完成一个素材的生成。

8. 根据提示填写视频设置、音频设置、字幕设置

9. 单击最底部的“生成视频”，耐心等待
10. 成功生成视频后，可下载到本地

## 提示词注意
1. 不要包含数字、字母、中文字符等特殊符号，因为wan21只会生成一些“看起来”像字符的东西。
2. 尽可能详细描述你想要的画面。


## 文案生成
代码中已经设置好基础提示词，有需要可在llm.py中自行修改。（有更好的提示词请在issue里给我也看看(´▽`ʃ♡ƪ)）  
“视频主题”和“视频风格”决定“视频文案”的内容    
“素材块数量”决定“视频文案”的长短。

## 分镜生成
代码中已经设置好基础提示词，有需要可在llm.py中自行修改。 
由于wan21 api每次只能生成一段5s的视频，为了满足剪辑时长需求，通过指定分镜段数来让它生成多个视频素材的提示词和上传图片。

## 视频素材生成
使用魔搭社区上通义万相官方提供的Wan-2.1试用api提供文生视频、图生视频功能。  
（正在探索其他的视频生成模型……尽力白嫖）

考虑到不一定有ai给出的指定图片素材，因此上传图片可选，Wan2.1会基于你上传的图片和提示词进行视频生成，视频分辨率与上传的图片一致。
该试用api速度较慢，测试下来每个5s的视频素材需要10分钟。（偶尔会超过20分钟都没生成成功，可以放弃这次生成重试了）

[Wan-2.1试用页](https://modelscope.cn/studios/Wan-AI/Wan-2.1/summary)

[Wan-2.1项目仓库](https://github.com/Wan-Video/Wan2.1)

## 使用问题
1. edge-tts非V2的声音不用apikey，如果提示连接不了等等错误，可尝试开启vpn（全局模式），在app/services/voice.py，communicate = edge_tts.Communicate(text, voice_name, rate=rate_str) 加上代理配置，详见代码注释
2. 大模型生成文案和分镜时，有时会返回空值或莫名出错无响应，已增加日志，可以多尝试几次

## 后续优化
1. 接入腾讯混元语言大模型（每月有免费额度）
2. 优化提示词，增加预设风格选择，提高文案和分镜提示词质量
3. 更改剪辑逻辑，将文案分段填入分镜中。使同一分镜中，朗读的文案和画面适配