<template>
  <div class="video-synthesis-container">
    <FlowNavigation ref="flowNavigation" @step-change="handleStepChange" />
    
    <div class="main-content">
      <div class="header">
        <button @click="goBack" class="back-button">
          <span class="back-icon">←</span>
          返回媒体编辑
        </button>
        <h1>视频合成</h1>
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
        
        <!-- 视频合成设置 -->
        <div class="synthesis-settings">
          <h2>视频合成设置</h2>
          
          <div class="settings-grid">
            <!-- 视频基本设置 -->
            <div class="setting-card">
              <h3>基本设置</h3>
              
              <div class="option-group">
                <label>视频标题</label>
                <input 
                  v-model="videoTitle" 
                  type="text" 
                  class="input-field"
                  placeholder="输入视频标题"
                />
              </div>
              
              <div class="option-row">
                <div class="option-group half">
                  <label>分辨率</label>
                  <select v-model="videoResolution" class="select-field">
                    <option value="720p">720p (1280×720)</option>
                    <option value="1080p">1080p (1920×1080)</option>
                    <option value="4k">4K (3840×2160)</option>
                  </select>
                </div>
                
                <div class="option-group half">
                  <label>帧率</label>
                  <select v-model="videoFps" class="select-field">
                    <option value="24">24 FPS</option>
                    <option value="30">30 FPS</option>
                    <option value="60">60 FPS</option>
                  </select>
                </div>
              </div>
              
              <div class="option-group">
                <label>视频比例</label>
                <select v-model="aspectRatio" class="select-field">
                  <option value="16:9">16:9 (宽屏)</option>
                  <option value="9:16">9:16 (竖屏)</option>
                  <option value="1:1">1:1 (方形)</option>
                  <option value="4:3">4:3 (标准)</option>
                </select>
              </div>
            </div>
            
            <!-- 背景音乐设置 -->
            <div class="setting-card">
              <h3>背景音乐</h3>
              
              <div class="option-group">
                <label>音乐类型</label>
                <select v-model="bgmType" class="select-field" @change="onBgmTypeChange">
                  <option value="">不使用背景音乐</option>
                  <option value="happy">欢快</option>
                  <option value="sad">悲伤</option>
                  <option value="exciting">激动</option>
                  <option value="peaceful">平静</option>
                  <option value="mysterious">神秘</option>
                  <option value="epic">史诗</option>
                </select>
              </div>
              
              <div v-if="bgmType" class="option-group">
                <label>音乐选择</label>
                <select v-model="selectedBgm" class="select-field">
                  <option v-for="music in bgmList" :key="music.id" :value="music.id">
                    {{ music.name }}
                  </option>
                </select>
              </div>
              
              <div v-if="selectedBgm" class="option-group">
                <label>音量</label>
                <div class="volume-control">
                  <input 
                    type="range" 
                    v-model.number="bgmVolume" 
                    min="0" 
                    max="100" 
                    step="5"
                    class="range-input"
                  />
                  <span class="volume-value">{{ bgmVolume }}%</span>
                </div>
                <audio :src="currentBgmUrl" controls class="bgm-player"></audio>
              </div>
              
              <div v-if="bgmType" class="option-group">
                <label>
                  <input type="checkbox" v-model="fadeInOut" />
                  淡入淡出效果
                </label>
              </div>
            </div>
          </div>
          
          <!-- 转场效果设置 -->
          <div class="setting-card">
            <h3>转场效果</h3>
            
            <div class="transition-effects">
              <div 
                v-for="transition in transitionEffects" 
                :key="transition.id"
                class="transition-item"
                :class="{ active: selectedTransition === transition.id }"
                @click="selectedTransition = transition.id"
              >
                <div class="transition-icon">{{ transition.icon }}</div>
                <div class="transition-name">{{ transition.name }}</div>
              </div>
            </div>
            
            <div class="option-group">
              <label>转场时长 (秒)</label>
              <input 
                type="number" 
                v-model.number="transitionDuration" 
                min="0.1" 
                max="3" 
                step="0.1"
                class="input-field small"
              />
            </div>
          </div>
          
          <!-- 字幕设置 -->
          <div class="setting-card">
            <h3>字幕设置</h3>
            
            <div class="option-group">
              <label>
                <input type="checkbox" v-model="enableSubtitles" />
                启用字幕
              </label>
            </div>
            
            <div v-if="enableSubtitles" class="subtitles-options">
              <div class="option-row">
                <div class="option-group half">
                  <label>字体</label>
                  <select v-model="subtitleFont" class="select-field">
                    <option value="Arial">Arial</option>
                    <option value="微软雅黑">微软雅黑</option>
                    <option value="宋体">宋体</option>
                    <option value="黑体">黑体</option>
                  </select>
                </div>
                
                <div class="option-group half">
                  <label>字号</label>
                  <input 
                    type="number" 
                    v-model.number="subtitleSize" 
                    min="12" 
                    max="48" 
                    step="2"
                    class="input-field small"
                  />
                </div>
              </div>
              
              <div class="option-row">
                <div class="option-group half">
                  <label>文字颜色</label>
                  <input type="color" v-model="subtitleColor" class="color-input" />
                </div>
                
                <div class="option-group half">
                  <label>背景颜色</label>
                  <input type="color" v-model="subtitleBgColor" class="color-input" />
                </div>
              </div>
              
              <div class="option-group">
                <label>位置</label>
                <select v-model="subtitlePosition" class="select-field">
                  <option value="bottom">底部</option>
                  <option value="top">顶部</option>
                  <option value="middle">中间</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 视频预览 -->
        <div class="video-preview-section">
          <h2>视频预览</h2>
          
          <div class="preview-container">
            <div v-if="isPreviewing" class="preview-loading">
              <div class="loading-spinner"></div>
              <p>生成预览中...</p>
            </div>
            <div v-else-if="previewVideoUrl" class="preview-video">
              <video :src="previewVideoUrl" controls autoplay loop class="video-player"></video>
              <div class="preview-actions">
                <button @click="regeneratePreview" :disabled="isPreviewing" class="action-button">
                  重新预览
                </button>
              </div>
            </div>
            <div v-else class="no-preview">
              <div class="preview-placeholder">🎬</div>
              <p>暂无预览</p>
              <button @click="generatePreview" :disabled="isPreviewing" class="action-button">
                生成预览
              </button>
            </div>
          </div>
        </div>
        
        <!-- 分镜预览列表 -->
        <div class="storyboard-list">
          <h2>分镜预览</h2>
          
          <div class="storyboard-grid">
            <div 
              v-for="(storyboard, index) in storyboards" 
              :key="index"
              class="storyboard-item"
            >
              <div class="storyboard-number">{{ index + 1 }}</div>
              <div v-if="storyboard.image_url" class="storyboard-image">
                <img :src="storyboard.image_url" :alt="storyboard.description" />
              </div>
              <div v-else class="no-image">无图片</div>
              <div class="storyboard-dialogue">{{ truncateText(storyboard.dialogue, 30) }}</div>
              <div class="storyboard-duration">{{ formatDuration(storyboard.duration || 3) }}</div>
            </div>
          </div>
        </div>
        
        <!-- 批量操作 -->
        <div class="batch-operations">
          <h2>批量调整</h2>
          
          <div class="operation-grid">
            <div class="operation-item">
              <label>统一调整分镜时长 (秒)</label>
              <div class="adjust-control">
                <input 
                  type="number" 
                  v-model.number="uniformDuration" 
                  min="1" 
                  max="10" 
                  step="0.5"
                  class="input-field small"
                />
                <button @click="applyUniformDuration" class="apply-button">
                  应用
                </button>
              </div>
            </div>
            
            <div class="operation-item">
              <label>调整整体音量 (配音)</label>
              <div class="adjust-control">
                <input 
                  type="range" 
                  v-model.number="voiceVolume" 
                  min="0" 
                  max="200" 
                  step="10"
                  class="range-input"
                />
                <span class="volume-value">{{ voiceVolume }}%</span>
                <button @click="applyVoiceVolume" class="apply-button">
                  应用
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部操作 -->
        <div class="bottom-actions">
          <button @click="saveSettings" :disabled="isSaving" class="save-button">
            {{ isSaving ? '保存中...' : '保存设置' }}
          </button>
          <button @click="generateFinalVideo" :disabled="isGeneratingVideo || !previewVideoUrl" class="generate-button">
            {{ isGeneratingVideo ? '生成中...' : '生成最终视频' }}
          </button>
        </div>
        
        <!-- 视频生成进度 -->
        <div v-if="isGeneratingVideo" class="generation-progress">
          <h3>视频生成进度</h3>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: videoGenerationProgress + '%' }"></div>
          </div>
          <p class="progress-text">{{ videoGenerationProgress }}% - {{ generationStatusMessage }}</p>
          <p class="estimation-text">{{ estimatedTime }}</p>
        </div>
        
        <!-- 最终视频结果 -->
        <div v-if="finalVideoUrl" class="final-video-section">
          <h2>最终视频</h2>
          
          <div class="final-video-container">
            <video :src="finalVideoUrl" controls class="video-player"></audio>
            
            <div class="video-actions">
              <button @click="downloadVideo" class="download-button">
                <span class="download-icon">⬇️</span>
                下载视频
              </button>
              <button @click="shareVideo" class="share-button">
                <span class="share-icon">📤</span>
                分享视频
              </button>
            </div>
          </div>
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
const isLoading = ref(true);
const loadingMessage = ref('');
const error = ref<string | null>(null);
const isSaving = ref(false);
const isPreviewing = ref(false);
const isGeneratingVideo = ref(false);
const videoGenerationProgress = ref(0);
const generationStatusMessage = ref('');
const estimatedTime = ref('');
const isFinalVideoGenerated = ref(false);

// 视频设置
const videoTitle = ref('');
const videoResolution = ref('1080p');
const videoFps = ref('30');
const aspectRatio = ref('16:9');
const selectedTransition = ref('fade');
const transitionDuration = ref(0.5);
const enableSubtitles = ref(true);
const subtitleFont = ref('微软雅黑');
const subtitleSize = ref(24);
const subtitleColor = ref('#ffffff');
const subtitleBgColor = ref('rgba(0, 0, 0, 0.6)');
const subtitlePosition = ref('bottom');

// 音频设置
const bgmType = ref('');
const bgmList = ref<any[]>([]);
const selectedBgm = ref('');
const bgmVolume = ref(50);
const fadeInOut = ref(true);
const voiceVolume = ref(100);

// 预览和最终视频
const previewVideoUrl = ref('');
const finalVideoUrl = ref('');
const uniformDuration = ref(3);

// 转场效果列表
const transitionEffects = ref([
  { id: 'fade', name: '淡入淡出', icon: '🔄' },
  { id: 'slide', name: '滑动', icon: '↔️' },
  { id: 'zoom', name: '缩放', icon: '🔍' },
  { id: 'push', name: '推入', icon: '⏩' },
  { id: 'wipe', name: '擦除', icon: '🧹' },
  { id: 'cube', name: '立方体', icon: '📦' },
  { id: 'flip', name: '翻转', icon: '🔄' },
  { id: 'none', name: '无', icon: '⚪' }
]);

// Computed
const taskStatusText = computed(() => {
  if (isLoading.value) return '加载中';
  if (error.value) return '错误';
  if (isGeneratingVideo.value) return '生成视频中';
  if (isFinalVideoGenerated.value) return '视频已生成';
  return '编辑中';
});

const currentBgmUrl = computed(() => {
  if (!selectedBgm.value) return '';
  const bgm = bgmList.value.find(b => b.id === selectedBgm.value);
  return bgm ? bgm.url : '';
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
      
      // 初始化分镜时长
      storyboards.value.forEach(sb => {
        if (!sb.duration) {
          sb.duration = 3; // 默认3秒
        }
      });
      
      // 设置视频标题
      videoTitle.value = taskData.title || `自动生成视频_${new Date().toLocaleDateString()}`;
      
      // 加载背景音乐列表
      await loadBgmList();
      
      // 尝试加载已保存的设置
      await loadSavedSettings();
      
      // 更新导航状态
      emit('update-task-id', taskIdParam);
      emit('update-status', 'video_synthesis_in_progress');
      
      // 检查是否已有生成的视频
      if (taskData.final_video_url) {
        finalVideoUrl.value = taskData.final_video_url;
        isFinalVideoGenerated.value = true;
        
        if (flowNavigation.value) {
          flowNavigation.value.updateStepStatus('video_synthesis', true);
        }
      }
      
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

const loadBgmList = async () => {
  try {
    const response = await axios.get('/api/v1/media/bgm-list');
    
    if (response.data.code === 200) {
      bgmList.value = response.data.data || [];
    }
  } catch (err) {
    console.error('加载背景音乐列表失败:', err);
    // 使用默认背景音乐列表
    bgmList.value = [
      { id: 'bgm1', name: '背景音乐1', url: '/assets/music/bgm1.mp3' },
      { id: 'bgm2', name: '背景音乐2', url: '/assets/music/bgm2.mp3' },
      { id: 'bgm3', name: '背景音乐3', url: '/assets/music/bgm3.mp3' }
    ];
  }
};

const loadSavedSettings = async () => {
  try {
    if (!taskId.value) return;
    
    const response = await axios.get(`/api/v1/video/settings/${taskId.value}`);
    
    if (response.data.code === 200) {
      const settings = response.data.data;
      
      if (settings) {
        videoResolution.value = settings.resolution || '1080p';
        videoFps.value = settings.fps || '30';
        aspectRatio.value = settings.aspect_ratio || '16:9';
        selectedTransition.value = settings.transition || 'fade';
        transitionDuration.value = settings.transition_duration || 0.5;
        enableSubtitles.value = settings.enable_subtitles !== undefined ? settings.enable_subtitles : true;
        subtitleFont.value = settings.subtitle_font || '微软雅黑';
        subtitleSize.value = settings.subtitle_size || 24;
        subtitleColor.value = settings.subtitle_color || '#ffffff';
        subtitleBgColor.value = settings.subtitle_bg_color || 'rgba(0, 0, 0, 0.6)';
        subtitlePosition.value = settings.subtitle_position || 'bottom';
        bgmType.value = settings.bgm_type || '';
        selectedBgm.value = settings.selected_bgm || '';
        bgmVolume.value = settings.bgm_volume !== undefined ? settings.bgm_volume : 50;
        fadeInOut.value = settings.fade_in_out !== undefined ? settings.fade_in_out : true;
        voiceVolume.value = settings.voice_volume !== undefined ? settings.voice_volume : 100;
        previewVideoUrl.value = settings.preview_url || '';
      }
    }
  } catch (err) {
    console.error('加载保存的设置失败:', err);
  }
};

const saveSettings = async () => {
  try {
    if (!taskId.value) return;
    
    isSaving.value = true;
    
    const settings = {
      resolution: videoResolution.value,
      fps: videoFps.value,
      aspect_ratio: aspectRatio.value,
      transition: selectedTransition.value,
      transition_duration: transitionDuration.value,
      enable_subtitles: enableSubtitles.value,
      subtitle_font: subtitleFont.value,
      subtitle_size: subtitleSize.value,
      subtitle_color: subtitleColor.value,
      subtitle_bg_color: subtitleBgColor.value,
      subtitle_position: subtitlePosition.value,
      bgm_type: bgmType.value,
      selected_bgm: selectedBgm.value,
      bgm_volume: bgmVolume.value,
      fade_in_out: fadeInOut.value,
      voice_volume: voiceVolume.value,
      preview_url: previewVideoUrl.value,
      storyboards: storyboards.value
    };
    
    const response = await axios.post(`/api/v1/video/settings/${taskId.value}`, settings);
    
    if (response.data.code === 200) {
      alert('设置保存成功');
    } else {
      throw new Error(response.data.message || '保存设置失败');
    }
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '保存设置失败，请重试');
    console.error('保存设置失败:', err);
  } finally {
    isSaving.value = false;
  }
};

const generatePreview = async () => {
  try {
    if (!taskId.value || storyboards.value.length === 0) return;
    
    isPreviewing.value = true;
    
    // 先保存设置
    await saveSettings();
    
    // 生成预览视频
    const response = await axios.post('/api/v1/media/generate-batch', {
      storyboard_id: taskId.value,
      // 只取前3个分镜生成预览
      frames: storyboards.value.slice(0, 3).map((sb, index) => ({
        frame_id: index.toString(),
        image_url: sb.image_url,
        dialogue: sb.dialogue,
        duration: sb.duration || 3,
        audio_url: sb.audio_url
      })),
      bgm: {
        bgm_id: selectedBgm.value,
        volume: bgmVolume.value,
        fade_in_out: fadeInOut.value
      },
      voice_volume: voiceVolume.value
    });
    
    if (response.data.code === 200) {
      previewVideoUrl.value = response.data.data.preview_url;
      
      // 更新保存的预览URL
      await saveSettings();
    } else {
      throw new Error(response.data.message || '生成预览失败');
    }
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '生成预览失败，请重试');
    console.error('生成预览失败:', err);
  } finally {
    isPreviewing.value = false;
  }
};

const regeneratePreview = () => {
  generatePreview();
};

// 轮询任务状态
const pollTaskStatus = async (taskId: string) => {
  try {
    const response = await axios.get(`/api/v1/tasks/${taskId}/status`);
    if (response.data.code === 200) {
      const status = response.data.data;
      videoGenerationProgress.value = status.progress || 0;
      generationStatusMessage.value = status.message || '';
      
      if (status.status === 'completed') {
        finalVideoUrl.value = status.video_url;
        isFinalVideoGenerated.value = true;
        return true;
      } else if (status.status === 'failed') {
        throw new Error(status.message || '视频生成失败');
      }
    }
  } catch (err) {
    console.error('轮询任务状态失败:', err);
    throw err;
  }
  return false;
};

const generateFinalVideo = async () => {
  try {
    if (!taskId.value || storyboards.value.length === 0) return;
    
    isGeneratingVideo.value = true;
    videoGenerationProgress.value = 0;
    generationStatusMessage.value = '准备生成视频...';
    estimatedTime.value = '预计需要几分钟，请耐心等待';
    
    // 先保存设置
    await saveSettings();
    
    // 调用视频合成接口
    const response = await axios.post('/api/v1/media/synthesize-video', {
      storyboard_id: taskId.value,
      title: videoTitle.value,
      bgm: {
        bgm_id: selectedBgm.value,
        volume: bgmVolume.value,
        fade_in_out: fadeInOut.value
      },
      transition_effect: selectedTransition.value,
      frame_duration: 3, // 默认帧时长
      output_format: 'mp4',
      subtitles: enableSubtitles.value ? {
        font: subtitleFont.value,
        size: subtitleSize.value,
        color: subtitleColor.value,
        bg_color: subtitleBgColor.value,
        position: subtitlePosition.value
      } : null
    });
    
    if (response.data.code === 200) {
      const synthesisTaskId = response.data.data.task_id;
      
      // 开始轮询任务状态
      const pollInterval = setInterval(async () => {
        try {
          const isComplete = await pollTaskStatus(synthesisTaskId);
          if (isComplete) {
            clearInterval(pollInterval);
            videoGenerationProgress.value = 100;
            generationStatusMessage.value = '视频生成完成！';
            
            // 更新任务状态
            await axios.post(`/api/v1/tasks/${taskId.value}/status`, {
              status: 'completed',
              final_video_url: finalVideoUrl.value
            });
            
            // 更新导航状态
            if (flowNavigation.value) {
              flowNavigation.value.updateStepStatus('video_synthesis', true);
            }
            
            alert('视频生成成功！');
          }
        } catch (err) {
          clearInterval(pollInterval);
          throw err;
        }
      }, 3000); // 每3秒轮询一次
    
    // 注意：成功的处理已在轮询中完成
    
  } catch (err) {
    alert(err instanceof Error ? err.message : '生成视频失败，请重试');
    console.error('生成视频失败:', err);
  } finally {
    isGeneratingVideo.value = false;
  }
};

const downloadVideo = () => {
  if (!finalVideoUrl.value) return;
  
  // 创建下载链接
  const link = document.createElement('a');
  link.href = finalVideoUrl.value;
  link.download = `${videoTitle.value || '生成视频'}_${new Date().getTime()}.mp4`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const shareVideo = () => {
  if (!finalVideoUrl.value) return;
  
  // 模拟分享功能
  prompt('复制以下链接分享视频:', finalVideoUrl.value);
};

const applyUniformDuration = () => {
  storyboards.value.forEach(sb => {
    sb.duration = uniformDuration.value;
  });
  
  alert('已统一调整所有分镜时长');
};

const applyVoiceVolume = () => {
  // 这里可以调用API来调整配音音量
  alert('配音音量调整设置已保存');
};

const onBgmTypeChange = async () => {
  if (bgmType.value) {
    // 根据选择的音乐类型过滤背景音乐列表
    try {
      const response = await axios.get(`/api/v1/media/bgm-list?type=${bgmType.value}`);
      
      if (response.data.code === 200) {
        bgmList.value = response.data.data || [];
        if (bgmList.value.length > 0) {
          selectedBgm.value = bgmList.value[0].id;
        } else {
          selectedBgm.value = '';
        }
      }
    } catch (err) {
      console.error('加载指定类型背景音乐失败:', err);
    }
  }
};

const goBack = () => {
  router.push({
    path: '/media-generation',
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
    case 'media-generation':
      router.push({ path: '/media-generation', query: { taskId: taskId.value } });
      break;
    // 其他步骤可以在这里添加
  }
};

const truncateText = (text: string, maxLength: number): string => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

const formatDuration = (duration: number): string => {
  return `${duration}秒`;
};

// Lifecycle
onMounted(() => {
  loadTaskData();
});
</script>

<style scoped>
.video-synthesis-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  color: white;
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
  background-color: rgba(255, 255, 255, 0.1);
}

.back-icon {
  font-size: 18px;
}

.header h1 {
  margin: 0;
  color: white;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
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
  background-color: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background-color: #5a67d8;
}

/* 任务信息 */
.task-info {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

/* 合成设置 */
.synthesis-settings {
  margin-bottom: 30px;
}

.synthesis-settings h2 {
  color: white;
  font-size: 22px;
  margin-bottom: 20px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.setting-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.setting-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 18px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e9ecef;
}

/* 选项组 */
.option-group {
  margin-bottom: 15px;
}

.option-group label {
  display: block;
  margin-bottom: 5px;
  color: #2c3e50;
  font-weight: 500;
}

.option-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.option-group.half {
  margin-bottom: 0;
}

.input-field,
.select-field {
  width: 100%;
  padding: 10px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.input-field:focus,
.select-field:focus {
  outline: none;
  border-color: #667eea;
}

.input-field.small {
  max-width: 100px;
}

/* 音量控制 */
.volume-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.volume-control .range-input {
  flex: 1;
}

.volume-value {
  min-width: 40px;
  font-weight: 500;
  color: #667eea;
}

.range-input {
  width: 100%;
}

.color-input {
  width: 100%;
  height: 40px;
  padding: 5px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
}

.bgm-player {
  width: 100%;
  margin-top: 10px;
}

/* 转场效果 */
.transition-effects {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.transition-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid #e9ecef;
}

.transition-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.transition-item.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.transition-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.transition-name {
  font-size: 14px;
  font-weight: 500;
}

/* 字幕选项 */
.subtitles-options {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

/* 视频预览 */
.video-preview-section,
.storyboard-list,
.batch-operations {
  margin-bottom: 30px;
}

.video-preview-section h2,
.storyboard-list h2,
.batch-operations h2 {
  color: white;
  font-size: 22px;
  margin-bottom: 20px;
}

.preview-container {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.preview-loading,
.no-preview {
  padding: 60px 20px;
}

.preview-video {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.video-player {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.preview-placeholder {
  font-size: 64px;
  margin-bottom: 20px;
}

.preview-actions,
.video-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
}

/* 按钮样式 */
.action-button,
.apply-button,
.download-button,
.share-button,
.save-button,
.generate-button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-button {
  background: #667eea;
  color: white;
}

.action-button:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-2px);
}

.apply-button {
  background: #3498db;
  color: white;
  white-space: nowrap;
}

.download-button {
  background: #2ecc71;
  color: white;
}

.share-button {
  background: #f39c12;
  color: white;
}

.save-button {
  background: #27ae60;
  color: white;
}

.generate-button {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  padding: 12px 30px;
  font-size: 16px;
}

.generate-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* 分镜列表 */
.storyboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.storyboard-item {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

.storyboard-number {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(102, 126, 234, 0.9);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  z-index: 1;
}

.storyboard-image {
  height: 150px;
  overflow: hidden;
  background: #f8f9fa;
}

.storyboard-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  color: #95a5a6;
}

.storyboard-dialogue {
  padding: 15px;
  font-size: 14px;
  color: #2c3e50;
  min-height: 40px;
}

.storyboard-duration {
  padding: 10px 15px;
  background: #f8f9fa;
  color: #7f8c8d;
  font-size: 12px;
  text-align: right;
  border-top: 1px solid #e9ecef;
}

/* 批量操作 */
.operation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.operation-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.operation-item label {
  display: block;
  margin-bottom: 10px;
  color: #2c3e50;
  font-weight: 500;
}

.adjust-control {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.adjust-control .range-input {
  flex: 1;
  min-width: 150px;
}

/* 底部操作 */
.bottom-actions {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

/* 视频生成进度 */
.generation-progress {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.generation-progress h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text,
.estimation-text {
  margin: 5px 0;
  color: #7f8c8d;
}

.progress-text {
  font-weight: 500;
  color: #2c3e50;
}

/* 最终视频 */
.final-video-section h2 {
  color: white;
  font-size: 22px;
  margin-bottom: 20px;
}

.final-video-container {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

/* 禁用状态 */
.action-button:disabled,
.generate-button:disabled,
.save-button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .operation-grid {
    grid-template-columns: 1fr;
  }
  
  .storyboard-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
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
  
  .bottom-actions {
    flex-direction: column;
  }
  
  .preview-actions,
  .video-actions {
    flex-direction: column;
  }
  
  .adjust-control {
    flex-direction: column;
    align-items: stretch;
  }
  
  .adjust-control .input-field.small {
    max-width: 100%;
  }
  
  .transition-effects {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
}
</style>