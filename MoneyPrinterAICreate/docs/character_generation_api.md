# 角色列表生成接口文档

## 接口概述

本文档描述了角色列表生成接口，参考 `/tasks/create-and-generate` 接口实现。

## 接口信息

- **URL**: `/api/v1/tasks/{task_id}/generate-characters`
- **方法**: `POST`
- **描述**: 根据任务剧本内容和模板配置生成角色列表

## 请求参数

### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | int | 是 | 任务ID（数据库ID） |

## 请求示例

```bash
curl -X POST "http://localhost:8080/api/v1/tasks/1/generate-characters"
```

## 响应格式

### 成功响应（200）

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "id": 1,
    "video_idea": "一个关于春天的美好故事",
    "template_id": 1,
    "style_id": 1,
    "aspect_ratio": "16:9",
    "duration": 30,
    "bgm": null,
    "script": "春天来了，万物复苏...\n花朵绽放，鸟儿歌唱...\n这是一个美好的季节。",
    "character_list": [
      {
        "character_name": "小明",
        "brief_description": "主角，年轻的上班族",
        "appearance_description": "穿着休闲装的年轻人",
        "recommended_voice": "年轻男性音色",
        "character_image_url": ""
      },
      {
        "character_name": "小鸟",
        "brief_description": "森林中的小鸟",
        "appearance_description": "色彩斑斓的小鸟",
        "recommended_voice": "清脆的鸟鸣声",
        "character_image_url": ""
      }
    ],
    "scene_list": null,
    "storyboard_list": null,
    "storyboard_frame_list": null,
    "storyboard_video_list": null,
    "voice_list": null,
    "sound_effect_list": null,
    "status": 1,
    "operator": "system",
    "created_at": "2025-11-29T10:30:00",
    "updated_at": "2025-11-29T10:35:00"
  }
}
```

### 错误响应

**404 - 任务不存在**
```json
{
  "detail": "任务ID 1 不存在"
}
```

**400 - 缺少剧本内容**
```json
{
  "detail": "任务缺少剧本内容，请先生成剧本"
}
```

**400 - 模板缺少角色生成提示词**
```json
{
  "detail": "模板缺少角色生成提示词"
}
```

**404 - 模板不存在**
```json
{
  "detail": "模板ID 1 不存在或已停用"
}
```

**404 - 未找到默认大模型**
```json
{
  "detail": "未找到默认的文本类型大模型，请联系管理员配置"
}
```

**500 - 生成失败**
```json
{
  "detail": "角色列表生成失败: [错误信息]"
}
```

## 功能说明

1. 检查任务是否存在
2. 验证任务是否有剧本内容
3. 获取任务对应的模板配置
4. 检查模板是否有角色生成提示词
5. 获取默认文本类型大模型配置
6. 构建生成角色列表的提示词（包含剧本内容）
7. 调用LLM生成角色列表
8. 解析LLM响应并格式化角色列表
9. 更新角色列表到数据库
10. 返回完整的任务信息

## 实现逻辑

### 1. 参数验证
- 验证任务ID是否存在
- 检查任务是否包含剧本内容

### 2. 模板配置获取
- 根据任务的template_id获取模板
- 验证模板包含角色生成提示词（character_prompt）

### 3. 大模型配置
- 获取默认的文本类型大模型配置
- 支持OpenAI、DeepSeek等模型

### 4. 提示词构建
- 使用模板中的角色生成提示词
- 添加任务的剧本内容作为上下文

### 5. 角色列表生成
- 调用LLM生成角色列表
- 解析响应并转换为标准格式

### 6. 数据库存储
- 更新任务的character_list字段
- 保持与其他任务数据的一致性

## 使用场景

### 场景1: 自动生成角色列表
用户创建任务并生成剧本后，调用此接口自动生成角色列表：

```javascript
async function generateCharacters(taskId) {
  const response = await axios.post(`/api/v1/tasks/${taskId}/generate-characters`);
  
  if (response.data.status === 200) {
    const characterList = response.data.data.character_list;
    console.log('生成的角色列表:', characterList);
    // 更新前端显示
    updateCharacterListDisplay(characterList);
  }
}
```

## 数据库变化

### 更新的字段
- `character_list`: 角色列表JSON数据
- `updated_at`: 更新时间（自动）

## 注意事项

1. **前置条件**: 任务必须已生成剧本内容
2. **模板要求**: 模板必须包含角色生成提示词
3. **模型配置**: 需要正确配置默认文本类型大模型
4. **错误处理**: 建议前端对所有错误情况做适当提示
5. **响应格式**: 返回完整的TaskResponse对象

## 测试

使用提供的测试脚本：

```bash
python test_character_generation.py
```

测试脚本会依次测试：
1. 创建任务并生成剧本
2. 生成角色列表
3. 获取任务详情验证角色列表已保存

## 相关接口

- `POST /api/v1/tasks/create-and-generate` - 创建任务并生成剧本
- `PUT /api/v1/tasks/{task_id}/script` - 保存剧本内容
- `GET /api/v1/tasks/{task_id}` - 获取任务详情

## 更新日志

**v1.0.0** (2025-11-29)
- 新增角色列表生成接口
- 参考 `create-and-generate` 接口实现
- 所有代码添加详细中文注释
