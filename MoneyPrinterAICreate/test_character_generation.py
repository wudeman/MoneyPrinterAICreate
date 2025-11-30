"""
测试角色列表生成接口

使用方法：
1. 确保后端服务已启动（python main.py）
2. 运行此测试脚本: python test_character_generation.py
"""

import requests
import json


# 配置
BASE_URL = "http://localhost:8080/api/v1"

# 测试数据
TEST_TASK_DATA = {
    "video_idea": "一个关于春天的美好故事",
    "template_id": 1,  # 需要根据实际数据库中的模板ID调整
    "style_id": 1,     # 需要根据实际数据库中的风格ID调整
    "duration": 30
}


def test_create_task():
    """测试创建任务并生成剧本"""
    print("\n========== 测试1: 创建任务并生成剧本 ==========")
    url = f"{BASE_URL}/tasks/create-and-generate"
    
    try:
        response = requests.post(url, json=TEST_TASK_DATA)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 提取任务ID
            task_id = data.get("data", {}).get("task_id")
            if task_id:
                print(f"✅ 任务创建成功，任务ID: {task_id}")
                return task_id
            else:
                print("❌ 未能获取任务ID")
                return None
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


def test_generate_characters(task_id):
    """测试生成角色列表接口"""
    print(f"\n========== 测试2: 生成角色列表 (任务ID: {task_id}) ==========")
    
    if not task_id:
        print("❌ 任务ID为空，跳过测试")
        return False
    
    url = f"{BASE_URL}/tasks/{task_id}/generate-characters"
    
    try:
        response = requests.post(url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 显示生成的角色列表
            character_list = data.get("data", {}).get("character_list", [])
            if character_list:
                print(f"\n✅ 成功生成 {len(character_list)} 个角色:")
                for i, character in enumerate(character_list, 1):
                    name = character.get("character_name", "未知")
                    desc = character.get("brief_description", "")
                    print(f"  {i}. {name}: {desc}")
            else:
                print("⚠️  角色列表为空")
            
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def test_get_task(task_id):
    """测试获取任务详情"""
    print(f"\n========== 测试3: 获取任务详情 (任务ID: {task_id}) ==========")
    
    if not task_id:
        print("❌ 任务ID为空，跳过测试")
        return False
    
    url = f"{BASE_URL}/tasks/{task_id}"
    
    try:
        response = requests.get(url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 显示角色列表
            task_data = data.get("data", {})
            character_list = task_data.get("characters", [])
            if character_list:
                print(f"\n✅ 任务中包含 {len(character_list)} 个角色:")
                for i, character in enumerate(character_list, 1):
                    name = character.get("name", "未知")
                    desc = character.get("description", "")
                    print(f"  {i}. {name}: {desc}")
            else:
                print("⚠️  任务中没有角色信息")
            
            print("✅ 任务详情获取成功")
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("开始测试角色列表生成接口")
    print("=" * 60)
    
    # 测试1: 创建任务并生成剧本
    task_id = test_create_task()
    
    if not task_id:
        print("\n⚠️  无法继续测试，因为任务创建失败")
        print("\n可能的原因：")
        print("1. 后端服务未启动")
        print("2. 数据库中没有对应的模板ID或风格ID")
        print("3. 大模型配置有问题")
        return
    
    # 等待用户确认
    input("\n按Enter键继续测试角色列表生成...")
    
    # 测试2: 生成角色列表
    test_generate_characters(task_id)
    
    # 等待用户确认
    input("\n按Enter键继续测试任务详情获取...")
    
    # 测试3: 获取任务详情
    test_get_task(task_id)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n任务ID: {task_id}")
    print(f"可以通过以下URL查看任务详情:")
    print(f"  {BASE_URL}/tasks/{task_id}")


if __name__ == "__main__":
    main()
