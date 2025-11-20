<template>
  <div class="media-generation-container">
    <FlowNavigation ref="flowNavigation" @step-change="handleStepChange" />
    
    <div class="main-content">
      <div class="header">
        <button @click="goBack" class="back-button">
          <span class="back-icon">←</span>
          返回分镜编辑
        </button>
        <h1>画面生成与配音</h1>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>{{ loadingMessage || '加载中...' }}</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <p class="error-message">{{ error }}</p>
        <button @click="loadTaskData" class="retry-button">重试</button>
      </div>
      
      <!-- 主内容 -->
      <div v-else class="content">
        <!-- 任务信息 -->
        <div class="task-info">
          <h2>任务信息</h2>
          <p>任务ID: {{ taskId }}</p>
          <p>状态: {{ taskStatusText }}</p>
        </div>
        
        <!-- 分镜列表 -->
        <div class="storyboards-section">
          <h2>分镜列表</h2>
          <div class="storyboard-tabs">
            <div 
              v-for="(storyboard, index) in storyboards" 
              :key="index"
              class="storyboard-tab"
              :class="{ active: activeStoryboardIndex === index }"
              @click="switchStoryboard(index)"
            >
              <span class="tab-number">{{ index + 1 }}</span>
              <span class="tab-title">{{ truncateText(storyboard.description, 20) }}</span>
              <span v-if="storyboard.media_status === 'completed'" class="tab-status success">✓</span>
              <span v-else-if="storyboard.media_status === 'processing'" class="tab-status processing">⏳</span>
              <span v-else class="tab-status pending">○</span>
            </div>
          </div>
        </div>
        
        <!-- 当前分镜编辑 -->
        <div v-if="activeStoryboard" class="storyboard-editor">
          <div class="editor-content">
            <!-- 左侧：画面生成 -->
            <div class="media-panel">
              <h3>画面生成</h3>
              
              <!-- 画面预览 -->
              <div class="preview-container">
                <div v-if="activeStoryboard.image_url" class="image-preview">
                  <img :src="activeStoryboard.image_url" :alt="activeStoryboard.description" />
                  <div class="preview-actions">
                    <button @click="regenerateImage" :disabled="isGeneratingImage" class="action-button">
                      {{ isGeneratingImage ? '重新生成中...' : '重新生成' }}
                    </button>
                    <button @click="customizeImage" class="action-button secondary">
                      自定义
                    </button>
                  </div>
                </div>
                <div v-else class="no-image">
                  <div class="no-image-placeholder">📷</div>
                  <p>暂无生成的画面</p>
                </div>
              </div>
              
              <!-- 画面生成选项 -->
              <div class="generation-options">
                <div class="option-group">
                  <label>生成提示词</label>
                  <textarea 
                    v-model="imagePrompt" 
                    class="prompt-input"
                    :disabled="isGeneratingImage"
                    placeholder="输入画面生成提示词"
                  ></textarea>
                </div>
                
                <div class="option-row">
                  <div class="option-group half">
                    <label>模型选择</label>
                    <select v-model="selectedImageModel" :disabled="isGeneratingImage" class="select-input">
                      <option value="dall-e-3">DALL-E 3</option>
                      <option value="midjourney">MidJourney</option>
                      <option value="stable-diffusion">Stable Diffusion</option>
                    </select>
                  </div>
                  
                  <div class="option-group half">
                    <label>风格选择</label>
                    <select v-model="imageStyle" :disabled="isGeneratingImage" class="select-input">
                      <option value="realistic">写实风格</option>
                      <option value="cartoon">卡通风格</option>
                      <option value="anime">动漫风格</option>
                      <option value="painting">油画风格</option>
                    </select>
                  </div>
                </div>
                
                <button 
                  @click="generateImage" 
                  :disabled="isGeneratingImage || !imagePrompt"
                  class="generate-button"
                >
                  {{ isGeneratingImage ? '生成中...' : '生成画面' }}
                </button>
              </div>
            </div>
            
            <!-- 右侧：配音编辑 -->
            <div class="voice-panel">
              <h3>配音编辑</h3>
              
              <!-- 配音内容 -->
              <div class="voice-content">
                <div class="option-group">
                  <label>对白文本</label>
                  <textarea 
                    v-model="activeStoryboard.dialogue" 
                    class="dialogue-input"
                    placeholder="输入对白文本"
                    @input="updateDialogue"
                  ></textarea>
                </div>
                
                <div class="option-row">
                  <div class="option-group half">
                    <label>角色选择</label>
                    <select v-model="selectedCharacter" class="select-input">
                      <option v-for="character in characters" :key="character.name" :value="character.name">
                        {{ character.name }}
                      </option>
                    </select>
                  </div>
                  
                  <div class="option-group half">
                    <label>语音类型</label>
                    <select v-model="voiceType" class="select-input">
                      <option value="male">男声</option>
                      <option value="female">女声</option>
                      <option value="child">童声</option>
                      <option value="elder">老人</option>
                    </select>
                  </div>
                </div>
                
                <div class="option-row">
                  <div class="option-group half">
                    <label>语音提供商</label>
                    <select v-model="voiceProvider" class="select-input">
                      <option value="edge-tts">Edge TTS</option>
                      <option value="openai">OpenAI</option>
                      <option value="azure">Azure</option>
                    </select>
                  </div>
                  
                  <div class="option-group half">
                    <label>语速</label>
                    <input 
                      type="range" 
                      v-model.number="voiceSpeed" 
                      min="0.5" 
                      max="2" 
                      step="0.1"
                      class="range-input"
                    />
                    <span class="range-value">{{ voiceSpeed.toFixed(1) }}</span>
                  </div>
                </div>
                
                <!-- 音频控制 -->
                <div class="audio-controls">
                  <button 
                    @click="generateVoice" 
                    :disabled="isGeneratingVoice || !activeStoryboard.dialogue"
                    class="generate-button"
                  >
                    {{ isGeneratingVoice ? '生成中...' : '生成配音' }}
                  </button>
                  
                  <div v-if="activeStoryboard.voice_url" class="audio-player">
                    <audio :src="activeStoryboard.voice_url" controls></audio>
                    <button @click="regenerateVoice" :disabled="isGeneratingVoice" class="action-button secondary">
                      重新生成
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 动效设置 -->
          <div class="effects-panel">
            <h3>动效设置</h3>
            
            <div class="effects-grid">
              <div 
                v-for="effect in effects" 
                :key="effect.id"
                class="effect-item"
                :class="{ active: activeStoryboard.effects.includes(effect.id) }"
                @click="toggleEffect(effect.id)"
              >
                <div class="effect-icon">{{ effect.icon }}</div>
                <div class="effect-name">{{ effect.name }}</div>
              </div>
            </div>
            
            <!-- 动效预览 -->
            <div class="effect-preview">
              <h4>动效组合预览</h4>
              <div class="preview-text">
                当前选择的动效：
                <span v-for="(effectId, index) in activeStoryboard.effects" :key="effectId">
                  {{ getEffectName(effectId) }}{{ index < activeStoryboard.effects.length - 1 ? '、' : '' }}
                </span>
                <span v-if="activeStoryboard.effects.length === 0">无</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 批量操作 -->
        <div class="batch-operations">
          <h3>批量操作</h3>
          <div class="operation-buttons">
            <button @click="batchGenerateImages" :disabled="isGeneratingImages" class="batch-button">
              {{ isGeneratingImages ? '批量生成画面中...' : '批量生成所有画面' }}
            </button>
            <button @click="batchGenerateVoices" :disabled="isGeneratingVoices" class="batch-button">
              {{ isGeneratingVoices ? '批量生成配音中...' : '批量生成所有配音' }}
            </button>
            <button @click="applyDefaultEffects" class="batch-button secondary">
              应用默认动效
            </button>
          </div>
        </div>
        
        <!-- 底部操作 -->
        <div class="bottom-actions">
          <button @click="saveAllChanges" :disabled="isSaving" class="save-button">
            {{ isSaving ? '保存中...' : '保存所有更改' }}
          </button>
          <button @click="nextStep" :disabled="isSaving || !canProceed" class="next-button">
            下一步：视频合成 →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import FlowNavigation from '../components/FlowNavigation.vue';

// Props and Emits
const emit = defineEmits(['update-task-id', 'update-status']);

// Router and Route
const router = useRouter();
const route = useRoute();

// Refs
const flowNavigation = ref<InstanceType<typeof FlowNavigation> | null>(null);

// State
const taskId = ref<string | null>(null);
const storyboards = ref<any[]>([]);
const activeStoryboardIndex = ref(0);
const characters = ref<any[]>([]);
const scenes = ref<any[]>([]);
const isLoading = ref(true);
const loadingMessage = ref('');
const error = ref<string | null>(null);
const isSaving = ref(false);
const isGeneratingImage = ref(false);
const isGeneratingImages = ref(false);
const isGeneratingVoice = ref(false);
const isGeneratingVoices = ref(false);
const imagePrompt = ref('');
const selectedImageModel = ref('dall-e-3');
const imageStyle = ref('realistic');
const selectedCharacter = ref('');
const voiceType = ref('male');
const voiceProvider = ref('edge-tts');
const voiceSpeed = ref(1.0);
const voiceName = ref('zh-CN-XiaoxiaoNeural-Female');
const voiceVolume = ref(1.0);
const isMediaGenerationCompleted = ref(false);

// 动效列表
const effects = ref([
  { id: 'fade_in', name: '淡入', icon: '🔄' },
  { id: 'fade_out', name: '淡出', icon: '🔄' },
  { id: 'zoom_in', name: '放大', icon: '🔍' },
  { id: 'zoom_out', name: '缩小', icon: '🔍' },
  { id: 'pan_left', name: '左移', icon: '←' },
  { id: 'pan_right', name: '右移', icon: '→' },
  { id: 'shake', name: '摇晃', icon: '⚡' },
  { id: 'blur', name: '模糊', icon: '🌫️' }
]);

// Computed
const activeStoryboard = computed(() => {
  return storyboards.value[activeStoryboardIndex.value] || null;
});

const taskStatusText = computed(() => {
  if (isLoading.value) return '加载中';
  if (error.value) return '错误';
  return '编辑中';
});

const canProceed = computed(() => {
  // 检查是否所有分镜都已完成媒体生成
  return storyboards.value.every(sb => 
    sb.image_url && 
    sb.voice_url && 
    sb.media_status === 'completed'
  );
});

// Methods
const loadTaskData = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    loadingMessage.value = '加载任务数据...';
    
    // 从路由参数或本地存储获取任务ID
    const taskIdParam = route.query.taskId as string || localStorage.getItem('currentTaskId');
    if (!taskIdParam) {
      throw new Error('任务ID不存在');
    }
    
    taskId.value = taskIdParam;
    localStorage.setItem('currentTaskId', taskIdParam);
    
    // 更新导航组件
    await nextTick();
    if (flowNavigation.value) {
      flowNavigation.value.updateTaskId(taskIdParam);
    }
    
    // 加载任务数据
    const response = await axios.get(`/api/v1/tasks/${taskIdParam}`);
    
    if (response.data.code === 200) {
      const taskData = response.data.data;
      
      // 加载分镜数据
      storyboards.value = taskData.storyboards || [];
      
      // 初始化分镜的媒体状态和动效
      storyboards.value.forEach(sb => {
        if (!sb.media_status) {
          sb.media_status = 'pending';
        }
        if (!sb.effects) {
          sb.effects = [];
        }
      });
      
      // 加载角色和场景数据
      characters.value = taskData.characters || [];
      scenes.value = taskData.scenes || [];
      
      // 设置默认选中的角色
      if (characters.value.length > 0) {
        selectedCharacter.value = characters.value[0].name;
      }
      
      // 更新导航状态
      emit('update-task-id', taskIdParam);
      emit('update-status', 'media_generation_in_progress');
      
    } else {
      throw new Error(response.data.message || '加载任务数据失败');
    }
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败，请重试';
    console.error('加载任务数据失败:', err);
  } finally {
    isLoading.value = false;
  }
};

const switchStoryboard = (index: number) => {
  activeStoryboardIndex.value = index;
  
  // 更新画面提示词
  if (activeStoryboard.value) {
    imagePrompt.value = generateDefaultImagePrompt(activeStoryboard.value);
  }
};

const generateDefaultImagePrompt = (storyboard: any): string => {
  let prompt = `${storyboard.description}`;
  
  // 添加场景信息
  if (scenes.value.length > 0) {
    const scene = scenes.value[0]; // 简化处理，实际可能需要匹配对应的场景
    prompt += `, ${scene.description}`;
  }
  
  // 添加风格信息
  prompt += `, ${imageStyle.value}风格, 高清, 专业品质`;
  
  return prompt;
};

const generateImage = async () => {
  if (!activeStoryboard.value || !imagePrompt.value) return;
  
  try {
    isGeneratingImage.value = true;
    
    // 创建单个分镜画面生成请求
    const frameRequest = {
      frame_id: activeStoryboard.value.id || `frame_${activeStoryboardIndex.value}`,
      prompt: imagePrompt.value,
      image_style: imageStyle.value,
      width: 1920,
      height: 1080,
      negative_prompt: ""
    };
    
    const response = await axios.post('/api/v1/media/generate-frame', {
      task_id: taskId.value,
      storyboard_id: taskId.value, // 使用taskId作为storyboard_id
      frame: frameRequest
    });
    
    if (response.status === 200) {
      // 更新分镜的图片URL
      activeStoryboard.value.image_url = response.data.data.image_url;
      activeStoryboard.value.media_status = 'completed';
    } else {
      throw new Error(response.data.message || '生成画面失败');
    }
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '生成画面失败，请重试');
    console.error('生成画面失败:', err);
  } finally {
    isGeneratingImage.value = false;
  }
};

const regenerateImage = () => {
  generateImage();
};

const customizeImage = () => {
  // TODO: 实现自定义图片功能，如上传本地图片
  alert('自定义图片功能开发中');
};

const updateDialogue = () => {
  // 自动保存对白更改
  // 这里可以添加防抖逻辑
};

const generateVoice = async () => {
  if (!activeStoryboard.value || !activeStoryboard.value.dialogue) return;
  
  try {
    isGeneratingVoice.value = true;
    
    const response = await axios.post('/api/v1/media/generate-voice', {
      task_id: taskId.value,
      storyboard_index: activeStoryboardIndex.value,
      text: activeStoryboard.value.dialogue,
      character: selectedCharacter.value,
      voice_type: voiceType.value,
      provider: voiceProvider.value,
      speed: voiceSpeed.value
    });
    
    if (response.data.code === 200) {
      // 更新分镜的语音URL
      activeStoryboard.value.voice_url = response.data.data.voice_url;
      activeStoryboard.value.media_status = 'completed';
    } else {
      throw new Error(response.data.message || '生成配音失败');
    }
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '生成配音失败，请重试');
    console.error('生成配音失败:', err);
  } finally {
    isGeneratingVoice.value = false;
  }
};

const regenerateVoice = () => {
  generateVoice();
};

const toggleEffect = (effectId: string) => {
  if (!activeStoryboard.value) return;
  
  const index = activeStoryboard.value.effects.indexOf(effectId);
  if (index > -1) {
    activeStoryboard.value.effects.splice(index, 1);
  } else {
    activeStoryboard.value.effects.push(effectId);
  }
};

const getEffectName = (effectId: string): string => {
  const effect = effects.value.find(e => e.id === effectId);
  return effect ? effect.name : effectId;
};

const batchGenerateImages = async () => {
  try {
    isGeneratingImages.value = true;
    
    // 过滤出需要生成图片的分镜
    const pendingStoryboards = storyboards.value.filter(sb => !sb.image_url);
    
    if (pendingStoryboards.length === 0) {
      alert('所有分镜都已有图片');
      return;
    }
    
    // 准备批量生成请求数据
    const frames = pendingStoryboards.map((sb, index) => {
      const sbIndex = storyboards.value.indexOf(sb);
      storyboards.value[sbIndex].media_status = 'processing';
      
      return {
        frame_id: sb.id || `frame_${sbIndex}`,
        prompt: generateDefaultImagePrompt(sb),
        image_style: imageStyle.value,
        width: 1920,
        height: 1080,
        negative_prompt: ""
      };
    });
    
    // 调用批量生成接口
    const response = await axios.post('/api/v1/media/generate-batch', {
      task_id: taskId.value,
      storyboard_id: taskId.value, // 使用taskId作为storyboard_id
      frames: frames,
      audio_enabled: false, // 只生成图片
      effects_enabled: false
    });
    
    if (response.status === 200) {
      const taskId = response.data.data.task_id;
      
      // 轮询任务状态
      await pollTaskStatus(taskId);
      
      alert('批量生成图片完成');
    } else {
      throw new Error(response.data.message || '批量生成图片失败');
    }
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '批量生成图片失败');
    console.error('批量生成图片失败:', err);
  } finally {
    isGeneratingImages.value = false;
  }
};

const batchGenerateVoices = async () => {
  try {
    isGeneratingVoices.value = true;
    
    // 过滤出需要生成配音的分镜
    const pendingStoryboards = storyboards.value.filter(sb => 
      sb.dialogue && !sb.voice_url
    );
    
    if (pendingStoryboards.length === 0) {
      alert('没有需要生成配音的分镜');
      return;
    }
    
    // 批量生成配音
    for (let i = 0; i < pendingStoryboards.length; i++) {
      const sbIndex = storyboards.value.indexOf(pendingStoryboards[i]);
      
      // 更新状态为处理中
      storyboards.value[sbIndex].media_status = 'processing';
      
      // 调用生成接口
      const response = await axios.post('/api/v1/media/generate-voice', {
        task_id: taskId.value,
        storyboard_index: sbIndex,
        text: storyboards.value[sbIndex].dialogue,
        character: selectedCharacter.value,
        voice_type: voiceType.value,
        provider: voiceProvider.value,
        speed: voiceSpeed.value
      });
      
      if (response.data.code === 200) {
        storyboards.value[sbIndex].voice_url = response.data.data.voice_url;
        storyboards.value[sbIndex].media_status = 'completed';
      } else {
        storyboards.value[sbIndex].media_status = 'failed';
        console.error(`第 ${sbIndex + 1} 个分镜生成配音失败:`, response.data.message);
      }
      
      // 避免请求过于频繁
      if (i < pendingStoryboards.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    alert('批量生成配音完成');
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '批量生成配音失败');
    console.error('批量生成配音失败:', err);
  } finally {
    isGeneratingVoices.value = false;
  }
};

const applyDefaultEffects = () => {
  // 为所有分镜应用默认动效
  storyboards.value.forEach(sb => {
    sb.effects = ['fade_in', 'fade_out']; // 默认添加淡入淡出效果
  });
  
  alert('默认动效已应用到所有分镜');
};

const saveAllChanges = async () => {
  try {
    isSaving.value = true;
    
    // 准备批量生成请求，包含已有的媒体资源和动效设置
    const frames = storyboards.value.map((sb, index) => ({
      frame_id: sb.id || `frame_${index}`,
      prompt: generateDefaultImagePrompt(sb),
      image_style: imageStyle.value,
      width: 1920,
      height: 1080,
      negative_prompt: ""
    }));
    
    const response = await axios.post('/api/v1/media/generate-batch', {
      task_id: taskId.value,
      storyboard_id: taskId.value, // 使用taskId作为storyboard_id
      frames: frames,
      audio_enabled: true,
      effects_enabled: true,
      voice_name: voiceName.value,
      voice_volume: voiceVolume.value,
      voice_rate: voiceSpeed.value
    });
    
    if (response.status === 200) {
      const batchTaskId = response.data.data.task_id;
      
      // 轮询任务状态
      await pollTaskStatus(batchTaskId);
      
      alert('保存成功');
      
      // 更新导航组件的状态
      if (canProceed.value && flowNavigation.value) {
        flowNavigation.value.updateStepStatus('media_generation', true);
      }
    } else {
      throw new Error(response.data.message || '保存失败');
    }
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '保存失败，请重试');
    console.error('保存失败:', err);
  } finally {
    isSaving.value = false;
  }
};

const nextStep = async () => {
  if (!canProceed.value) {
    alert('请确保所有分镜都已完成画面和配音的生成');
    return;
  }
  
  // 保存所有更改
  await saveAllChanges();
  
  // 跳转到视频合成页面
  localStorage.setItem('currentTaskId', taskId.value as string);
  router.push({
    path: '/video-synthesis',
    query: {
      taskId: taskId.value
    }
  });
};

const goBack = () => {
  router.push({
    path: '/storyboard',
    query: {
      taskId: taskId.value
    }
  });
};

const handleStepChange = (step: string) => {
  // 处理流程步骤变更
  switch (step) {
    case 'script':
      router.push({ path: '/script-edit', query: { taskId: taskId.value } });
      break;
    case 'character-scene':
      router.push({ path: '/character-scene', query: { taskId: taskId.value } });
      break;
    case 'storyboard':
      router.push({ path: '/storyboard', query: { taskId: taskId.value } });
      break;
    // 其他步骤可以在这里添加
  }
};

const truncateText = (text: string, maxLength: number): string => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

// 轮询任务状态
const pollTaskStatus = async (taskId: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const checkStatus = async () => {
      try {
        const response = await axios.get(`/api/v1/tasks/${taskId}`);
        
        if (response.status === 200) {
          const taskStatus = response.data.data;
          
          // 更新进度显示
          loadingMessage.value = `处理中: ${taskStatus.progress}%`;
          
          if (taskStatus.state === 1 || taskStatus.progress === 100) {
            // 任务完成，更新分镜数据
            if (taskStatus.storyboards) {
              storyboards.value = taskStatus.storyboards;
            }
            resolve();
          } else {
            // 继续轮询
            setTimeout(checkStatus, 3000);
          }
        } else {
          reject(new Error('查询任务状态失败'));
        }
      } catch (err) {
        reject(err);
      }
    };
    
    // 开始轮询
    setTimeout(checkStatus, 2000);
  });
};

// Lifecycle
onMounted(() => {
  loadTaskData();
});
</script>

<style scoped>
.media-generation-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
}

.back-button {
  background: none;
  border: none;
  color: #5d6afb;
  font-size: 16px;
  cursor: pointer;
  margin-right: 20px;
  padding: 8px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: rgba(93, 106, 251, 0.1);
}

.back-icon {
  font-size: 18px;
}

.header h1 {
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
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #5d6afb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  margin-bottom: 20px;
}

.retry-button {
  background-color: #5d6afb;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background-color: #4a58e0;
}

/* 任务信息 */
.task-info {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.task-info h2 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 18px;
}

.task-info p {
  margin: 5px 0;
  color: #7f8c8d;
}

/* 分镜列表 */
.storyboards-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.storyboards-section h2 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 18px;
}

.storyboard-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 10px;
}

.storyboard-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 200px;
}

.storyboard-tab:hover {
  background: #e9ecef;
}

.storyboard-tab.active {
  background: #5d6afb;
  color: white;
  border-color: #5d6afb;
}

.tab-number {
  background: rgba(0, 0, 0, 0.1);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.storyboard-tab.active .tab-number {
  background: rgba(255, 255, 255, 0.2);
}

.tab-title {
  flex: 1;
  font-size: 14px;
}

.tab-status {
  font-size: 18px;
}

.tab-status.success {
  color: #2ecc71;
}

.tab-status.processing {
  color: #f39c12;
}

.tab-status.pending {
  color: #95a5a6;
}

/* 分镜编辑器 */
.storyboard-editor {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.editor-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

/* 媒体面板 */
.media-panel,
.voice-panel {
  display: flex;
  flex-direction: column;
}

.media-panel h3,
.voice-panel h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 18px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e9ecef;
}

/* 预览容器 */
.preview-container {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}

.image-preview {
  position: relative;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 4px;
}

.preview-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.no-image {
  padding: 40px 20px;
  color: #7f8c8d;
}

.no-image-placeholder {
  font-size: 48px;
  margin-bottom: 15px;
}

/* 生成选项 */
.generation-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.option-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
}

.prompt-input,
.dialogue-input,
.select-input {
  padding: 10px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.prompt-input:focus,
.dialogue-input:focus,
.select-input:focus {
  outline: none;
  border-color: #5d6afb;
}

.prompt-input,
.dialogue-input {
  min-height: 80px;
  resize: vertical;
}

.option-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.option-group.half {
  flex: 1;
}

.range-input {
  width: 100%;
  margin: 10px 0;
}

.range-value {
  font-size: 14px;
  color: #5d6afb;
  font-weight: 500;
}

/* 按钮样式 */
.generate-button,
.action-button,
.batch-button,
.save-button,
.next-button {
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.generate-button {
  background: linear-gradient(135deg, #5d6afb 0%, #4a58e0 100%);
  color: white;
}

.generate-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #4a58e0 0%, #3a47d5 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(93, 106, 251, 0.3);
}

.action-button {
  background: #3498db;
  color: white;
}

.action-button.secondary {
  background: #95a5a6;
}

.action-button:hover:not(:disabled) {
  opacity: 0.9;
}

/* 音频控制 */
.audio-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 15px;
}

.audio-player {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.audio-player audio {
  width: 100%;
}

/* 动效面板 */
.effects-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.effects-panel h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 18px;
}

.effects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.effect-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid #e9ecef;
}

.effect-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.effect-item.active {
  background: #5d6afb;
  color: white;
  border-color: #5d6afb;
}

.effect-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.effect-name {
  font-size: 14px;
  font-weight: 500;
}

.effect-preview {
  background: white;
  padding: 15px;
  border-radius: 8px;
}

.effect-preview h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #2c3e50;
  font-size: 16px;
}

.preview-text {
  font-size: 14px;
  color: #7f8c8d;
}

/* 批量操作 */
.batch-operations {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.batch-operations h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 18px;
}

.operation-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.batch-button {
  background: #2ecc71;
  color: white;
}

.batch-button.secondary {
  background: #34495e;
}

.batch-button:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-2px);
}

/* 底部操作 */
.bottom-actions {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 30px;
}

.save-button {
  background: #27ae60;
  color: white;
}

.save-button:hover:not(:disabled) {
  background: #229954;
}

.next-button {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
}

.next-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* 禁用状态 */
.generate-button:disabled,
.action-button:disabled,
.batch-button:disabled,
.save-button:disabled,
.next-button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .editor-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 15px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header h1 {
    font-size: 20px;
  }
  
  .option-row {
    grid-template-columns: 1fr;
  }
  
  .storyboard-tabs {
    max-height: 150px;
  }
  
  .storyboard-tab {
    min-width: auto;
    flex: 1;
  }
  
  .effects-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
  
  .bottom-actions {
    flex-direction: column;
  }
  
  .operation-buttons {
    flex-direction: column;
  }
}
</style>