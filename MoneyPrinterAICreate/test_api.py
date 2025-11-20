import requests
import json
import time
import os

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试结果记录
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

# 任务ID，测试过程中会动态生成
task_id = None

def print_header(title):
    """打印测试标题"""
    print("=" * 60)
    print(f"{title.center(58)}")
    print("=" * 60)

def test_case(func):
    """测试用例装饰器"""
    def wrapper(*args, **kwargs):
        test_results["total"] += 1
        print(f"\n测试: {func.__name__}")
        print("-" * 30)
        try:
            result = func(*args, **kwargs)
            test_results["passed"] += 1
            print(f"✓ 成功: {func.__doc__}")
            return result
        except Exception as e:
            test_results["failed"] += 1
            error_msg = f"✗ 失败: {str(e)}"
            test_results["errors"].append({
                "test": func.__name__,
                "error": str(e)
            })
            print(error_msg)
            return None
    return wrapper

@test_case
def test_create_script():
    """测试创建剧本"""
    global task_id
    
    url = f"{BASE_URL}/tasks/script"
    data = {
        "script": "这是一个测试剧本。\n第一幕：早上的咖啡厅。\n小明走进咖啡厅，点了一杯咖啡。\n服务员：您的咖啡好了。\n小明：谢谢。"
    }
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    assert result.get("code") == 200, f"创建剧本失败: {result}"
    
    task_id = result.get("data", {}).get("task_id")
    assert task_id is not None, "任务ID未返回"
    
    print(f"生成的任务ID: {task_id}")
    return task_id

@test_case
def test_update_character_scene():
    """测试更新角色和场景"""
    assert task_id is not None, "任务ID不存在"
    
    url = f"{BASE_URL}/tasks/{task_id}/character-scene"
    data = {
        "characters": [
            {"name": "小明", "description": "主角，年轻的上班族"},
            {"name": "服务员", "description": "咖啡厅服务员"}
        ],
        "scenes": [
            {"name": "咖啡厅", "description": "一个温馨的街角咖啡厅，阳光透过窗户照射进来"}
        ]
    }
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    assert result.get("code") == 200, f"更新角色场景失败: {result}"
    return True

@test_case
def test_get_task():
    """测试获取任务详情"""
    assert task_id is not None, "任务ID不存在"
    
    url = f"{BASE_URL}/tasks/{task_id}"
    response = requests.get(url)
    response.raise_for_status()
    
    result = response.json()
    assert result.get("code") == 200, f"获取任务详情失败: {result}"
    
    task_data = result.get("data", {})
    assert task_data.get("task_id") == task_id, "返回的任务ID不匹配"
    assert task_data.get("script") is not None, "剧本数据缺失"
    assert len(task_data.get("characters", [])) > 0, "角色数据缺失"
    assert len(task_data.get("scenes", [])) > 0, "场景数据缺失"
    
    print(f"任务数据完整性检查通过")
    return task_data

@test_case
def test_generate_storyboards():
    """测试自动生成分镜"""
    assert task_id is not None, "任务ID不存在"
    
    # 先获取任务数据
    task_data = test_get_task()
    if not task_data:
        raise Exception("无法获取任务数据")
    
    url = f"{BASE_URL}/tasks/script/storyboard"
    data = {
        "script": task_data.get("script", ""),
        "characters": task_data.get("characters", []),
        "scenes": task_data.get("scenes", [])
    }
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    assert result.get("code") == 200, f"生成分镜失败: {result}"
    
    storyboards = result.get("data", {}).get("storyboards", [])
    assert len(storyboards) > 0, "没有生成任何分镜"
    
    print(f"成功生成 {len(storyboards)} 个分镜")
    return storyboards

@test_case
def test_save_storyboards():
    """测试保存分镜"""
    assert task_id is not None, "任务ID不存在"
    
    # 先生成分镜
    storyboards = test_generate_storyboards()
    if not storyboards:
        raise Exception("无法生成分镜")
    
    url = f"{BASE_URL}/tasks/storyboards"
    data = {
        "task_id": task_id,
        "storyboards": storyboards
    }
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    assert result.get("code") == 200, f"保存分镜失败: {result}"
    
    saved_task_id = result.get("data", {}).get("task_id")
    assert saved_task_id == task_id, "保存的任务ID不匹配"
    
    print("分镜保存成功")
    return True

@test_case
def test_get_task_progress():
    """测试获取任务进度"""
    assert task_id is not None, "任务ID不存在"
    
    url = f"{BASE_URL}/tasks/{task_id}/progress"
    response = requests.get(url)
    response.raise_for_status()
    
    result = response.json()
    assert result.get("code") == 200, f"获取任务进度失败: {result}"
    
    progress = result.get("data", {}).get("progress", {})
    assert progress.get("script_completed") is True, "剧本状态错误"
    assert progress.get("character_scene_completed") is True, "角色场景状态错误"
    assert progress.get("storyboard_completed") is True, "分镜状态错误"
    
    print(f"任务进度: {progress}")
    return progress

@test_case
def test_get_bgm_types():
    """测试获取背景音乐类型"""
    assert task_id is not None, "任务ID不存在"
    
    url = f"{BASE_URL}/tasks/{task_id}/bgm-types"
    response = requests.get(url)
    response.raise_for_status()
    
    result = response.json()
    assert result.get("code") == 200, f"获取背景音乐类型失败: {result}"
    
    bgm_types = result.get("data", {}).get("bgm_types", [])
    assert len(bgm_types) > 0, "没有返回任何背景音乐类型"
    
    print(f"获取到 {len(bgm_types)} 种背景音乐类型")
    return bgm_types

def run_all_tests():
    """运行所有测试用例"""
    print_header("MoneyPrinter AI 创建工具 - API 功能测试")
    print(f"测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 按顺序运行测试用例，确保依赖关系
    test_create_script()
    test_update_character_scene()
    test_save_storyboards()  # 这个会调用生成分镜
    test_get_task_progress()
    test_get_bgm_types()
    
    # 打印测试结果摘要
    print("\n" + "=" * 60)
    print(f"测试结果摘要".center(58))
    print("=" * 60)
    print(f"总测试用例数: {test_results['total']}")
    print(f"通过: {test_results['passed']} ✓")
    print(f"失败: {test_results['failed']} ✗")
    
    if test_results['errors']:
        print("\n错误详情:")
        for i, error in enumerate(test_results['errors'], 1):
            print(f"{i}. {error['test']}: {error['error']}")
    
    print("\n" + "=" * 60)
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"测试完成! 成功率: {success_rate:.1f}%")
    
    return test_results['failed'] == 0

if __name__ == "__main__":
    print("注意: 请确保后端服务正在运行 (http://localhost:8000)")
    print("按Enter键开始测试...")
    input()
    
    success = run_all_tests()
    
    # 保存测试报告
    report_file = "api_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: {os.path.abspath(report_file)}")
    
    # 退出码
    exit(0 if success else 1)