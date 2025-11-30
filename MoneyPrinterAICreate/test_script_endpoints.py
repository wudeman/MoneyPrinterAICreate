"""
测试剧本编辑保存和重新生成接口

使用方法：
1. 确保后端服务已启动（python main.py）
2. 运行此测试脚本: python test_script_endpoints.py
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


def test_update_script(task_id):
    """测试更新剧本接口"""
    print(f"\n========== 测试2: 更新剧本 (任务ID: {task_id}) ==========")
    
    if not task_id:
        print("❌ 任务ID为空，跳过测试")
        return False
    
    url = f"{BASE_URL}/tasks/{task_id}/script"
    
    # 修改后的剧本内容
    updated_script = """
春天到了，万物复苏。
小鸟在枝头欢快地歌唱。
花朵绽放，散发着迷人的香气。
孩子们在草地上奔跑嬉戏。
这是一个充满希望和生机的季节。

（这是通过API编辑保存的剧本）
"""
    
    payload = {
        "script": updated_script.strip()
    }
    
    try:
        response = requests.put(url, json=payload)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 剧本更新成功")
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def test_regenerate_script(task_id):
    """测试重新生成剧本接口"""
    print(f"\n========== 测试3: 重新生成剧本 (任务ID: {task_id}) ==========")
    
    if not task_id:
        print("❌ 任务ID为空，跳过测试")
        return False
    
    url = f"{BASE_URL}/tasks/{task_id}/regenerate-script"
    
    try:
        response = requests.post(url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 剧本重新生成成功")
            
            # 显示新生成的剧本片段（前200个字符）
            new_script = data.get("data", {}).get("script", "")
            if new_script:
                print(f"\n新生成的剧本（前200字符）:\n{new_script[:200]}...")
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def test_get_task(task_id):
    """测试获取任务详情"""
    print(f"\n========== 测试4: 获取任务详情 (任务ID: {task_id}) ==========")
    
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
    print("开始测试剧本编辑保存和重新生成接口")
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
    input("\n按Enter键继续测试剧本编辑保存...")
    
    # 测试2: 更新剧本
    test_update_script(task_id)
    
    # 等待用户确认
    input("\n按Enter键继续测试剧本重新生成...")
    
    # 测试3: 重新生成剧本
    test_regenerate_script(task_id)
    
    # 测试4: 获取任务详情
    test_get_task(task_id)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n任务ID: {task_id}")
    print(f"可以通过以下URL查看任务详情:")
    print(f"  {BASE_URL}/tasks/{task_id}")


if __name__ == "__main__":
    main()
