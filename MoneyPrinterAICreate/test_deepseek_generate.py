"""
测试DeepSeekLLM的generate方法
"""

from app.services.llm_engine.deepseek import DeepSeekLLM

def test_deepseek_generate():
    """测试DeepSeekLLM的generate方法"""
    # 配置参数，基于用户提供的curl请求
    config = {
        "model_name": "deepseek-chat",
        "base_url": "https://api.deepseek.com/chat/completions",
        "api_key": "sk-eb56acb1f6df4a2da286eda4c46535c7",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 60000,
        "max_retries": 5
    }
    
    # 创建DeepSeekLLM实例
    llm = DeepSeekLLM(config)
    
    # 用户提供的提示文本
    prompt = """# 角色
你是一位知识渊博的历史人物传记专家，能够以清晰、生动且准确的语言，为用户阐述历史人物的传奇一生。你擅长从海量的历史资料中提取关键信息，以编年体的形式呈现历史人物在不同人生阶段的重大事件和关键转折点。
视频创意：'王冕的一生'
视频时长约为 60 秒。
使用风格ID: 2。"""
    
    print("开始测试DeepSeekLLM.generate方法...")
    print(f"模型: {config['model_name']}")
    print(f"API地址: {config['base_url']}")
    print(f"提示文本长度: {len(prompt)} 字符")
    
    try:
        # 调用generate方法
        response = llm.generate(prompt)
        
        # 打印结果
        print("\n生成结果:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        print(f"生成结果长度: {len(response)} 字符")
        print("测试成功!")
        
        return response
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_deepseek_generate()