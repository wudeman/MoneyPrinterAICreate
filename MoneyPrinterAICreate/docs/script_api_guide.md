# 剧本编辑保存和重新生成接口文档

## 接口概述

本文档描述了两个新增的剧本管理接口，参考 `/tasks/create-and-generate` 接口实现。

## 1. 剧本编辑保存接口

### 接口信息
- **URL**: `/api/v1/tasks/{task_id}/script`
- **方法**: `PUT`
- **描述**: 保存编辑后的剧本内容到数据库

### 请求参数

#### 路径参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | int | 是 | 任务ID（数据库ID） |

#### 请求体（JSON）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| script | string | 是 | 剧本内容 |

### 请求示例

```bash
curl -X PUT "http://localhost:8080/api/v1/tasks/1/script" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "春天来了，万物复苏。\n花朵绽放，鸟儿歌唱。\n这是一个美好的季节。"
  }'
```

### 响应格式

#### 成功响应（200）
```json
{
  "status": 200,
  "message": "success",
  "data": {
    "message": "剧本保存成功",
    "task_id": 1,
    "script": "春天来了，万物复苏。\n花朵绽放，鸟儿歌唱。\n这是一个美好的季节。"
  }
}
```

#### 错误响应

**400 - 剧本内容为空**
```json
{
  "detail": "剧本内容不能为空"
}
```

**404 - 任务不存在**
```json
{
  "detail": "任务ID 1 不存在"
}
```

**500 - 服务器错误**
```json
{
  "detail": "更新剧本失败: [错误信息]"
}
```

### 功能说明
1. 验证剧本内容不为空
2. 检查任务是否存在
3. 更新剧本内容到数据库
4. 更新任务状态为"剧本已完成"（SCRIPT_COMPLETED）
5. 返回更新后的剧本内容

---

## 2. 剧本重新生成接口

### 接口信息
- **URL**: `/api/v1/tasks/{task_id}/regenerate-script`
- **方法**: `POST`
- **描述**: 基于任务原有参数重新生成剧本

### 请求参数

#### 路径参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | int | 是 | 任务ID（数据库ID） |

### 请求示例

```bash
curl -X POST "http://localhost:8080/api/v1/tasks/1/regenerate-script"
```

### 响应格式

#### 成功响应（200）
```json
{
  "status": 200,
  "message": "剧本重新生成成功",
  "data": {
    "task_id": 1,
    "video_idea": "一个关于春天的美好故事",
    "template_id": 1,
    "style_id": 1,
    "duration": 30,
    "script": "春天，是大自然最美的季节...",
    "status": 1
  }
}
```

#### 错误响应

**404 - 任务不存在**
```json
{
  "detail": "任务ID 1 不存在"
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
  "detail": "剧本生成失败: [错误信息]"
}
```

### 功能说明
1. 检查任务是否存在
2. 更新任务状态为"剧本生成中"（SCRIPT_GENERATING）
3. 获取任务的原有参数（video_idea、template_id、style_id、duration）
4. 获取模板配置和默认文本类型大模型
5. 构建提示词并调用LLM生成新剧本
6. 保存新剧本到数据库
7. 更新任务状态为"剧本已完成"（SCRIPT_COMPLETED）
8. 返回完整的任务信息和新生成的剧本

### 与 create-and-generate 的区别
- **create-and-generate**: 创建新任务并生成剧本
- **regenerate-script**: 基于已有任务重新生成剧本

---

## 使用场景

### 场景1: 编辑并保存剧本
用户在前端编辑器中修改剧本后，点击"保存"按钮：

```javascript
async function saveScript(taskId, scriptContent) {
  const response = await axios.put(`/api/v1/tasks/${taskId}/script`, {
    script: scriptContent
  });
  
  if (response.data.status === 200) {
    console.log('剧本保存成功');
  }
}
```

### 场景2: 重新生成剧本
用户对当前剧本不满意，点击"重新生成"按钮：

```javascript
async function regenerateScript(taskId) {
  const response = await axios.post(`/api/v1/tasks/${taskId}/regenerate-script`);
  
  if (response.data.status === 200) {
    const newScript = response.data.data.script;
    console.log('新剧本:', newScript);
    // 更新前端显示
    updateScriptEditor(newScript);
  }
}
```

---

## 数据库变化

### 任务状态变化

#### 剧本编辑保存
```
任何状态 → SCRIPT_COMPLETED (1)
```

#### 剧本重新生成
```
任何状态 → SCRIPT_GENERATING (0) → SCRIPT_COMPLETED (1)
           ↓ (如果失败)
           SCRIPT_FAILED (2)
```

### 更新的字段
- `script`: 剧本内容
- `status`: 任务状态
- `updated_at`: 更新时间（自动）

---

## 注意事项

1. **任务ID类型**: 两个接口都使用数据库中的整型 `task_id`，不是 UUID
2. **状态管理**: 两个接口都会更新任务状态，确保前端及时刷新状态
3. **错误处理**: 建议前端对所有错误情况做适当提示
4. **剧本内容**: 保存时会验证剧本不能为空
5. **重新生成**: 会使用任务创建时的原始参数（video_idea、template_id、style_id、duration）

---

## 测试

使用提供的测试脚本：

```bash
python test_script_endpoints.py
```

测试脚本会依次测试：
1. 创建任务并生成剧本
2. 编辑保存剧本
3. 重新生成剧本
4. 获取任务详情

---

## 相关接口

- `POST /api/v1/tasks/create-and-generate` - 创建任务并生成剧本
- `GET /api/v1/tasks/{task_id}` - 获取任务详情
- `POST /api/v1/tasks/{task_id}/storyboards` - 保存分镜
- `PUT /api/v1/tasks/{task_id}/design` - 保存角色场景设计

---

## 更新日志

**v1.0.0** (2025-11-29)
- 新增剧本编辑保存接口
- 新增剧本重新生成接口
- 参考 `create-and-generate` 接口实现
- 所有代码添加详细中文注释
