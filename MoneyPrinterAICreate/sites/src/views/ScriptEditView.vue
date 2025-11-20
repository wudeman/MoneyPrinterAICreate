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

// 初始化时从URL获取任务ID
onMounted(() => {
  const queryTaskId = route.query.taskId as string;
  if (queryTaskId) {
    taskId.value = queryTaskId;
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
  generatingText.value = '正在创建剧本生成任务...';
  
  try {
    const params = getParamsFromRoute();
    
    // 调用后端API创建剧本生成任务
    const response = await axios.post('/api/v1/tasks/script', {
      video_subject: params.inspiration,
      template_id: params.templateId || '',
      style_id: params.styleId || '',
      video_style: params.styleId || '', // 后端需要的必填字段
      video_language: 'zh', // 默认中文
      paragraph_number: 5   // 默认5个段落
    });
    
    // 获取任务ID
    const taskId = response.data.data.task_id;
    localStorage.setItem('currentTaskId', taskId);
    
    generatingText.value = '正在生成剧本，请稍候...';
    
    // 轮询任务状态，直到剧本生成完成
    await pollTaskStatus(taskId);
  } catch (err: any) {
    console.error('生成剧本失败:', err);
    error.value = `生成剧本失败: ${err.message || '未知错误'}`;
  } finally {
    loading.value = false;
    generatingText.value = '';
  }
};

/**
 * 轮询任务状态
 */
const pollTaskStatus = async (taskId: string) => {
  return new Promise((resolve, reject) => {
    const maxRetries = 60; // 最多重试60次（约2分钟）
    let retries = 0;
    
    const checkStatus = async () => {
      retries++;
      
      if (retries > maxRetries) {
        reject(new Error('生成剧本超时，请重试'));
        return;
      }
      
      try {
        const response = await axios.get(`/api/v1/tasks/${taskId}`);
        const task = response.data.data;
        
        // 检查任务状态
        if (task && task.script) {
            scriptContent.value = task.script;
            
            // 更新任务ID
            taskId.value = taskId;
            
            resolve(null);
          } else if (task && task.status === 'failed') {
          reject(new Error('剧本生成失败'));
        } else {
          // 更新进度提示
          if (retries % 5 === 0) {
            generatingText.value = `正在生成剧本，已等待 ${retries * 2} 秒...`;
          }
          // 继续轮询，每2秒检查一次
          setTimeout(checkStatus, 2000);
        }
      } catch (error) {
        console.error('检查任务状态失败:', error);
        // 如果是网络错误，继续尝试
        setTimeout(checkStatus, 2000);
      }
    };
    
    // 开始轮询
    setTimeout(checkStatus, 1000);
  });
};

/**
 * 保存剧本
 */
const saveScript = async () => {
  if (!taskId.value) {
    alert('任务ID不存在');
    return;
  }
  
  if (!scriptContent.value.trim()) {
    alert('剧本内容不能为空');
    return;
  }
  
  try {
    // 调用API保存剧本
    const response = await axios.put(`/api/v1/tasks/${taskId.value}/script`, {
      script: scriptContent.value
    });
    
    if (response.data.code === 200) {
      // 更新流程导航组件的任务ID
      if (flowNavigation.value) {
        await nextTick();
        flowNavigation.value.updateTaskId(taskId.value);
      }
      
      // 标记剧本完成
      localStorage.setItem('scriptCompleted', 'true');
      
      alert('剧本保存成功');
    } else {
      alert('保存失败: ' + response.data.message);
    }
  } catch (error: any) {
    console.error('保存剧本失败:', error);
    alert('保存失败，请重试: ' + (error.message || ''));
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
  
  // 先保存当前剧本
  await saveScript();
  
  // 跳转到角色场景设计页面
  router.push({
    path: '/character-scene',
    query: {
      taskId: taskId.value,
      script: scriptContent.value
    }
  });
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