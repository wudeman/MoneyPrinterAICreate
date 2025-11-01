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
              <option value="short-film">短片剧本</option>
              <option value="tv-series">电视剧本</option>
              <option value="movie">电影剧本</option>
            </select>
          </div>
          
          <div class="option-group">
            <label class="option-label">风格</label>
            <select v-model="styleType" class="select-option">
              <option value="">请选择风格</option>
              <option value="drama">戏剧性</option>
              <option value="comedy">喜剧</option>
              <option value="suspense">悬疑</option>
              <option value="romance">浪漫</option>
            </select>
          </div>
          
          <button @click="handleGenerate" class="generate-btn">
            <span class="btn-text">生成剧本</span>
            <span class="btn-icon">→</span>
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 创作灵感文本
const inspirationText = ref('');
// 模板类型
const templateType = ref('');
// 风格类型
const styleType = ref('');

/**
 * 处理生成按钮点击事件
 * 这里可以添加生成剧本的逻辑
 */
const handleGenerate = () => {
  if (!inspirationText.value.trim()) {
    alert('请输入创作灵感');
    return;
  }
  
  // 模拟生成过程
  console.log('开始生成剧本...');
  console.log('创作灵感:', inspirationText.value);
  console.log('模板类型:', templateType.value);
  console.log('风格:', styleType.value);
  
  // 这里可以调用实际的API进行剧本生成
};
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
</style>