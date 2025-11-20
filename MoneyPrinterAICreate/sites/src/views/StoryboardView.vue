<template>
  <div class="storyboard-container">
    <!-- 流程导航 -->
    <FlowNavigation :taskId="taskId" @step-change="handleStepChange" ref="flowNavigation" />
    
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <button @click="goBack" class="back-btn">← 返回上一步</button>
      <h2>分镜制作</h2>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>{{ loadingText || '加载中...' }}</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="loadTaskData" class="retry-btn">重试</button>
    </div>
    
    <!-- 主内容区 -->
    <div v-else class="main-content">
      <!-- 左侧：项目概览 -->
      <div class="project-overview">
        <h3>项目信息</h3>
        <div class="overview-content">
          <div class="info-item">
            <strong>任务ID:</strong> {{ taskId }}
          </div>
          <div class="info-item">
            <strong>角色数量:</strong> {{ characters.length }}
          </div>
          <div class="info-item">
            <strong>场景数量:</strong> {{ scenes.length }}
          </div>
          <div class="info-item">
            <strong>背景音乐:</strong> {{ getBgmDisplayName() }}
          </div>
          <div class="info-item">
            <strong>分镜数量:</strong> {{ storyboards.length }}
          </div>
        </div>
        
        <!-- 角色列表 -->
        <div class="characters-summary">
          <h4>角色</h4>
          <ul>
            <li v-for="char in characters" :key="char.name">{{ char.name }}</li>
          </ul>
        </div>
        
        <!-- 场景列表 -->
        <div class="scenes-summary">
          <h4>场景</h4>
          <ul>
            <li v-for="scene in scenes" :key="scene.name">{{ scene.name }}</li>
          </ul>
        </div>
      </div>
      
      <!-- 右侧：分镜编辑区 -->
      <div class="storyboard-editor">
        <div class="editor-header">
          <h3>分镜编辑</h3>
          <div class="header-actions">
            <button @click="autoGenerateStoryboards" class="generate-btn">自动生成分镜</button>
            <button @click="addStoryboard" class="add-btn">+ 添加分镜</button>
          </div>
        </div>
        
        <!-- 分镜列表 -->
        <div class="storyboard-list" v-if="storyboards.length > 0">
          <div 
            v-for="(storyboard, index) in storyboards" 
            :key="index"
            class="storyboard-item"
            :class="{ 'selected': selectedIndex === index }"
            @click="selectStoryboard(index)"
          >
            <!-- 分镜预览 -->
            <div class="storyboard-preview">
              <div class="frame-number">#{{ index + 1 }}</div>
              <div class="preview-content">
                <div class="scene-name">{{ storyboard.scene || '未选择场景' }}</div>
                <div class="character-actions">{{ storyboard.actions || '无动作描述' }}</div>
              </div>
              <div class="storyboard-controls">
                <button 
                  @click.stop="moveStoryboard(index, 'up')"
                  class="control-btn" 
                  :disabled="index === 0"
                  title="上移"
                >↑</button>
                <button 
                  @click.stop="moveStoryboard(index, 'down')"
                  class="control-btn" 
                  :disabled="index === storyboards.length - 1"
                  title="下移"
                >↓</button>
                <button 
                  @click.stop="removeStoryboard(index)"
                  class="control-btn delete-btn"
                  title="删除"
                >×</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-state">
          <p>暂无分镜，请点击添加分镜按钮开始创建</p>
        </div>
        
        <!-- 分镜详情编辑 -->
        <div v-if="selectedStoryboard && selectedIndex !== -1" class="storyboard-detail">
          <h3>分镜详情</h3>
          
          <div class="form-group">
            <label>选择场景</label>
            <select v-model="selectedStoryboard.scene" class="form-control">
              <option value="">请选择场景</option>
              <option v-for="scene in scenes" :key="scene.name" :value="scene.name">
                {{ scene.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>参与角色</label>
            <div class="checkbox-group">
              <label v-for="char in characters" :key="char.name" class="checkbox-label">
                <input 
                  type="checkbox" 
                  :value="char.name" 
                  v-model="selectedStoryboard.characters"
                />
                {{ char.name }}
              </label>
            </div>
          </div>
          
          <div class="form-group">
            <label>动作描述</label>
            <textarea 
              v-model="selectedStoryboard.actions" 
              class="form-control" 
              rows="3"
              placeholder="描述此分镜中角色的动作和对话"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>时长 (秒)</label>
            <input 
              v-model.number="selectedStoryboard.duration" 
              type="number" 
              class="form-control"
              min="1"
              max="60"
              placeholder="1-60秒"
            />
          </div>
          
          <div class="form-group">
            <label>画面描述</label>
            <textarea 
              v-model="selectedStoryboard.description" 
              class="form-control" 
              rows="3"
              placeholder="详细描述画面内容、构图、镜头运用等"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>特效说明</label>
            <textarea 
              v-model="selectedStoryboard.effects" 
              class="form-control" 
              rows="2"
              placeholder="特殊效果要求"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button @click="updateStoryboard" class="save-btn">保存分镜</button>
            <button @click="duplicateStoryboard" class="duplicate-btn">复制分镜</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部操作按钮 -->
    <div class="action-buttons">
      <button @click="saveAllStoryboards" class="secondary-btn">保存所有分镜</button>
      <button @click="nextStep" class="primary-btn">下一步 →</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import FlowNavigation from '../components/FlowNavigation.vue';

const router = useRouter();
const route = useRoute();
const flowNavigation = ref<InstanceType<typeof FlowNavigation>>();

// 状态变量
const taskId = ref('');
const loading = ref(false);
const loadingText = ref('');
const error = ref('');
const script = ref('');
const generatingStoryboards = ref(false);
const isStoryboardSaved = ref(false);

// 项目数据
const characters = ref<Array<{ name: string; description: string }>>([]);
const scenes = ref<Array<{ name: string; description: string }>>([]);
const bgmType = ref('none');
const bgmFileName = ref('');

// 分镜数据
interface Storyboard {
  scene: string;
  characters: string[];
  actions: string;
  duration: number;
  description: string;
  effects: string;
  // 可能的扩展字段
  cameraAngle?: string;
  transition?: string;
}

const storyboards = ref<Storyboard[]>([]);
const selectedIndex = ref(-1);
const selectedStoryboard = computed(() => {
  return selectedIndex.value >= 0 && selectedIndex.value < storyboards.value.length 
    ? storyboards.value[selectedIndex.value] 
    : null;
});

/**
 * 获取背景音乐显示名称
 */
const getBgmDisplayName = (): string => {
  if (bgmType.value === 'none') return '无背景音乐';
  if (bgmType.value === 'custom' && bgmFileName.value) return bgmFileName.value;
  
  const bgmTypeMap: Record<string, string> = {
    upbeat: '欢快',
    dramatic: '戏剧性',
    emotional: '情感',
    relaxing: '轻松'
  };
  
  return bgmTypeMap[bgmType.value] || bgmType.value;
};

/**
 * 加载任务数据
 */
const loadTaskData = async () => {
  loading.value = true;
  error.value = '';
  loadingText.value = '加载任务数据中...';
  
  try {
    // 从URL参数或localStorage获取taskId
    const queryTaskId = route.query.taskId as string;
    taskId.value = queryTaskId || localStorage.getItem('currentTaskId') || '';
    
    if (!taskId.value) {
      throw new Error('未找到任务ID');
    }
    
    // 获取任务数据
    const response = await axios.get(`/api/v1/tasks/${taskId.value}`);
    const taskData = response.data.data;
    
    if (taskData) {
      // 加载基础数据
      script.value = taskData.script || '';
      
      // 加载角色和场景
      if (taskData.characters) {
        characters.value = JSON.parse(JSON.stringify(taskData.characters));
      }
      
      if (taskData.scenes) {
        scenes.value = JSON.parse(JSON.stringify(taskData.scenes));
      }
      
      // 加载背景音乐设置
      if (taskData.bgm_type) {
        bgmType.value = taskData.bgm_type;
      }
      if (taskData.bgm_filename) {
        bgmFileName.value = taskData.bgm_filename;
      }
      
      // 加载分镜数据
      if (taskData.storyboards) {
        storyboards.value = JSON.parse(JSON.stringify(taskData.storyboards));
        if (storyboards.value.length > 0) {
          selectedIndex.value = 0;
        }
        isStoryboardSaved.value = true;
        localStorage.setItem('storyboardCompleted', 'true');
      } else {
        // 如果没有分镜数据，自动根据场景生成基础分镜
        generateInitialStoryboards();
      }
      
      // 默认选中第一个分镜
      if (storyboards.value.length > 0) {
        selectedIndex.value = 0;
      }
      
      // 更新流程导航组件
      if (flowNavigation.value) {
        await nextTick();
        flowNavigation.value.loadTaskProgress();
      }
    }
  } catch (err: any) {
    console.error('加载任务数据失败:', err);
    error.value = `加载失败: ${err.message || '未知错误'}`;
  } finally {
    loading.value = false;
    loadingText.value = '';
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
 * 根据场景自动生成初始分镜
 */
const generateInitialStoryboards = () => {
  if (scenes.value.length === 0) return;
  
  // 为每个场景创建一个基础分镜
  storyboards.value = scenes.value.map(scene => ({
    scene: scene.name,
    characters: [],
    actions: '',
    duration: 5,
    description: '',
    effects: ''
  }));
};

/**
 * 自动生成分镜
 */
const autoGenerateStoryboards = async () => {
  if (!script.value.trim()) {
    alert('没有剧本内容，无法自动生成分镜');
    return;
  }
  
  if (confirm('自动生成分镜将覆盖当前所有分镜，确定继续吗？')) {
    generatingStoryboards.value = true;
    
    try {
      // 调用API生成分镜
      const response = await axios.post('/api/v1/tasks/script/storyboard', {
        script: script.value,
        characters: characters.value,
        scenes: scenes.value
      });
      
      if (response.data.code === 200 && response.data.data.storyboards) {
        storyboards.value = response.data.data.storyboards;
        selectedIndex.value = 0;
        alert('分镜自动生成成功');
      } else {
        throw new Error(response.data.message || '生成失败');
      }
    } catch (err: any) {
      console.error('自动生成分镜失败:', err);
      
      // 降级方案：基于简单规则自动生成
      alert('API生成失败，将使用本地规则生成分镜');
      generateSimpleStoryboards();
    } finally {
      generatingStoryboards.value = false;
    }
  }
};

/**
 * 简单的本地分镜生成规则
 */
const generateSimpleStoryboards = () => {
  if (!script.value) return;
  
  // 将剧本按段落分割
  const paragraphs = script.value.split('\n').filter(p => p.trim());
  const newStoryboards: Storyboard[] = [];
  
  // 简单规则：每2-3个段落生成一个分镜
  for (let i = 0; i < paragraphs.length; i += Math.floor(Math.random() * 2) + 2) {
    const segment = paragraphs.slice(i, i + Math.floor(Math.random() * 2) + 2).join(' ');
    
    // 尝试从段落中识别场景
    let sceneName = scenes.value[0]?.name || '';
    for (const scene of scenes.value) {
      if (segment.includes(scene.name)) {
        sceneName = scene.name;
        break;
      }
    }
    
    // 尝试识别角色
    const charNames = [];
    for (const char of characters.value) {
      if (segment.includes(char.name)) {
        charNames.push(char.name);
      }
    }
    
    // 生成分镜
    newStoryboards.push({
      scene: sceneName,
      characters: charNames.length > 0 ? charNames : [],
      actions: segment.length > 100 ? segment.substring(0, 100) + '...' : segment,
      duration: 5 + Math.floor(Math.random() * 6), // 5-10秒
      description: `基于剧本段落 ${i+1}-${Math.min(i+3, paragraphs.length)} 生成的画面`,
      effects: ''
    });
  }
  
  storyboards.value = newStoryboards;
  if (storyboards.value.length > 0) {
    selectedIndex.value = 0;
  }
};

/**
 * 选择分镜
 */
const selectStoryboard = (index: number) => {
  selectedIndex.value = index;
};

/**
 * 添加分镜
 */
const addStoryboard = () => {
  const newStoryboard: Storyboard = {
    scene: scenes.value.length > 0 ? scenes.value[0].name : '',
    characters: [],
    actions: '',
    duration: 5,
    description: '',
    effects: ''
  };
  
  storyboards.value.push(newStoryboard);
  selectedIndex.value = storyboards.value.length - 1;
};

/**
 * 删除分镜
 */
const removeStoryboard = (index: number) => {
  if (confirm('确定要删除这个分镜吗？')) {
    storyboards.value.splice(index, 1);
    
    // 更新选中状态
    if (selectedIndex.value === index) {
      selectedIndex.value = Math.min(index, storyboards.value.length - 1);
    } else if (selectedIndex.value > index) {
      selectedIndex.value--;
    }
  }
};

/**
 * 移动分镜位置
 */
const moveStoryboard = (index: number, direction: 'up' | 'down') => {
  if (direction === 'up' && index > 0) {
    // 上移
    [storyboards.value[index - 1], storyboards.value[index]] = 
      [storyboards.value[index], storyboards.value[index - 1]];
    selectedIndex.value = index - 1;
  } else if (direction === 'down' && index < storyboards.value.length - 1) {
    // 下移
    [storyboards.value[index], storyboards.value[index + 1]] = 
      [storyboards.value[index + 1], storyboards.value[index]];
    selectedIndex.value = index + 1;
  }
};

/**
 * 复制分镜
 */
const duplicateStoryboard = () => {
  if (!selectedStoryboard.value) return;
  
  const newStoryboard = JSON.parse(JSON.stringify(selectedStoryboard.value));
  storyboards.value.splice(selectedIndex.value + 1, 0, newStoryboard);
  selectedIndex.value += 1;
};

/**
 * 更新当前选中的分镜
 */
const updateStoryboard = () => {
  // 因为我们直接编辑的是数组中的对象，Vue会自动响应更新
  // 这里主要做一些验证
  if (!selectedStoryboard.value) return;
  
  // 确保时长为数字
  if (!selectedStoryboard.value.duration || selectedStoryboard.value.duration < 1) {
    selectedStoryboard.value.duration = 5;
  }
  
  alert('分镜已更新');
};

/**
 * 保存所有分镜
 */
const saveAllStoryboards = async () => {
  if (!taskId.value) {
    alert('任务ID不存在');
    return;
  }
  
  loading.value = true;
  loadingText.value = '保存分镜中...';
  
  try {
    const response = await axios.post(`/api/v1/tasks/${taskId.value}/storyboards`, {
      storyboards: storyboards.value
    });
    
    if (response.data.code === 200) {
    // 标记分镜完成
    localStorage.setItem('storyboardCompleted', 'true');
    
    // 更新流程导航组件
    if (flowNavigation.value) {
      await nextTick();
      flowNavigation.value.loadTaskProgress();
    }
    
    alert('所有分镜已保存');
    isStoryboardSaved.value = true;
    // 更新任务状态
    localStorage.setItem('currentTaskId', taskId.value);
  } else {
      throw new Error(response.data.message || '保存失败');
    }
  } catch (err: any) {
    console.error('保存分镜失败:', err);
    alert('保存失败: ' + (err.message || '未知错误'));
  } finally {
    loading.value = false;
    loadingText.value = '';
  }
};

/**
 * 下一步
 */
const nextStep = async () => {
  if (!isStoryboardSaved.value) {
    // 如果还没保存，先保存分镜
    await saveAllStoryboards();
  }
  
  // 检查是否成功保存
  if (isStoryboardSaved.value) {
    // 跳转到模型管理页面
    router.push({
      path: '/model-management',
      query: { taskId: taskId.value }
    });
  }
};

/**
 * 返回上一步
 */
const goBack = () => {
  router.push('/character-scene');
};

/**
 * 下一步：生成画面和配音
 */
const nextStep = async () => {
  if (storyboards.value.length === 0) {
    alert('请至少创建一个分镜');
    return;
  }
  
  // 先保存所有分镜
  await saveAllStoryboards();
  
  // 跳转到下一步
  localStorage.setItem('currentTaskId', taskId.value);
  router.push({ 
    path: '/visual-audio', 
    query: { taskId: taskId.value } 
  });
};

// 组件挂载时加载数据
onMounted(() => {
  loadTaskData();
});
</script>

<style scoped>
.storyboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 导航栏 */
.navbar {
  display: flex;
  align-items: center;
  padding: 1rem 2rem;
  background: #1e293b;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar h2 {
  margin: 0 0 0 1rem;
  font-size: 1.5rem;
}

.back-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #2563eb;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误提示 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  gap: 1rem;
  color: #ef4444;
}

.retry-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  padding: 1rem;
  gap: 1rem;
  overflow: hidden;
}

/* 项目概览 */
.project-overview {
  width: 250px;
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  overflow-y: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.project-overview h3 {
  margin-top: 0;
  color: #1e293b;
}

.project-overview h4 {
  margin-bottom: 0.5rem;
  color: #334155;
}

.overview-content {
  margin-bottom: 1rem;
}

.info-item {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #64748b;
}

.characters-summary, .scenes-summary {
  margin-bottom: 1rem;
}

.characters-summary ul, .scenes-summary ul {
  margin: 0;
  padding-left: 1.5rem;
  font-size: 0.9rem;
  color: #64748b;
}

/* 分镜编辑器 */
.storyboard-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-header h3 {
  margin: 0;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.generate-btn {
  background: #8b5cf6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.generate-btn:hover {
  background: #7c3aed;
}

.generate-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.add-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.add-btn:hover {
  background: #059669;
}

/* 分镜列表 */
.storyboard-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

/* 生成状态覆盖层 */
.storyboard-list::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #3b82f6;
  visibility: hidden;
  opacity: 0;
  transition: visibility 0s, opacity 0.3s;
}

.storyboard-list.generating::after {
  visibility: visible;
  opacity: 1;
  content: '正在生成分镜...';
}

.storyboard-item {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.storyboard-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.storyboard-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.storyboard-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.frame-number {
  background: #3b82f6;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.preview-content {
  flex: 1;
}

.scene-name {
  font-weight: bold;
  color: #1e293b;
}

.character-actions {
  font-size: 0.9rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.storyboard-controls {
  display: flex;
  gap: 0.25rem;
}

.control-btn {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.control-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.delete-btn:hover:not(:disabled) {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
}

/* 分镜详情 */
.storyboard-detail {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  overflow-y: auto;
  flex: 1;
}

.storyboard-detail h3 {
  margin-top: 0;
  color: #1e293b;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #334155;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.save-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.save-btn:hover {
  background: #2563eb;
}

.duplicate-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.duplicate-btn:hover {
  background: #4f46e5;
}

/* 底部操作按钮 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 2rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.primary-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.primary-btn:hover {
  background: #2563eb;
}

.secondary-btn {
  background: #64748b;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.secondary-btn:hover {
  background: #475569;
}
</style>