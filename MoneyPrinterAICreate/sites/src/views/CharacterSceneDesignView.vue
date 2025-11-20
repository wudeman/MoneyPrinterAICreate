<template>
  <div class="character-scene-container">
    <!-- 流程导航 -->
    <FlowNavigation :taskId="taskId" @step-change="handleStepChange" ref="flowNavigation" />
    
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <button @click="goBack" class="back-btn">← 返回上一步</button>
      <h2>角色与场景设计</h2>
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
      <!-- 左侧：剧本概览 -->
      <div class="script-overview">
        <h3>剧本概览</h3>
        <div class="script-preview">
          <p>{{ formatScriptPreview(script) }}</p>
        </div>
      </div>
      
      <!-- 右侧：角色与场景编辑 -->
      <div class="edit-section">
        <!-- 角色设计 -->
        <div class="character-design">
          <h3>角色设计</h3>
          <div class="character-list">
            <div 
              v-for="(character, index) in characters" 
              :key="index"
              class="character-item"
            >
              <input 
                v-model="character.name"
                placeholder="角色名称"
                class="character-name-input"
              />
              <input 
                v-model="character.description"
                placeholder="角色描述"
                class="character-desc-input"
              />
              <button @click="removeCharacter(index)" class="remove-btn">×</button>
            </div>
            <button @click="addCharacter" class="add-btn">+ 添加角色</button>
          </div>
        </div>
        
        <!-- 场景设计 -->
        <div class="scene-design">
          <h3>场景设计</h3>
          <div class="scene-list">
            <div 
              v-for="(scene, index) in scenes" 
              :key="index"
              class="scene-item"
            >
              <input 
                v-model="scene.name"
                placeholder="场景名称"
                class="scene-name-input"
              />
              <input 
                v-model="scene.description"
                placeholder="场景描述"
                class="scene-desc-input"
              />
              <button @click="removeScene(index)" class="remove-btn">×</button>
            </div>
            <button @click="addScene" class="add-btn">+ 添加场景</button>
          </div>
        </div>
        
        <!-- 背景音乐选择 -->
        <div class="bgm-selection">
          <h3>背景音乐选择</h3>
          <div class="bgm-options">
            <select v-model="bgmType" class="bgm-type-select" @change="handleBgmTypeChange">
              <option value="none">无背景音乐</option>
              <option 
                v-for="(typeInfo, typeKey) in bgmTypes" 
                :key="typeKey" 
                :value="typeKey"
                v-if="typeKey !== 'none' && typeKey !== 'custom'"
              >
                {{ typeInfo.name }} - {{ typeInfo.description }}
              </option>
              <option value="custom">自定义背景音乐</option>
            </select>
            
            <!-- 自定义音乐上传区域 -->
            <div v-if="bgmType === 'custom'" class="custom-bgm-section">
              <input 
                type="file" 
                accept=".mp3,.wav,.ogg"
                class="bgm-file-input"
                @change="handleBgmFileSelect"
              />
              
              <!-- 已上传的背景音乐信息 -->
              <div v-if="savedBgmFileName || customBgmFileName" class="custom-bgm-info">
                <div class="bgm-info-content">
                  <span>已选择: {{ savedBgmFileName || customBgmFileName }}</span>
                  <button 
                    @click="deleteBgm" 
                    class="delete-bgm-btn"
                    :disabled="deletingBgm"
                  >
                    {{ deletingBgm ? '删除中...' : '删除' }}
                  </button>
                </div>
                <div class="audio-player" v-if="savedBgmFileName">
                  <!-- 简单的音频播放提示 -->
                  <small>提示: 实际音频将在视频生成时应用</small>
                </div>
              </div>
              
              <!-- 上传进度 -->
              <div v-if="uploadingBgm" class="upload-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
                </div>
                <span>{{ uploadProgress }}%</span>
              </div>
            </div>
            
            <!-- 预设音乐说明 -->
            <div v-else-if="bgmType !== 'none'" class="preset-bgm-info">
              <div class="bgm-type-description">
                <h4>{{ bgmTypes[bgmType]?.name }}</h4>
                <p>{{ bgmTypes[bgmType]?.description }}</p>
              </div>
              <small>系统将根据选择的类型自动应用合适的背景音乐</small>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部操作按钮 -->
    <div class="action-buttons">
      <button @click="saveDesign" class="secondary-btn">保存设计</button>
      <button @click="nextStep" class="primary-btn">下一步：分镜制作 →</button>
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

// 响应式数据
const loading = ref(false);
const loadingText = ref('');
const error = ref('');
const taskId = ref('');
const script = ref('');
const customBgmFileName = ref('');
const customBgmFile = ref<File | null>(null);

// 角色数据
interface Character {
  name: string;
  description: string;
}
const characters = ref<Character[]>([]);

// 场景数据
interface Scene {
  name: string;
  description: string;
}
const scenes = ref<Scene[]>([]);

// 背景音乐类型
const bgmType = ref('none');

// 预设背景音乐类型列表
const bgmTypes = ref<Record<string, {name: string; description: string}>>({
  none: { name: '无背景音乐', description: '不使用背景音乐' },
  upbeat: { name: '欢快', description: '充满活力的欢快音乐' },
  dramatic: { name: '戏剧性', description: '有张力的戏剧性音乐' },
  emotional: { name: '情感', description: '温柔抒情的音乐' },
  relaxing: { name: '轻松', description: '舒缓放松的音乐' }
});

// 背景音乐上传状态
const uploadingBgm = ref(false);
const uploadProgress = ref(0);
const deletingBgm = ref(false);
const savedBgmFileName = ref('');

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
    
    // 获取预设背景音乐类型
    await loadBgmTypes();
    
    // 获取任务数据
    const response = await axios.get(`/api/v1/tasks/${taskId.value}`);
    const taskData = response.data.data;
    
    if (taskData) {
      // 获取剧本内容
      script.value = taskData.script || (route.query.script as string) || '';
      
      // 如果有已保存的角色场景数据，加载它
      if (taskData.characters) {
        characters.value = JSON.parse(JSON.stringify(taskData.characters));
      } else {
        // 默认添加一些角色
        characters.value = [
          { name: '主角', description: '视频的主要角色' },
          { name: '配角', description: '辅助主角的角色' }
        ];
      }
      
      if (taskData.scenes) {
        scenes.value = JSON.parse(JSON.stringify(taskData.scenes));
      } else {
        // 默认添加一些场景
        scenes.value = [
          { name: '主场景', description: '主要故事发生的地方' },
          { name: '次要场景', description: '辅助情节发展的场景' }
        ];
      }
      
      // 加载背景音乐设置
      if (taskData.bgm_type) {
        bgmType.value = taskData.bgm_type;
      }
      
      // 加载已保存的背景音乐文件名
      if (taskData.bgm_filename) {
        savedBgmFileName.value = taskData.bgm_filename;
      }
      
      // 如果有角色和场景数据，标记为完成
      if (taskData.characters && taskData.scenes) {
        localStorage.setItem('characterSceneCompleted', 'true');
      }
    }
  } catch (err: any) {
    console.error('加载任务数据失败:', err);
    error.value = `加载失败: ${err.message || '未知错误'}`;
  } finally {
    loading.value = false;
    loadingText.value = '';
    
    // 更新流程导航组件
    if (flowNavigation.value) {
      await nextTick();
      flowNavigation.value.loadTaskProgress();
    }
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
 * 格式化剧本预览
 */
const formatScriptPreview = (scriptText: string): string => {
  if (!scriptText) return '无剧本内容';
  
  // 简单处理，取前200个字符
  const preview = scriptText.slice(0, 200);
  return scriptText.length > 200 ? `${preview}...` : preview;
};

/**
 * 添加角色
 */
const addCharacter = () => {
  characters.value.push({ name: '', description: '' });
};

/**
 * 移除角色
 */
const removeCharacter = (index: number) => {
  if (characters.value.length > 1) {
    characters.value.splice(index, 1);
  } else {
    alert('至少保留一个角色');
  }
};

/**
 * 添加场景
 */
const addScene = () => {
  scenes.value.push({ name: '', description: '' });
};

/**
 * 移除场景
 */
const removeScene = (index: number) => {
  if (scenes.value.length > 1) {
    scenes.value.splice(index, 1);
  } else {
    alert('至少保留一个场景');
  }
};

/**
 * 获取预设背景音乐类型
 */
const loadBgmTypes = async () => {
  try {
    const response = await axios.get('/api/v1/bgm/types');
    if (response.data.code === 200 && response.data.data.types) {
      bgmTypes.value = response.data.data.types;
    }
  } catch (error) {
    console.error('获取背景音乐类型失败:', error);
    // 使用默认值作为备选
  }
};

/**
 * 处理背景音乐类型变更
 */
const handleBgmTypeChange = async () => {
  // 如果切换到非自定义类型，清除自定义文件
  if (bgmType.value !== 'custom') {
    customBgmFile.value = null;
    customBgmFileName.value = '';
    
    // 如果之前有保存的自定义音乐，提示用户
    if (savedBgmFileName.value) {
      if (confirm('切换到预设音乐将覆盖之前上传的自定义音乐，确定继续吗？')) {
        await deleteBgm();
      } else {
        // 恢复到custom类型
        bgmType.value = 'custom';
      }
    }
  }
};

/**
 * 处理背景音乐文件选择
 */
const handleBgmFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    
    // 验证文件大小 (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('文件大小不能超过50MB');
      target.value = '';
      return;
    }
    
    // 验证文件类型
    const allowedTypes = ['audio/mp3', 'audio/wav', 'audio/ogg'];
    if (!allowedTypes.includes(file.type)) {
      alert('只支持MP3、WAV、OGG格式的音频文件');
      target.value = '';
      return;
    }
    
    customBgmFile.value = file;
    customBgmFileName.value = file.name;
    
    // 自动上传文件
    await uploadBgmFile(file);
    
    // 清空input，允许选择同一文件
    target.value = '';
  }
};

/**
 * 上传背景音乐文件
 */
const uploadBgmFile = async (file: File) => {
  if (!taskId.value) {
    alert('任务ID不存在');
    return;
  }
  
  uploadingBgm.value = true;
  uploadProgress.value = 0;
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10;
      }
    }, 200);
    
    const response = await axios.post(
      `/api/v1/tasks/${taskId.value}/bgm`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    clearInterval(progressInterval);
    uploadProgress.value = 100;
    
    if (response.data.code === 200) {
      savedBgmFileName.value = file.name;
      customBgmFileName.value = '';
      alert('背景音乐上传成功');
    } else {
      throw new Error(response.data.message || '上传失败');
    }
  } catch (error: any) {
    console.error('上传背景音乐失败:', error);
    alert('上传失败: ' + (error.message || '未知错误'));
  } finally {
    setTimeout(() => {
      uploadingBgm.value = false;
      uploadProgress.value = 0;
    }, 500);
  }
};

/**
 * 删除背景音乐
 */
const deleteBgm = async () => {
  if (!taskId.value || !savedBgmFileName.value) {
    return;
  }
  
  deletingBgm.value = true;
  
  try {
    const response = await axios.delete(`/api/v1/tasks/${taskId.value}/bgm`);
    
    if (response.data.code === 200) {
      savedBgmFileName.value = '';
      customBgmFileName.value = '';
      customBgmFile.value = null;
    }
  } catch (error) {
    console.error('删除背景音乐失败:', error);
  } finally {
    deletingBgm.value = false;
  }
};

/**
 * 保存角色场景设计
 */
const saveDesign = async () => {
  if (!taskId.value) {
    alert('未找到任务ID');
    return;
  }
  
  // 验证必填字段
  const invalidCharacters = characters.value.filter(char => !char.name.trim());
  const invalidScenes = scenes.value.filter(scene => !scene.name.trim());
  
  if (invalidCharacters.length > 0) {
    alert('请填写所有角色的名称');
    return;
  }
  
  if (invalidScenes.length > 0) {
    alert('请填写所有场景的名称');
    return;
  }
  
  loading.value = true;
  try {
    // 准备要保存的数据
    const designData = {
      characters: characters.value,
      scenes: scenes.value,
      bgm_type: bgmType.value
    };
    
    // 调用API保存设计
    await axios.put(`/api/v1/tasks/${taskId.value}/design`, designData);
    
    // 如果有自定义背景音乐，上传文件
    if (bgmType.value === 'custom' && customBgmFile.value) {
      const formData = new FormData();
      formData.append('file', customBgmFile.value);
      
      await axios.post(
        `/api/v1/tasks/${taskId.value}/bgm`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
    }
    
    // 标记角色场景设计完成
    localStorage.setItem('characterSceneCompleted', 'true');
    
    // 更新流程导航组件
    if (flowNavigation.value) {
      await nextTick();
      flowNavigation.value.loadTaskProgress();
    }
    
    alert('设计保存成功');
  } catch (err) {
    console.error('保存设计失败:', err);
    alert('保存失败，请重试');
  } finally {
    loading.value = false;
  }
};

/**
 * 进入下一步（分镜制作）
 */
const nextStep = async () => {
  // 先保存当前设计
  await saveDesign();
  
  // 跳转到分镜制作页面
  localStorage.setItem('currentTaskId', taskId.value);
  router.push({
    path: '/storyboard',
    query: {
      taskId: taskId.value
    }
  });
};

/**
 * 返回上一步
 */
const goBack = () => {
  router.push({
    path: '/script-edit',
    query: {
      taskId: taskId.value
    }
  });
};

// 组件挂载时加载数据
onMounted(() => {
  loadTaskData();
});
</script>

<style scoped>
.character-scene-container {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 顶部导航栏 */
.navbar {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
}

.back-btn {
  background: none;
  border: none;
  color: #5d6afb;
  font-size: 16px;
  cursor: pointer;
  margin-right: 20px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: rgba(93, 106, 251, 0.1);
}

.navbar h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin: 20px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #5d6afb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container p {
  color: #e74c3c;
  margin-bottom: 15px;
}

.retry-btn {
  background-color: #5d6afb;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background-color: #4a5af0;
}

/* 主内容区 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
  margin-bottom: 30px;
}

/* 剧本概览 */
.script-overview {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.script-overview h3 {
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 600;
}

.script-preview {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #5d6afb;
  min-height: 200px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  color: #495057;
  line-height: 1.6;
}

/* 编辑区域 */
.edit-section {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.character-design,
.scene-design,
.bgm-selection {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.character-design h3,
.scene-design h3,
.bgm-selection h3 {
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

/* 角色和场景列表 */
.character-list,
.scene-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.character-item,
.scene-item {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  position: relative;
}

.character-name-input,
.character-desc-input,
.scene-name-input,
.scene-desc-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.character-name-input:focus,
.character-desc-input:focus,
.scene-name-input:focus,
.scene-desc-input:focus {
  outline: none;
  border-color: #5d6afb;
  box-shadow: 0 0 0 2px rgba(93, 106, 251, 0.2);
}

.character-name-input,
.scene-name-input {
  width: 200px;
}

.character-desc-input,
.scene-desc-input {
  flex: 1;
  min-width: 0;
}

.remove-btn {
  background: #e74c3c;
  color: white;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.remove-btn:hover {
  background: #c0392b;
}

.add-btn {
  background: #5d6afb;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.add-btn:hover {
  background: #4a5af0;
}

/* 背景音乐选择 */
.bgm-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bgm-type-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s;
}

.bgm-type-select:focus {
  outline: none;
  border-color: #5d6afb;
  box-shadow: 0 0 0 2px rgba(93, 106, 251, 0.2);
}

.bgm-file-input {
  padding: 10px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s;
}

.bgm-file-input:hover {
  border-color: #5d6afb;
  background: rgba(93, 106, 251, 0.05);
}

.custom-bgm-info {
  font-size: 14px;
  color: #27ae60;
  padding: 10px;
  background: rgba(39, 174, 96, 0.1);
  border-radius: 8px;
}

/* 底部操作按钮 */
.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
}

.primary-btn,
.secondary-btn {
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.primary-btn {
  background-color: #5d6afb;
  color: white;
}

.primary-btn:hover {
  background-color: #4a5af0;
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(93, 106, 251, 0.3);
}

.secondary-btn {
  background-color: #6c757d;
  color: white;
}

.secondary-btn:hover {
  background-color: #5a6268;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .character-item,
  .scene-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .character-name-input,
  .scene-name-input {
    width: 100%;
  }
  
  .remove-btn {
    align-self: flex-end;
    position: absolute;
    top: 10px;
    right: 10px;
  }
}

@media (max-width: 480px) {
  .character-scene-container {
    padding: 15px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .primary-btn,
  .secondary-btn {
    width: 100%;
  }
}
</style>