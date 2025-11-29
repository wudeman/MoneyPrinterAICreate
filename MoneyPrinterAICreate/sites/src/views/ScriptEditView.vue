<template>
  <div class="script-edit-container">
    <!-- 流程导航 -->
    <FlowNavigation :taskId="taskId" @step-change="handleStepChange" ref="flowNavigation" />
    
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <button @click="goBack" class="back-btn">← 返回首页</button>
      <h2>剧本编辑</h2>
    </div>
    
    <!-- 剧本内容编辑区 -->
    <div class="script-content-wrapper">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>{{ generatingText || '正在生成剧本，请稍候...' }}</p>
      </div>
      
      <div v-else-if="error" class="error-container">
        <p>{{ error }}</p>
        <button @click="generateScript" class="retry-btn">重试</button>
      </div>
      
      <div v-else-if="scriptContent" class="script-editor">
        <textarea 
          v-model="scriptContent" 
          class="script-textarea" 
          placeholder="剧本内容将在这里显示"
        ></textarea>
        <div class="character-count">{{ scriptContent.length }}/5000</div>
      </div>
    </div>
    
    <!-- 底部操作按钮 -->
    <div class="action-buttons">
      <button @click="saveScript" class="secondary-btn">保存剧本</button>
      <button @click="generateScript" class="primary-btn">生成剧本</button>
      <button @click="nextStep" class="primary-btn" v-if="taskId">下一步：角色场景设计 →</button>
    </div>
    
    <!-- 剧本生成参数显示 -->
    <div class="params-info">
      <h3>生成参数</h3>
      <div class="param-item">
        <span class="param-label">创作灵感：</span>
        <span class="param-value">{{ inspiration }}</span>
      </div>
      <div class="param-item" v-if="templateName">
        <span class="param-label">使用模板：</span>
        <span class="param-value">{{ templateName }}</span>
      </div>
      <div class="param-item" v-if="styleName">
        <span class="param-label">使用风格：</span>
        <span class="param-value">{{ styleName }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import FlowNavigation from '../components/FlowNavigation.vue';

const router = useRouter();
const route = useRoute();
const flowNavigation = ref<InstanceType<typeof FlowNavigation>>();

// 任务ID
const taskId = ref('');

// 初始化时从URL获取任务ID，并尝试获取剧本内容
onMounted(async () => {
  const queryTaskId = route.query.taskId as string;
  if (queryTaskId) {
    // 设置任务ID并存储到localStorage
    taskId.value = queryTaskId;
    localStorage.setItem('currentTaskId', queryTaskId);
    
    // 直接获取任务详情而不是轮询
    try {
      loading.value = true;
      const response = await axios.get(`/api/v1/tasks/${taskId.value}`);
      const task = response.data.data;
      
      // 如果已经有剧本内容，直接显示
      if (task && task.script) {
        scriptContent.value = task.script;
      } else {
        error.value = '未找到剧本内容，可以点击"生成剧本"按钮重新生成';
      }
    } catch (error) {
      console.error('获取任务详情失败:', error);
      error.value = '获取任务详情失败，请尝试重新生成剧本';
    } finally {
      loading.value = false;
    }
  } else {
    // 尝试从localStorage获取之前的任务ID
    const savedTaskId = localStorage.getItem('currentTaskId');
    if (savedTaskId) {
      taskId.value = savedTaskId;
      // 可以选择是否自动加载该任务的剧本
    }
  }
});

// 响应式数据
const scriptContent = ref('');
const loading = ref(false);
const error = ref('');
const inspiration = ref('');
const templateName = ref('');
const styleName = ref('');
const generatingText = ref(''); // 用于显示生成进度信息

/**
 * 从URL参数中获取创作灵感和其他参数
 */
const getParamsFromRoute = () => {
  const inspirationParam = route.query.inspiration as string;
  const templateId = route.query.templateId as string;
  const styleId = route.query.styleId as string;
  const templateNameParam = route.query.templateName as string;
  const styleNameParam = route.query.styleName as string;
  
  if (inspirationParam) {
    inspiration.value = inspirationParam;
  }
  
  if (templateNameParam) {
    templateName.value = templateNameParam;
  }
  
  if (styleNameParam) {
    styleName.value = styleNameParam;
  }
  
  return {
    inspiration: inspirationParam,
    templateId,
    styleId
  };
};

/**
 * 生成剧本
 */
const generateScript = async () => {
  if (!inspiration.value.trim()) {
    error.value = '请提供创作灵感';
    return;
  }
  
  loading.value = true;
  error.value = '';
  
  try {
    const params = getParamsFromRoute();
    
    let scriptResponse;
    
    // 检查是否已有任务ID
    if (taskId.value) {
      // 如果已有任务ID，调用/script接口进行重新生成
      generatingText.value = '正在重新生成剧本...';
      scriptResponse = await axios.post('/api/v1/tasks/script', {
        task_id: taskId.value, // 带上任务ID以使用之前的参数
        video_subject: params.inspiration,
        template_id: params.templateId || '',
        style_id: params.styleId || '',
        video_style: params.styleId || '',
        video_language: 'zh',
        paragraph_number: 5
      });
    } else {
      // 如果没有任务ID，创建新任务
      generatingText.value = '正在创建剧本生成任务...';
      scriptResponse = await axios.post('/api/v1/tasks/script', {
        video_subject: params.inspiration,
        template_id: params.templateId || '',
        style_id: params.styleId || '',
        video_style: params.styleId || '',
        video_language: 'zh',
        paragraph_number: 5
      });
      
      // 获取任务ID
      const newTaskId = scriptResponse.data.data?.task_id;
      if (newTaskId) {
        localStorage.setItem('currentTaskId', newTaskId);
        taskId.value = newTaskId;
      }
    }
    
    generatingText.value = '正在获取剧本内容...';
    
    // 直接获取任务详情
    const taskResponse = await axios.get(`/api/v1/tasks/${taskId.value}`);
    const task = taskResponse.data.data;
    
    if (task && task.script) {
      scriptContent.value = task.script;
    } else {
      error.value = '剧本生成可能尚未完成，请稍后刷新页面或重试';
    }
  } catch (err: any) {
    console.error('生成剧本失败:', err);
    error.value = `生成剧本失败: ${err.message || '未知错误'}`;
  } finally {
    loading.value = false;
    generatingText.value = '';
  }
};




/**
 * 保存剧本
 */
const saveScript = async () => {
  if (!taskId.value) {
    console.error('任务ID不存在');
    alert('任务ID不存在，请重新生成剧本');
    return;
  }
  
  if (!scriptContent.value.trim()) {
    alert('剧本内容不能为空');
    return;
  }
  
  try {
    loading.value = true;
    
    // 调用API保存剧本
    const response = await axios.put(`/api/v1/tasks/${taskId.value}/script`, {
      script: scriptContent.value
    });
    
    // 检查响应是否有效
    if (response && response.data) {
      if (response.data.code === 200 || response.data.success === true) {
        // 更新流程导航组件的任务ID
        if (flowNavigation.value) {
          await nextTick();
          flowNavigation.value.updateTaskId(taskId.value);
        }
        
        // 标记剧本完成并保存任务ID到localStorage
        localStorage.setItem('scriptCompleted', 'true');
        localStorage.setItem('currentTaskId', taskId.value);
        
        console.log('剧本保存成功，任务ID:', taskId.value);
        
        // 保存成功不再弹出alert，减少干扰
        return true; // 返回成功状态
      } else {
        const errorMsg = response.data.message || '保存失败，服务器返回错误';
        console.error('保存失败:', errorMsg);
        alert(errorMsg);
        return false;
      }
    } else {
      console.error('保存失败: 无效的服务器响应');
      alert('保存失败，请检查网络连接');
      return false;
    }
  } catch (error: any) {
    console.error('保存剧本失败:', error);
    
    // 更友好的错误提示
    let errorMsg = '保存失败，请重试';
    if (error.response) {
      errorMsg += `: ${error.response.status} - ${error.response.statusText}`;
    } else if (error.message) {
      errorMsg += `: ${error.message}`;
    }
    
    alert(errorMsg);
    return false;
  } finally {
    loading.value = false;
  }
};

/**
 * 处理步骤切换
 */
const handleStepChange = (stepIndex: number) => {
  console.log('切换到步骤:', stepIndex);
  // 可以在这里添加额外的逻辑
};

/**
 * 进入下一步（角色场景设计）
 */
const nextStep = async () => {
  if (!taskId.value) {
    alert('请先生成剧本');
    return;
  }
  
  if (!scriptContent.value.trim()) {
    alert('请先生成或编辑剧本内容');
    return;
  }
  
  try {
    // 先保存当前剧本
    await saveScript();
    
    // 保存任务ID到localStorage，确保在后续步骤中能正确获取
    localStorage.setItem('currentTaskId', taskId.value);
    
    // 跳转到角色场景设计页面
    router.push({
      path: '/character-scene',
      query: {
        taskId: taskId.value,
        script: encodeURIComponent(scriptContent.value) // 编码剧本内容，避免URL参数问题
      }
    });
  } catch (error) {
    console.error('进入下一步失败:', error);
    alert('进入下一步失败，请重试');
  }
};

/**
 * 返回首页
 */
const goBack = () => {
  router.push('/');
};

// 组件挂载时获取参数并生成剧本
onMounted(() => {
  const params = getParamsFromRoute();
  if (params.inspiration) {
    generateScript();
  }
});
</script>

<style scoped>
:root {
  --primary-color: #5d6afb;
  --primary-hover: #4a5af0;
  --secondary-color: #6c757d;
  --secondary-hover: #5a6268;
  --text-primary: #2c3e50;
  --text-secondary: #6c757d;
  --border-color: #e9ecef;
  --bg-color: #f8f9fa;
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  --radius: 12px;
}

* {
  box-sizing: border-box;
}

.script-edit-container {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 顶部导航栏 */
.navbar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.back-btn {
  background: transparent;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

.navbar h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
}

/* 剧本内容编辑区 */
.script-content-wrapper {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 30px;
  margin-bottom: 30px;
  position: relative;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(93, 106, 251, 0.2);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #dc3545;
  text-align: center;
}

.retry-btn {
  margin-top: 15px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.retry-btn:hover {
  background-color: var(--primary-hover);
}

.script-editor {
  position: relative;
}

.script-textarea {
  width: 100%;
  min-height: 400px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  font-size: 16px;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  color: var(--text-primary);
  background-color: white;
}

.script-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(93, 106, 251, 0.2);
}

.character-count {
  position: absolute;
  bottom: 10px;
  right: 20px;
  font-size: 12px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 底部操作按钮 */
.action-buttons {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  justify-content: flex-end;
}

.primary-btn {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  border: none;
  padding: 14px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(93, 106, 251, 0.3);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(93, 106, 251, 0.4);
}

.secondary-btn {
  background: white;
  border: 1px solid var(--secondary-color);
  color: var(--secondary-color);
  padding: 14px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-btn:hover {
  background-color: var(--secondary-color);
  color: white;
}

/* 参数信息显示 */
.params-info {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 25px;
}

.params-info h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.param-item {
  display: flex;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.param-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.param-label {
  font-weight: 600;
  color: var(--text-secondary);
  width: 100px;
  flex-shrink: 0;
}

.param-value {
  color: var(--text-primary);
  flex: 1;
  word-break: break-word;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .script-edit-container {
    padding: 15px;
  }
  
  .script-content-wrapper {
    padding: 20px;
  }
  
  .navbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .navbar h2 {
    font-size: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .primary-btn,
  .secondary-btn {
    width: 100%;
  }
  
  .param-item {
    flex-direction: column;
    gap: 5px;
  }
  
  .param-label {
    width: auto;
  }
}
</style>