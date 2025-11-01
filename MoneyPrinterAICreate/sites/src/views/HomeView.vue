<template>
  <div class="home-view">
    <div class="container">
      <!-- 视频脚本设置 -->
      <div class="section">
        <h2>视频脚本设置</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="videoSubject">视频主题</label>
            <input 
              id="videoSubject" 
              v-model="params.video_subject" 
              type="text" 
              placeholder="请输入视频主题"
            />
          </div>
          
          <div class="form-group">
            <label for="videoStyle">视频风格</label>
            <input 
              id="videoStyle" 
              v-model="params.video_style" 
              type="text" 
              placeholder="请输入视频风格"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group flex-1">
              <label for="blockCount">素材块数量</label>
              <input 
                id="blockCount" 
                v-model.number="blockCount" 
                type="range" 
                min="3" 
                max="12" 
                @change="updateBlockCount"
              />
              <span class="range-value">{{ blockCount }}</span>
            </div>
            
            <div class="form-group flex-1">
              <label for="videoLanguage">脚本语言</label>
              <select id="videoLanguage" v-model="params.video_language">
                <option value="">自动检测</option>
                <option value="zh">中文</option>
                <option value="en">英文</option>
                <option value="ja">日语</option>
                <option value="ko">韩语</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label for="videoScript">视频脚本</label>
            <textarea 
              id="videoScript" 
              v-model="params.video_script" 
              rows="8" 
              placeholder="请输入视频脚本"
            ></textarea>
            <div class="button-row">
              <button @click="generateScript" class="secondary-button" :disabled="isLoading">
                {{ isLoading ? '生成中...' : '生成视频脚本' }}
              </button>
              <button @click="generateOutline" class="secondary-button" :disabled="isLoading">
                {{ isLoading ? '生成中...' : '生成视频分镜' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 三栏设置区域 -->
      <div class="settings-grid">
        <!-- 视频设置 -->
        <div class="section">
          <h2>视频设置</h2>
          <div class="form-container">
            <div class="form-group">
              <label for="videoSource">视频来源</label>
              <select id="videoSource" v-model="params.video_source">
                <option value="local">本地文件</option>
                <option value="wan21">wan21 AI</option>
              </select>
            </div>
            
            <div v-if="params.video_source === 'local'" class="form-group">
              <label>上传本地文件</label>
              <input type="file" multiple @change="handleFileUpload" accept=".mp4,.mov,.avi,.flv,.mkv,.jpg,.jpeg,.png" />
            </div>
            
            <div class="form-group">
              <label for="videoConcatMode">视频拼接模式</label>
              <select id="videoConcatMode" v-model="params.video_concat_mode">
                <option value="sequential">顺序</option>
                <option value="random">随机</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="videoAspect">视频比例</label>
              <select id="videoAspect" v-model="params.video_aspect">
                <option value="portrait">竖屏</option>
                <option value="landscape">横屏</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="videoClipDuration">片段时长（秒）</label>
              <select id="videoClipDuration" v-model.number="params.video_clip_duration">
                <option :value="i" v-for="i in [2,3,4,5,6,7,8,9,10]" :key="i">{{ i }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="videoCount">同时生成视频数量</label>
              <select id="videoCount" v-model.number="params.video_count">
                <option :value="i" v-for="i in [1,2,3,4,5]" :key="i">{{ i }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- 音频设置 -->
        <div class="section">
          <h2>音频设置</h2>
          <div class="form-container">
            <div class="form-group">
              <label for="voiceName">语音合成</label>
              <select id="voiceName" v-model="params.voice_name">
                <option value="zh-CN-XiaoxiaoNeural">中文 - 晓晓 (女声)</option>
                <option value="zh-CN-YunxiNeural">中文 - 云希 (女声)</option>
                <option value="zh-CN-YunyangNeural">中文 - 云扬 (男声)</option>
                <option value="en-US-AriaNeural">英文 - Aria (女声)</option>
                <option value="en-US-ChristopherNeural">英文 - Christopher (男声)</option>
              </select>
            </div>
            
            <button @click="playVoice" class="secondary-button" :disabled="isLoading">播放语音示例</button>
            
            <div class="form-group">
              <label for="voiceVolume">语音音量</label>
              <select id="voiceVolume" v-model.number="params.voice_volume">
                <option :value="i" v-for="i in [0.6,0.8,1.0,1.2,1.5,2.0,3.0,4.0,5.0]" :key="i">{{ i }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="voiceRate">语音语速</label>
              <select id="voiceRate" v-model.number="params.voice_rate">
                <option :value="i" v-for="i in [0.8,0.9,1.0,1.1,1.2,1.3,1.5,1.8,2.0]" :key="i">{{ i }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="bgmType">背景音乐</label>
              <select id="bgmType" v-model="params.bgm_type">
                <option value="">无背景音乐</option>
                <option value="random">随机背景音乐</option>
                <option value="custom">自定义背景音乐</option>
              </select>
            </div>
            
            <div v-if="params.bgm_type === 'custom'" class="form-group">
              <label for="bgmFile">自定义背景音乐文件</label>
              <input type="text" id="bgmFile" v-model="params.bgm_file" placeholder="请输入文件路径" />
            </div>
            
            <div class="form-group">
              <label for="bgmVolume">背景音乐音量</label>
              <select id="bgmVolume" v-model.number="params.bgm_volume">
                <option :value="i" v-for="i in [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]" :key="i">{{ i }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- 字幕设置 -->
        <div class="section">
          <h2>字幕设置</h2>
          <div class="form-container">
            <div class="form-group checkbox">
              <input type="checkbox" id="subtitleEnabled" v-model="params.subtitle_enabled" />
              <label for="subtitleEnabled">启用字幕</label>
            </div>
            
            <div class="form-group">
              <label for="fontName">字体</label>
              <select id="fontName" v-model="params.font_name">
                <option value="SimHei">黑体</option>
                <option value="SimSun">宋体</option>
                <option value="Microsoft YaHei">微软雅黑</option>
                <option value="Arial">Arial</option>
                <option value="Times New Roman">Times New Roman</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="subtitlePosition">位置</label>
              <select id="subtitlePosition" v-model="params.subtitle_position">
                <option value="top">顶部</option>
                <option value="center">居中</option>
                <option value="bottom">底部</option>
                <option value="custom">自定义</option>
              </select>
            </div>
            
            <div v-if="params.subtitle_position === 'custom'" class="form-group">
              <label for="customPosition">自定义位置（顶部百分比）</label>
              <input type="number" id="customPosition" v-model.number="params.custom_position" min="0" max="100" />
            </div>
            
            <div class="form-row">
              <div class="form-group flex-1">
                <label for="textForeColor">字体颜色</label>
                <input type="color" id="textForeColor" v-model="params.text_fore_color" />
              </div>
              
              <div class="form-group flex-1">
                <label for="fontSize">字体大小</label>
                <input type="range" id="fontSize" v-model.number="params.font_size" min="30" max="100" />
                <span class="range-value">{{ params.font_size }}</span>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group flex-1">
                <label for="strokeColor">描边颜色</label>
                <input type="color" id="strokeColor" v-model="params.stroke_color" />
              </div>
              
              <div class="form-group flex-1">
                <label for="strokeWidth">描边宽度</label>
                <input type="range" id="strokeWidth" v-model.number="params.stroke_width" min="0" max="10" step="0.1" />
                <span class="range-value">{{ params.stroke_width }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 素材生成区 -->
      <div class="section">
        <h2>素材生成区</h2>
        <div class="material-blocks">
          <div v-for="i in blockCount" :key="i" class="material-block">
            <div class="material-header">
              <h3>素材块 {{ i }}</h3>
            </div>
            
            <div class="material-content">
              <div class="material-left">
                <div class="form-group">
                  <label>提示词</label>
                  <textarea 
                    v-model="materialBlocks[i-1].prompt" 
                    rows="4" 
                    placeholder="请输入提示词"
                  ></textarea>
                </div>
                
                <div class="form-group">
                  <label>上传图片（可选）</label>
                  <input type="file" @change="handleImageUpload($event, i-1)" accept=".jpg,.jpeg,.png" />
                </div>
                
                <button 
                  @click="generateMaterial(i-1)" 
                  class="primary-button" 
                  :disabled="materialBlocks[i-1].generating || isLoading"
                >
                  {{ materialBlocks[i-1].generating ? '生成中...' : '生成' }}
                </button>
              </div>
              
              <div class="material-right">
                <div v-if="materialBlocks[i-1].generating" class="loading-state">
                  <p>素材块 {{ i }} 生成中...</p>
                </div>
                <div v-else-if="materialBlocks[i-1].video_path" class="video-preview">
                  <video :src="materialBlocks[i-1].video_path" controls></video>
                </div>
                <div v-else class="empty-state">
                  <p>等待生成指令</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 生成按钮和任务区域 -->
      <div class="section">
        <button @click="generateVideo" class="primary-button full-width" :disabled="isLoading">
          {{ isLoading ? '生成中...' : '生成视频' }}
        </button>
        
        <!-- 日志区域 -->
        <div v-if="logs.length > 0" class="logs-container">
          <h3>生成日志</h3>
          <pre class="logs">{{ logs.join('\n') }}</pre>
        </div>
        
        <!-- 生成结果 -->
        <div v-if="generatedVideos.length > 0" class="results-container">
          <h3>生成结果</h3>
          <div class="video-results">
            <div v-for="(video, index) in generatedVideos" :key="index" class="video-result">
              <video :src="video" controls></video>
              <a :href="video" download class="download-btn">下载视频</a>
            </div>
          </div>
        </div>
        
        <!-- 任务列表 -->
        <div class="task-section">
          <h2>任务列表</h2>
          <div class="task-list">
            <div 
              v-for="task in tasks" 
              :key="task.id"
              class="task-item"
              :class="`task-${task.status}`"
              @click="viewTaskDetail(task)"
            >
              <div class="task-info">
                <h4>{{ task.video_subject }}</h4>
                <div class="task-meta">
                  <span class="task-status">{{ task.status }}</span>
                  <span class="task-time">{{ task.created_at }}</span>
                </div>
              </div>
            </div>
            <div v-if="tasks.length === 0 && !isLoading" class="empty-task-list">
              <p>暂无任务，请先生成视频</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 任务详情弹窗 -->
      <div class="modal" v-if="showTaskDetail">
        <div class="modal-content">
          <div class="modal-header">
            <h3>任务详情</h3>
            <button class="close-btn" @click="closeTaskDetail">×</button>
          </div>
          <div class="modal-body">
            <div v-if="selectedTask">
              <p><strong>任务ID:</strong> {{ selectedTask.task_id }}</p>
              <p><strong>视频主题:</strong> {{ selectedTask.video_subject }}</p>
              <p><strong>状态:</strong> {{ selectedTask.status }}</p>
              <p><strong>创建时间:</strong> {{ selectedTask.created_at }}</p>
              <p v-if="selectedTask.completed_at"><strong>完成时间:</strong> {{ selectedTask.completed_at }}</p>
              <div v-if="selectedTask.status === 'completed' && selectedTask.video_url" class="video-preview">
                <video controls :src="selectedTask.video_url"></video>
                <a :href="selectedTask.video_url" download class="download-btn">下载视频</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

// 视频参数接口
interface VideoParams {
  video_subject: string;
  video_style: string;
  video_script: string;
  video_language: string;
  video_source: string;
  video_concat_mode: string;
  video_aspect: string;
  video_clip_duration: number;
  video_count: number;
  voice_name: string;
  voice_volume: number;
  voice_rate: number;
  bgm_type: string;
  bgm_file: string;
  bgm_volume: number;
  subtitle_enabled: boolean;
  font_name: string;
  subtitle_position: string;
  custom_position: number;
  text_fore_color: string;
  font_size: number;
  stroke_color: string;
  stroke_width: number;
  video_materials?: any[];
}

// 素材块接口
interface MaterialBlock {
  prompt: string;
  image: File | null;
  video_path: string;
  generating: boolean;
}

// 任务接口
interface Task {
  id: number;
  task_id: string;
  video_subject: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  video_url: string | null;
}

// 视频参数
const params = reactive<VideoParams>({
  video_subject: '',
  video_style: '',
  video_script: '',
  video_language: '',
  video_source: 'wan21',
  video_concat_mode: 'sequential',
  video_aspect: 'portrait',
  video_clip_duration: 6,
  video_count: 1,
  voice_name: 'zh-CN-XiaoxiaoNeural',
  voice_volume: 1.0,
  voice_rate: 1.0,
  bgm_type: 'random',
  bgm_file: '',
  bgm_volume: 0.2,
  subtitle_enabled: true,
  font_name: 'Microsoft YaHei',
  subtitle_position: 'bottom',
  custom_position: 70.0,
  text_fore_color: '#FFFFFF',
  font_size: 60,
  stroke_color: '#000000',
  stroke_width: 1.5,
  video_materials: []
});

// 状态管理
const isLoading = ref(false);
const tasks = ref<Task[]>([]);
const selectedTask = ref<Task | null>(null);
const showTaskDetail = ref(false);

// 分镜数据
const outline = ref<Record<string, any>>({});

// 素材块数量
const blockCount = ref(3);

// 素材块数据
const materialBlocks = ref<MaterialBlock[]>([
  { prompt: '', image: null, video_path: '', generating: false },
  { prompt: '', image: null, video_path: '', generating: false },
  { prompt: '', image: null, video_path: '', generating: false }
]);

// 上传的文件
const uploadedFiles = ref<File[]>([]);

// 日志
const logs = ref<string[]>([]);

// 生成的视频
const generatedVideos = ref<string[]>([]);

// 更新素材块数量
const updateBlockCount = () => {
  const currentCount = materialBlocks.value.length;
  if (blockCount.value > currentCount) {
    // 增加素材块
    for (let i = currentCount; i < blockCount.value; i++) {
      materialBlocks.value.push({ prompt: '', image: null, video_path: '', generating: false });
    }
  } else if (blockCount.value < currentCount) {
    // 减少素材块
    materialBlocks.value.splice(blockCount.value);
  }
};

// 生成脚本
const generateScript = async () => {
  if (!params.video_subject) {
    alert('请先输入视频主题');
    return;
  }
  
  isLoading.value = true;
  try {
    addLog('正在生成视频脚本...');
    // 模拟生成脚本，实际应调用API
    const response = await new Promise<string>((resolve) => {
      setTimeout(() => {
        resolve(`这是关于"${params.video_subject}"的视频脚本。风格为"${params.video_style || '默认'}"。\n\n这是一个示例脚本，在实际应用中会通过AI生成更丰富的内容。`);
      }, 1500);
    });
    
    params.video_script = response;
    addLog('视频脚本生成完成');
  } catch (error) {
    console.error('生成脚本失败:', error);
    addLog('生成脚本失败');
    alert('生成脚本失败');
  } finally {
    isLoading.value = false;
  }
};

// 生成分镜
const generateOutline = async () => {
  if (!params.video_script) {
    alert('请先输入或生成视频脚本');
    return;
  }
  
  isLoading.value = true;
  try {
    addLog('正在生成视频分镜...');
    // 模拟生成分镜
    const mockOutline: Record<string, any> = {};
    for (let i = 0; i < blockCount.value; i++) {
      mockOutline[i.toString()] = {
        prompt: `这是分镜 ${i+1} 的提示词，基于视频脚本生成。`,
        img: `分镜 ${i+1} 的图片描述`
      };
      // 更新素材块的提示词
      if (i < materialBlocks.value.length) {
        materialBlocks.value[i].prompt = mockOutline[i.toString()].prompt;
      }
    }
    outline.value = mockOutline;
    addLog('视频分镜生成完成');
  } catch (error) {
    console.error('生成分镜失败:', error);
    addLog('生成分镜失败');
    alert('生成分镜失败');
  } finally {
    isLoading.value = false;
  }
};

// 播放语音示例
const playVoice = async () => {
  try {
    addLog('正在合成语音...');
    // 模拟语音合成
    setTimeout(() => {
      addLog('语音合成完成');
      alert('语音合成完成（模拟）');
    }, 1000);
  } catch (error) {
    console.error('语音合成失败:', error);
    addLog('语音合成失败');
    alert('语音合成失败');
  }
};

// 处理文件上传
const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    uploadedFiles.value = Array.from(target.files);
    addLog(`已上传 ${uploadedFiles.value.length} 个文件`);
  }
};

// 处理图片上传
const handleImageUpload = (event: Event, index: number) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    materialBlocks.value[index].image = target.files[0];
    addLog(`已上传素材块 ${index+1} 的图片`);
  }
};

// 生成素材
const generateMaterial = async (index: number) => {
  const block = materialBlocks.value[index];
  
  if (!block.prompt) {
    alert('请输入提示词');
    return;
  }
  
  try {
    block.generating = true;
    addLog(`正在生成素材块 ${index+1}...`);
    
    // 模拟生成视频
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 模拟视频路径
    block.video_path = `/api/mock/video_${index+1}.mp4`;
    addLog(`素材块 ${index+1} 生成完成`);
  } catch (error) {
    console.error(`生成素材块 ${index+1} 失败:`, error);
    addLog(`生成素材块 ${index+1} 失败`);
    alert(`生成素材块 ${index+1} 失败`);
  } finally {
    block.generating = false;
  }
};

// 生成视频
const generateVideo = async () => {
  // 验证参数
  if (!params.video_subject && !params.video_script) {
    alert('视频主题和脚本不能同时为空');
    return;
  }
  
  // 验证素材块
  if (params.video_source === 'wan21') {
    const allGenerated = materialBlocks.value.every(block => block.video_path);
    if (!allGenerated) {
      alert('请先生成所有素材块');
      return;
    }
  }
  
  isLoading.value = true;
  try {
    addLog('开始生成视频...');
    
    // 模拟视频生成过程
    for (let i = 0; i < 5; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      addLog(`视频生成进度: ${(i+1)*20}%`);
    }
    
    // 模拟生成结果
    generatedVideos.value = [];
    for (let i = 0; i < params.video_count; i++) {
      generatedVideos.value.push(`/api/mock/final_video_${i+1}.mp4`);
    }
    
    addLog('视频生成完成');
    
    // 添加到任务列表
    const newTask: Task = {
      id: Date.now(),
      task_id: `task_${Date.now()}`,
      video_subject: params.video_subject || '未命名视频',
      status: 'completed',
      created_at: new Date().toLocaleString(),
      completed_at: new Date().toLocaleString(),
      video_url: generatedVideos.value[0]
    };
    tasks.value.unshift(newTask);
  } catch (error) {
    console.error('生成视频失败:', error);
    addLog('视频生成失败');
    alert('生成视频失败');
  } finally {
    isLoading.value = false;
  }
};

// 获取任务列表
const fetchTasks = async () => {
  isLoading.value = true;
  try {
    // 模拟数据，实际项目中使用真实API
    tasks.value = [
      {
        id: 1,
        task_id: 'task_123456',
        video_subject: '测试视频',
        status: 'completed',
        created_at: '2024-01-01 10:00:00',
        completed_at: '2024-01-01 10:10:00',
        video_url: '#'
      },
      {
        id: 2,
        task_id: 'task_789012',
        video_subject: '示例视频',
        status: 'processing',
        created_at: '2024-01-01 10:05:00',
        completed_at: null,
        video_url: null
      }
    ];
  } catch (error) {
    console.error('获取任务列表失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 查看任务详情
const viewTaskDetail = (task: Task) => {
  selectedTask.value = task;
  showTaskDetail.value = true;
};

// 关闭任务详情
const closeTaskDetail = () => {
  showTaskDetail.value = false;
  selectedTask.value = null;
};

// 添加日志
const addLog = (message: string) => {
  const timestamp = new Date().toLocaleTimeString();
  logs.value.push(`[${timestamp}] ${message}`);
  // 限制日志数量
  if (logs.value.length > 100) {
    logs.value.shift();
  }
};

// 组件挂载时获取任务列表
onMounted(() => {
  fetchTasks();
});
</script>

<style scoped>
/* 全局变量 */
:root {
  --primary-color: #409eff;
  --primary-hover: #66b1ff;
  --success-color: #4CAF50;
  --success-hover: #45a049;
  --text-primary: #303133;
  --text-secondary: #606266;
  --border-color: #dcdfe6;
  --card-bg: #ffffff;
  --bg-color: #f5f7fa;
}

.home-view {
  padding: 20px;
  background-color: var(--bg-color);
  min-height: 100vh;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.section {
  background-color: var(--card-bg);
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

h2 {
  margin-bottom: 20px;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

h3 {
  margin: 0 0 15px 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group.flex-1 {
  flex: 1;
}

.form-group.checkbox {
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 14px;
}

input[type="text"],
input[type="number"],
input[type="file"],
textarea,
select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

input[type="range"] {
  width: calc(100% - 50px);
  margin-right: 10px;
  display: inline-block;
  vertical-align: middle;
}

.range-value {
  display: inline-block;
  width: 40px;
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
  vertical-align: middle;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

.button-row {
  display: flex;
  gap: 10px;
  margin-top: 5px;
}

.primary-button,
.secondary-button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.primary-button {
  background-color: var(--success-color);
  color: white;
}

.primary-button:hover:not(:disabled) {
  background-color: var(--success-hover);
}

.primary-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.secondary-button {
  background-color: var(--primary-color);
  color: white;
}

.secondary-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.primary-button.full-width {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  font-size: 16px;
}

/* 三栏设置区域 */
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

/* 素材块样式 */
.material-blocks {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.material-block {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.material-header {
  background-color: #f8f9fa;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.material-header h3 {
  margin: 0;
  font-size: 15px;
}

.material-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px;
}

.material-left,
.material-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.video-preview video {
  width: 100%;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  background-color: #f8f9fa;
  border-radius: 4px;
  color: var(--text-secondary);
}

/* 日志和结果样式 */
.logs-container,
.results-container {
  margin-top: 20px;
}

.logs {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  max-height: 200px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 13px;
  white-space: pre-wrap;
}

.video-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.video-result {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.video-result video {
  width: 100%;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.download-btn {
  display: inline-block;
  padding: 8px 16px;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.download-btn:hover {
  background-color: var(--primary-hover);
}

/* 任务列表样式 */
.task-section {
  margin-top: 20px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 16px;
  border-radius: 6px;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-item:hover {
  border-color: var(--primary-color);
}

.task-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #e5e7eb;
  color: #6b7280;
}

.task-item.task-completed .task-status {
  background-color: #d1fae5;
  color: #065f46;
}

.task-item.task-processing .task-status {
  background-color: #dbeafe;
  color: #1e40af;
}

.task-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.empty-task-list {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--card-bg);
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background-color: var(--border-color);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.modal-body p {
  margin: 8px 0;
  font-size: 14px;
  color: var(--text-primary);
}

.modal-body .video-preview {
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .settings-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .settings-grid .section:last-child {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-grid .section:last-child {
    grid-column: span 1;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .material-content {
    grid-template-columns: 1fr;
  }
  
  .video-results {
    grid-template-columns: 1fr;
  }
  
  .button-row {
    flex-direction: column;
  }
  
  .home-view {
    padding: 10px;
  }
}
</style>