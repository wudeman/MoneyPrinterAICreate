<template>
 
    <div class="container">
      
      <!-- 主要内容区域 -->
      <div class="content-wrapper">
        <!-- 文本输入框 -->
        <div class="textarea-container">
          <textarea 
            v-model="inspirationText" 
            class="main-textarea" 
            placeholder="输入创作灵感，AI自动帮你生成剧本"
          ></textarea>
          <div class="character-count">{{ inspirationText.length }}/500</div>
        </div>
        
        <!-- 选项和按钮区域 -->
        <div class="options-container">
          <div class="option-group">
            <label class="option-label">模板选择</label>
            <select v-model="templateType" class="select-option">
              <option value="">请选择模板</option>
              <option v-for="template in templates" :key="template.id" :value="template.id">
                {{ template.template_name }}
              </option>
            </select>
          </div>
          
          <div class="option-group">
            <label class="option-label">风格</label>
            <select v-model="styleType" class="select-option">
                <option value="">请选择风格</option>
                <option v-for="style in styles" :key="style.id" :value="style.id">
                  {{ style.dict_name }}
                </option>
              </select>
          </div>
          
          <div class="option-group">
            <label class="option-label">时长（秒）</label>
            <input 
              v-model.number="duration" 
              type="number" 
              class="select-option" 
              min="10" 
              max="300" 
              placeholder="请输入视频时长"
            >
          </div>
          
          <button @click="handleGenerate" class="generate-btn">
            <span class="btn-text">生成剧本</span>
            <span class="btn-icon">→</span>
          </button>
        </div>
      </div>
      
      <!-- 集成测试入口 -->
      <div class="test-access">
        <router-link to="/integration-test" class="test-link">
          <span class="test-icon">🔍</span>
          <span>运行集成测试</span>
        </router-link>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

// 创作灵感文本
const inspirationText = ref('');
// 模板类型
const templateType = ref('');
// 风格类型
const styleType = ref('');
// 视频时长（秒）
const duration = ref(60);
// 模板列表
const templates = ref<any[]>([]);
// 风格列表
const styles = ref<any[]>([]);

// 路由实例
const router = useRouter();

/**
 * 获取激活的模板列表
 */
async function getActiveTemplates() {
  try {
    // 使用正确的API路径
    const response = await axios.get('/api/v1/templates/active/list');
    templates.value = response.data;
  } catch (error) {
    console.error('获取模板列表失败:', error);
  }
}

/**
   * 获取风格列表
   */
  async function getActiveStyles() {
    try {
      // 调用字典管理接口，根据字典类型"风格"查询
      const response = await axios.get('/api/v1/dicts', {
        params: {
          dict_type: '风格',
          status: 'active'
        }
      });
      styles.value = response.data.items;
    } catch (error) {
      console.error('获取风格列表失败:', error);
    }
  }

/**
 * 处理生成按钮点击事件
 * 调用后端API创建任务并生成剧本
 */
const handleGenerate = async () => {
  if (!inspirationText.value.trim()) {
    alert('请输入创作灵感');
    return;
  }
  
  if (!templateType.value) {
    alert('请选择模板');
    return;
  }
  
  if (!styleType.value) {
    alert('请选择风格');
    return;
  }
  
  if (!duration.value || duration.value < 10 || duration.value > 300) {
    alert('请输入有效的视频时长（10-300秒）');
    return;
  }
  
  try {
    // 获取选中的模板和风格信息
    const selectedTemplate = templates.value.find(t => t.id === templateType.value);
    const selectedStyle = styles.value.find(s => s.id === styleType.value);
    
    // 调用后端API创建任务并生成剧本
    const response = await axios.post('/api/v1/tasks/create-and-generate', {
      video_idea: inspirationText.value,
      template_id: parseInt(templateType.value),
      style_id: parseInt(styleType.value),
      aspect_ratio: '16:9', // 默认宽高比
      duration: duration.value
    });
    
    // 跳转到剧本编辑页面，并传递任务ID
    router.push({
      path: '/script-edit',
      query: {
        taskId: response.data.task_id,
        inspiration: inspirationText.value,
        templateId: templateType.value,
        templateName: selectedTemplate?.template_name || '',
        styleId: styleType.value,
        styleName: selectedStyle?.dict_name || '',
        duration: duration.value
      }
    });
  } catch (error) {
    console.error('处理生成请求失败:', error);
    alert('生成剧本请求失败，请重试');
  }
};

// 组件挂载时获取模板列表和风格列表
onMounted(() => {
  getActiveTemplates();
  getActiveStyles();
});
</script>

<style scoped>
/* 全局变量 */
:root {
  --primary-color: #5d6afb;
  --primary-hover: #4a5af0;
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

.home-view {
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.container {
  width: 100%;
  max-width: 800px;
}

/* 内容包装器 */
.content-wrapper {
  background-color: white;
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.content-wrapper:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

/* 文本输入区域 */
.textarea-container {
  position: relative;
  padding: 25px;
  border-bottom: 1px solid var(--border-color);
}

.main-textarea {
  width: 100%;
  height: 280px;
  border: none;
  outline: none;
  font-size: 16px;
  line-height: 1.6;
  resize: none;
  color: var(--text-primary);
  background-color: transparent;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  transition: all 0.2s ease;
}

.main-textarea:focus {
  box-shadow: 0 0 0 2px rgba(93, 106, 251, 0.2);
  border-radius: 8px;
}

.main-textarea::placeholder {
  color: var(--text-secondary);
  opacity: 0.7;
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

/* 选项容器样式 */
.options-container {
  display: flex;
  align-items: center;
  gap: 25px;
  padding: 25px;
  background-color: white;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.option-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 5px;
}

/* 选择框样式 */
.select-option {
  padding: 12px 15px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background-color: white;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236c757d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
}

.select-option:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(93, 106, 251, 0.2);
}

/* 生成按钮样式 */
.generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(93, 106, 251, 0.3);
  margin-left: auto;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(93, 106, 251, 0.4);
}

.generate-btn:active {
  transform: translateY(0);
}

.btn-text {
  transition: transform 0.2s ease;
}

.btn-icon {
  transition: transform 0.2s ease;
}

.generate-btn:hover .btn-icon {
  transform: translateX(3px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-view {
    padding: 20px 15px;
  }
  
  .options-container {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }
  
  .option-group {
    width: 100%;
  }
  
  .generate-btn {
    margin-left: 0;
    width: 100%;
    justify-content: center;
    margin-top: 10px;
  }
  
  .textarea-container {
    padding: 20px;
  }
  
  .main-textarea {
    height: 220px;
  }
}

/* 集成测试入口样式 */
.test-access {
  margin-top: 30px;
  text-align: center;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.test-access:hover {
  opacity: 1;
}

.test-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #f0f4ff 0%, #d9e0ff 100%);
  color: #3a4be0;
  text-decoration: none;
  border-radius: 8px;
  border: 2px dashed #5d6afb;
  font-weight: 600;
  transition: all 0.3s ease;
}

.test-link:hover {
  background: linear-gradient(135deg, #e6ebff 0%, #cbd4ff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(93, 106, 251, 0.2);
}

.test-icon {
  font-size: 18px;
}

@media (max-width: 480px) {
  .home-view {
    padding: 15px 10px;
  }
  
  .textarea-container {
    padding: 15px;
  }
  
  .options-container {
    padding: 20px 15px;
  }
  
  .main-textarea {
    height: 180px;
    font-size: 15px;
  }
}
/* 首页样式 */
.home {
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.home h1 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 40px;
  font-size: 2.5rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-item {
  background: white;
  padding: 30px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  text-align: center;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.feature-item h2 {
  color: var(--primary-color);
  margin-bottom: 15px;
  font-size: 1.5rem;
}

.feature-item p {
  color: var(--text-secondary);
  margin-bottom: 20px;
  line-height: 1.6;
}

.feature-item a {
  display: inline-block;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.feature-item a:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(93, 106, 251, 0.3);
}

/* 测试项目特殊样式 */
.test-item {
  background: linear-gradient(135deg, #f0f4ff 0%, #d9e0ff 100%);
  border: 2px dashed var(--primary-color);
}

.test-item h2 {
  color: #3a4be0;
}

@media (max-width: 768px) {
  .home h1 {
    font-size: 2rem;
  }
  
  .features {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .feature-item {
    padding: 25px;
  }
}

</style>