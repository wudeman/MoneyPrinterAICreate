<template>
  <div class="integration-test-container">
    <h1>MoneyPrinter AI 集成测试</h1>
    
    <!-- 测试控制面板 -->
    <div class="control-panel">
      <button @click="runFullTest" :disabled="isRunning">
        {{ isRunning ? '测试进行中...' : '运行完整测试流程' }}
      </button>
      <button @click="runApiTest" :disabled="isRunning">
        {{ isRunning ? '测试进行中...' : '仅测试API功能' }}
      </button>
      <button @click="resetTest">重置测试</button>
    </div>
    
    <!-- 测试结果展示 -->
    <div class="test-results">
      <div class="result-summary">
        <div class="summary-item">
          <span class="label">总测试项:</span>
          <span class="value">{{ testStats.total }}</span>
        </div>
        <div class="summary-item">
          <span class="label">通过:</span>
          <span class="value success">{{ testStats.passed }}</span>
        </div>
        <div class="summary-item">
          <span class="label">失败:</span>
          <span class="value error">{{ testStats.failed }}</span>
        </div>
        <div class="summary-item">
          <span class="label">状态:</span>
          <span class="value" :class="testStatusClass">{{ testStatus }}</span>
        </div>
      </div>
      
      <!-- 测试日志 -->
      <div class="test-logs">
        <h3>测试日志</h3>
        <div class="logs-container">
          <div 
            v-for="(log, index) in testLogs" 
            :key="index" 
            class="log-item" 
            :class="log.type"
          >
            <span class="timestamp">{{ log.time }}</span>
            <span class="content">{{ log.message }}</span>
          </div>
        </div>
      </div>
      
      <!-- 错误详情 -->
      <div class="error-details" v-if="testErrors.length > 0">
        <h3>错误详情</h3>
        <div class="errors-list">
          <div 
            v-for="(error, index) in testErrors" 
            :key="index" 
            class="error-item"
          >
            <strong>{{ error.module }}:</strong>
            <p>{{ error.message }}</p>
            <div v-if="error.details" class="error-stack">
              {{ error.details }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 测试状态可视化 -->
    <div class="test-visualization">
      <h3>流程状态</h3>
      <div class="flow-diagram">
        <div 
          v-for="step in testSteps" 
          :key="step.id" 
          class="step-item"
          :class="{ 
            'completed': step.status === 'completed',
            'failed': step.status === 'failed',
            'running': step.status === 'running'
          }"
        >
          <div class="step-icon">{{ step.icon }}</div>
          <div class="step-label">{{ step.label }}</div>
          <div class="step-status">{{ getStatusText(step.status) }}</div>
        </div>
      </div>
    </div>
    
    <!-- 任务信息 -->
    <div class="task-info" v-if="currentTaskId">
      <h3>当前测试任务</h3>
      <p>任务ID: {{ currentTaskId }}</p>
      <p>创建时间: {{ formatDate(taskCreationTime) }}</p>
      <button @click="loadTaskDetails" v-if="currentTaskId">查看任务详情</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'IntegrationTestView',
  data() {
    return {
      isRunning: false,
      testStats: {
        total: 0,
        passed: 0,
        failed: 0
      },
      testStatus: '未开始',
      testLogs: [],
      testErrors: [],
      testSteps: [
        { id: 'script', label: '剧本创建', icon: '📝', status: 'pending' },
        { id: 'character-scene', label: '角色场景', icon: '👥', status: 'pending' },
        { id: 'storyboard', label: '分镜制作', icon: '🎬', status: 'pending' },
        { id: 'progress', label: '进度检查', icon: '📊', status: 'pending' },
        { id: 'bgm', label: '背景音乐', icon: '🎵', status: 'pending' },
        { id: 'navigation', label: '流程导航', icon: '🔄', status: 'pending' }
      ],
      currentTaskId: null,
      taskCreationTime: null,
      taskDetails: null
    };
  },
  computed: {
    testStatusClass() {
      switch (this.testStatus) {
        case '成功':
          return 'success';
        case '失败':
          return 'error';
        case '进行中':
          return 'running';
        default:
          return 'pending';
      }
    }
  },
  methods: {
    // 添加日志
    addLog(message, type = 'info') {
      const timestamp = new Date().toLocaleTimeString('zh-CN');
      this.testLogs.push({
        time: timestamp,
        message,
        type
      });
      // 滚动到底部
      this.$nextTick(() => {
        const logsContainer = this.$el.querySelector('.logs-container');
        if (logsContainer) {
          logsContainer.scrollTop = logsContainer.scrollHeight;
        }
      });
    },
    
    // 添加错误
    addError(module, message, details = null) {
      this.testErrors.push({
        module,
        message,
        details
      });
      this.addLog(`${module} - 错误: ${message}`, 'error');
    },
    
    // 更新步骤状态
    updateStepStatus(stepId, status) {
      const step = this.testSteps.find(s => s.id === stepId);
      if (step) {
        step.status = status;
        this.addLog(`步骤 ${step.label} 状态更新为: ${this.getStatusText(status)}`);
      }
    },
    
    // 获取状态文本
    getStatusText(status) {
      switch (status) {
        case 'completed':
          return '完成';
        case 'failed':
          return '失败';
        case 'running':
          return '进行中';
        default:
          return '未开始';
      }
    },
    
    // 格式化日期
    formatDate(timestamp) {
      if (!timestamp) return '-';
      return new Date(timestamp).toLocaleString('zh-CN');
    },
    
    // 重置测试
    resetTest() {
      this.isRunning = false;
      this.testStats = { total: 0, passed: 0, failed: 0 };
      this.testStatus = '未开始';
      this.testLogs = [];
      this.testErrors = [];
      this.testSteps.forEach(step => {
        step.status = 'pending';
      });
      this.currentTaskId = null;
      this.taskCreationTime = null;
      this.taskDetails = null;
      this.addLog('测试已重置');
    },
    
    // 等待指定时间
    async wait(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    // 运行API测试
    async runApiTest() {
      if (this.isRunning) return;
      
      this.resetTest();
      this.isRunning = true;
      this.testStatus = '进行中';
      this.addLog('开始运行API功能测试', 'info');
      
      try {
        // 增加测试总数
        this.testStats.total = 5;
        
        // 测试1: 创建剧本
        this.updateStepStatus('script', 'running');
        await this.testCreateScript();
        this.testStats.passed++;
        this.updateStepStatus('script', 'completed');
        await this.wait(500);
        
        // 测试2: 更新角色场景
        this.updateStepStatus('character-scene', 'running');
        await this.testUpdateCharacterScene();
        this.testStats.passed++;
        this.updateStepStatus('character-scene', 'completed');
        await this.wait(500);
        
        // 测试3: 生成分镜和保存
        this.updateStepStatus('storyboard', 'running');
        await this.testStoryboard();
        this.testStats.passed++;
        this.updateStepStatus('storyboard', 'completed');
        await this.wait(500);
        
        // 测试4: 获取任务进度
        this.updateStepStatus('progress', 'running');
        await this.testTaskProgress();
        this.testStats.passed++;
        this.updateStepStatus('progress', 'completed');
        await this.wait(500);
        
        // 测试5: 获取背景音乐类型
        this.updateStepStatus('bgm', 'running');
        await this.testBgmTypes();
        this.testStats.passed++;
        this.updateStepStatus('bgm', 'completed');
        
        // 测试成功
        this.testStatus = '成功';
        this.addLog('API测试全部通过！', 'success');
        
      } catch (error) {
        this.testStats.failed++;
        this.testStatus = '失败';
        this.addError('API测试', '测试运行过程中发生错误', error.message);
      } finally {
        this.isRunning = false;
      }
    },
    
    // 运行完整测试流程
    async runFullTest() {
      if (this.isRunning) return;
      
      this.resetTest();
      this.isRunning = true;
      this.testStatus = '进行中';
      this.addLog('开始运行完整集成测试', 'info');
      
      try {
        // 增加测试总数
        this.testStats.total = 6;
        
        // 先运行API测试
        await this.runApiTest();
        if (this.testStats.failed > 0) {
          throw new Error('API测试失败，停止集成测试');
        }
        
        // 测试6: 流程导航
        this.updateStepStatus('navigation', 'running');
        await this.testNavigation();
        this.testStats.passed++;
        this.updateStepStatus('navigation', 'completed');
        
        // 测试成功
        this.testStatus = '成功';
        this.addLog('完整集成测试全部通过！', 'success');
        
      } catch (error) {
        this.testStats.failed++;
        this.testStatus = '失败';
        this.addError('集成测试', '测试运行过程中发生错误', error.message);
      } finally {
        this.isRunning = false;
      }
    },
    
    // 测试1: 创建剧本
    async testCreateScript() {
      this.addLog('开始创建剧本...');
      try {
        const response = await axios.post('/api/v1/tasks/script', {
          script: '这是一个测试剧本。\n第一幕：早上的咖啡厅。\n小明走进咖啡厅，点了一杯咖啡。\n服务员：您的咖啡好了。\n小明：谢谢。'
        });
        
        if (response.data.code !== 200) {
          throw new Error(`API返回错误: ${JSON.stringify(response.data)}`);
        }
        
        this.currentTaskId = response.data.data.task_id;
        this.taskCreationTime = new Date();
        this.addLog(`剧本创建成功！任务ID: ${this.currentTaskId}`, 'success');
        
      } catch (error) {
        this.addError('剧本创建', '创建剧本失败', error.message);
        this.updateStepStatus('script', 'failed');
        throw error;
      }
    },
    
    // 测试2: 更新角色场景
    async testUpdateCharacterScene() {
      if (!this.currentTaskId) {
        throw new Error('没有有效的任务ID');
      }
      
      this.addLog('开始更新角色和场景...');
      try {
        const response = await axios.post(`/api/v1/tasks/${this.currentTaskId}/character-scene`, {
          characters: [
            { name: '小明', description: '主角，年轻的上班族' },
            { name: '服务员', description: '咖啡厅服务员' }
          ],
          scenes: [
            { name: '咖啡厅', description: '一个温馨的街角咖啡厅，阳光透过窗户照射进来' }
          ]
        });
        
        if (response.data.code !== 200) {
          throw new Error(`API返回错误: ${JSON.stringify(response.data)}`);
        }
        
        this.addLog('角色和场景更新成功！', 'success');
        
      } catch (error) {
        this.addError('角色场景', '更新角色和场景失败', error.message);
        this.updateStepStatus('character-scene', 'failed');
        throw error;
      }
    },
    
    // 测试3: 生成分镜和保存
    async testStoryboard() {
      if (!this.currentTaskId) {
        throw new Error('没有有效的任务ID');
      }
      
      this.addLog('开始生成分镜...');
      try {
        // 先获取任务数据
        const taskResponse = await axios.get(`/api/v1/tasks/${this.currentTaskId}`);
        if (taskResponse.data.code !== 200) {
          throw new Error(`获取任务数据失败: ${JSON.stringify(taskResponse.data)}`);
        }
        
        const taskData = taskResponse.data.data;
        
        // 生成分镜
        const generateResponse = await axios.post('/api/v1/tasks/script/storyboard', {
          script: taskData.script,
          characters: taskData.characters,
          scenes: taskData.scenes
        });
        
        if (generateResponse.data.code !== 200) {
          throw new Error(`生成分镜失败: ${JSON.stringify(generateResponse.data)}`);
        }
        
        const storyboards = generateResponse.data.data.storyboards;
        this.addLog(`成功生成 ${storyboards.length} 个分镜`);
        
        // 保存分镜
        this.addLog('保存分镜中...');
        const saveResponse = await axios.post('/api/v1/tasks/storyboards', {
          task_id: this.currentTaskId,
          storyboards
        });
        
        if (saveResponse.data.code !== 200) {
          throw new Error(`保存分镜失败: ${JSON.stringify(saveResponse.data)}`);
        }
        
        this.addLog('分镜保存成功！', 'success');
        
      } catch (error) {
        this.addError('分镜制作', '生成分镜或保存失败', error.message);
        this.updateStepStatus('storyboard', 'failed');
        throw error;
      }
    },
    
    // 测试4: 获取任务进度
    async testTaskProgress() {
      if (!this.currentTaskId) {
        throw new Error('没有有效的任务ID');
      }
      
      this.addLog('检查任务进度...');
      try {
        const response = await axios.get(`/api/v1/tasks/${this.currentTaskId}/progress`);
        
        if (response.data.code !== 200) {
          throw new Error(`获取任务进度失败: ${JSON.stringify(response.data)}`);
        }
        
        const progress = response.data.data.progress;
        this.addLog(`任务进度: ${JSON.stringify(progress)}`);
        
        // 验证进度状态
        if (!progress.script_completed) {
          throw new Error('剧本状态不正确');
        }
        if (!progress.character_scene_completed) {
          throw new Error('角色场景状态不正确');
        }
        if (!progress.storyboard_completed) {
          throw new Error('分镜状态不正确');
        }
        
        this.addLog('任务进度检查通过！', 'success');
        
      } catch (error) {
        this.addError('进度检查', '检查任务进度失败', error.message);
        this.updateStepStatus('progress', 'failed');
        throw error;
      }
    },
    
    // 测试5: 获取背景音乐类型
    async testBgmTypes() {
      if (!this.currentTaskId) {
        throw new Error('没有有效的任务ID');
      }
      
      this.addLog('获取背景音乐类型...');
      try {
        const response = await axios.get(`/api/v1/tasks/${this.currentTaskId}/bgm-types`);
        
        if (response.data.code !== 200) {
          throw new Error(`获取背景音乐类型失败: ${JSON.stringify(response.data)}`);
        }
        
        const bgmTypes = response.data.data.bgm_types;
        this.addLog(`获取到 ${bgmTypes.length} 种背景音乐类型`);
        
        if (bgmTypes.length === 0) {
          throw new Error('背景音乐类型列表为空');
        }
        
        this.addLog('背景音乐类型获取成功！', 'success');
        
      } catch (error) {
        this.addError('背景音乐', '获取背景音乐类型失败', error.message);
        this.updateStepStatus('bgm', 'failed');
        throw error;
      }
    },
    
    // 测试6: 流程导航
    async testNavigation() {
      this.addLog('测试流程导航功能...');
      try {
        // 模拟导航状态检查
        const navigationState = {
          currentStep: 'storyboard',
          completedSteps: ['script', 'character-scene', 'storyboard'],
          pendingSteps: ['bgm', 'video', 'export']
        };
        
        this.addLog(`导航状态: ${JSON.stringify(navigationState)}`);
        
        // 测试本地存储
        localStorage.setItem('currentTaskId', this.currentTaskId);
        const storedTaskId = localStorage.getItem('currentTaskId');
        
        if (storedTaskId !== this.currentTaskId) {
          throw new Error('本地存储任务ID失败');
        }
        
        this.addLog('流程导航测试通过！', 'success');
        
      } catch (error) {
        this.addError('流程导航', '测试流程导航失败', error.message);
        this.updateStepStatus('navigation', 'failed');
        throw error;
      }
    },
    
    // 加载任务详情
    async loadTaskDetails() {
      if (!this.currentTaskId) return;
      
      try {
        this.addLog(`加载任务 ${this.currentTaskId} 详情...`);
        const response = await axios.get(`/api/v1/tasks/${this.currentTaskId}`);
        
        if (response.data.code === 200) {
          this.taskDetails = response.data.data;
          this.addLog('任务详情加载成功！');
          
          // 显示任务详情对话框
          this.showTaskDetails();
        } else {
          throw new Error(`加载失败: ${JSON.stringify(response.data)}`);
        }
      } catch (error) {
        this.addError('任务详情', '加载任务详情失败', error.message);
      }
    },
    
    // 显示任务详情
    showTaskDetails() {
      if (!this.taskDetails) return;
      
      // 在实际应用中，这里可以使用模态框显示任务详情
      this.addLog('任务详情已加载，包括剧本、角色、场景和分镜数据');
      
      // 打印主要信息
      console.log('任务详情:', {
        taskId: this.taskDetails.task_id,
        scriptLength: this.taskDetails.script ? this.taskDetails.script.length : 0,
        characterCount: this.taskDetails.characters ? this.taskDetails.characters.length : 0,
        sceneCount: this.taskDetails.scenes ? this.taskDetails.scenes.length : 0,
        storyboardCount: this.taskDetails.storyboards ? this.taskDetails.storyboards.length : 0
      });
    }
  }
};
</script>

<style scoped>
.integration-test-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 30px;
}

.control-panel {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  justify-content: center;
  flex-wrap: wrap;
}

.control-panel button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.control-panel button:hover:not(:disabled) {
  background-color: #45a049;
}

.control-panel button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.test-results {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.result-summary {
  display: flex;
  justify-content: space-around;
  background-color: white;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-item .label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.summary-item .value.success {
  color: #4CAF50;
}

.summary-item .value.error {
  color: #f44336;
}

.summary-item .value.running {
  color: #2196F3;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.test-logs h3,
.error-details h3,
.test-visualization h3,
.task-info h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  border-bottom: 2px solid #ddd;
  padding-bottom: 8px;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  background-color: #2d2d2d;
  color: #e0e0e0;
  padding: 15px;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.log-item {
  margin-bottom: 5px;
  padding: 3px 0;
}

.log-item .timestamp {
  color: #888;
  margin-right: 10px;
}

.log-item.info .content {
  color: #e0e0e0;
}

.log-item.success .content {
  color: #4CAF50;
}

.log-item.error .content {
  color: #f44336;
}

.log-item.warning .content {
  color: #ff9800;
}

.error-details {
  margin-top: 30px;
}

.errors-list {
  background-color: #ffebee;
  border-left: 4px solid #f44336;
  padding: 15px;
  border-radius: 6px;
}

.error-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ffcdd2;
}

.error-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.error-item strong {
  color: #c62828;
}

.error-stack {
  margin-top: 10px;
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #666;
  max-height: 150px;
  overflow-y: auto;
}

.test-visualization {
  margin-bottom: 30px;
}

.flow-diagram {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.step-item {
  flex: 1;
  min-width: 150px;
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  background-color: #f5f5f5;
  border: 2px solid #ddd;
  transition: all 0.3s;
}

.step-item.completed {
  background-color: #e8f5e9;
  border-color: #4CAF50;
  box-shadow: 0 0 10px rgba(76, 175, 80, 0.2);
}

.step-item.failed {
  background-color: #ffebee;
  border-color: #f44336;
  box-shadow: 0 0 10px rgba(244, 67, 54, 0.2);
}

.step-item.running {
  background-color: #e3f2fd;
  border-color: #2196F3;
  box-shadow: 0 0 10px rgba(33, 150, 243, 0.2);
  animation: pulse 1s infinite;
}

.step-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.step-label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
}

.step-status {
  font-size: 14px;
  color: #666;
}

.task-info {
  background-color: #e3f2fd;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #2196F3;
}

.task-info p {
  margin: 8px 0;
  color: #333;
}

.task-info button {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.task-info button:hover {
  background-color: #0b7dda;
}

@media (max-width: 768px) {
  .control-panel {
    flex-direction: column;
  }
  
  .flow-diagram {
    flex-direction: column;
  }
  
  .step-item {
    min-width: auto;
  }
  
  .result-summary {
    flex-direction: column;
    align-items: center;
  }
}
</style>