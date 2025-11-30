"""
即梦AI接入测试脚本

使用方法：
1. 确保已安装 volcengine 包: pip install volcengine
2. 在环境变量中设置火山引擎访问凭证:
   - VOLC_ACCESSKEY=your_access_key_id
   - VOLC_SECRETKEY=your_secret_access_key
3. 运行脚本: python test_jianmeng_ai.py
"""

import os
import sys
from loguru import logger

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_engine.factory import LLMFactory


def test_jianmeng_text2image():
    """测试即梦AI文生图功能"""
    print("\n========== 测试即梦AI文生图 ==========")
    
    try:
        # 从环境变量获取访问凭证
        access_key_id = os.environ.get("VOLC_ACCESSKEY")
        secret_access_key = os.environ.get("VOLC_SECRETKEY")
        
        if not access_key_id or not secret_access_key:
            print("❌ 请先设置环境变量 VOLC_ACCESSKEY 和 VOLC_SECRETKEY")
            return False
        
        # 创建即梦AI文生图实例
        text2image_llm = LLMFactory.get_llm(
            provider="jianmeng_text2image",
            model_name="jimeng-img-gen-v3",
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region="cn-north-1"
        )
        
        print("✅ 即梦AI文生图实例创建成功")
        
        # 生成图像
        print("正在生成图像...")
        image_url = text2image_llm.generate(
            prompt="一只可爱的小猫在花园里玩耍，阳光明媚",
            image_size="1024x1024"
        )
        
        if image_url:
            print(f"✅ 图像生成成功，URL: {image_url}")
            return True
        else:
            print("❌ 图像生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试即梦AI文生图时出错: {str(e)}")
        return False


def test_jianmeng_img2video():
    """测试即梦AI图生视频功能"""
    print("\n========== 测试即梦AI图生视频 ==========")
    
    try:
        # 从环境变量获取访问凭证
        access_key_id = os.environ.get("VOLC_ACCESSKEY")
        secret_access_key = os.environ.get("VOLC_SECRETKEY")
        
        if not access_key_id or not secret_access_key:
            print("❌ 请先设置环境变量 VOLC_ACCESSKEY 和 VOLC_SECRETKEY")
            return False
        
        # 创建即梦AI图生视频实例
        img2video_llm = LLMFactory.get_llm(
            provider="jianmeng_img2video",
            model_name="jimeng-video-gen-v3",
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region="cn-north-1"
        )
        
        print("✅ 即梦AI图生视频实例创建成功")
        
        # 注意：这里需要一个真实的图像URL进行测试
        # 在实际使用中，请替换为有效的图像URL
        test_image_url = "https://example.com/test-image.jpg"
        
        print("正在生成视频...")
        video_url = img2video_llm.generate(
            image_url=test_image_url,
            prompt="让画面中的元素动起来",
            duration=5
        )
        
        if video_url:
            print(f"✅ 视频生成成功，URL: {video_url}")
            return True
        else:
            print("❌ 视频生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试即梦AI图生视频时出错: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("即梦AI接入测试")
    print("=" * 60)
    
    # 测试即梦AI文生图
    text2image_success = test_jianmeng_text2image()
    
    # 测试即梦AI图生视频
    img2video_success = test_jianmeng_img2video()
    
    print("\n" + "=" * 60)
    print("测试结果:")
    print(f"  文生图测试: {'✅ 通过' if text2image_success else '❌ 失败'}")
    print(f"  图生视频测试: {'✅ 通过' if img2video_success else '❌ 失败'}")
    print("=" * 60)
    
    if text2image_success and img2video_success:
        print("🎉 所有测试通过，即梦AI接入成功！")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")


if __name__ == "__main__":
    main()
