<template>
  <div class="flow-navigation">
    <div class="flow-title">创作流程</div>
    <div class="flow-steps">
      <div
        v-for="(step, index) in steps"
        :key="step.id"
        :class="[
          'flow-step',
          { 'active': currentStep === index },
          { 'completed': completedSteps.includes(index) },
          { 'editable': canEditStep(index) }
        ]"
        @click="handleStepClick(index)"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-title">{{ step.title }}</div>
        <div v-if="completedSteps.includes(index)" class="step-status">✓</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

// Props
const props = defineProps<{
  taskId?: string;
}>();

// Emits
const emit = defineEmits<{
  (e: 'step-change', stepIndex: number): void;
}>();

const router = useRouter();
const route = useRoute();

// 流程步骤定义
const steps = [
  { id: 'script', title: '剧本创作', path: '/script-edit' },
  { id: 'character-scene', title: '角色场景设计', path: '/character-scene' },
  { id: 'storyboard', title: '分镜制作', path: '/storyboard' },
  { id: 'media-generation', title: '媒体生成', path: '/media-generation' },
  { id: 'video-synthesis', title: '视频合成', path: '/video-synthesis' },
  { id: 'model-management', title: '模型管理', path: '/model-management' }
];

// 当前任务ID
const currentTaskId = ref(props.taskId || localStorage.getItem('currentTaskId') || '');

// 已完成的步骤
const completedSteps = ref<number[]>([]);

// 当前步骤索引
const currentStep = ref(0);

// 根据当前路由确定当前步骤
const determineCurrentStep = () => {
  const currentPath = route.path;
  const stepIndex = steps.findIndex(step => currentPath.includes(step.path));
  if (stepIndex !== -1) {
    currentStep.value = stepIndex;
  }
};

// 检查是否可以编辑某个步骤
const canEditStep = (index: number) => {
  // 已完成的步骤可以编辑，当前步骤也可以编辑
  return completedSteps.value.includes(index) || currentStep.value === index;
};

// 处理步骤点击
const handleStepClick = (index: number) => {
  if (canEditStep(index)) {
    // 导航到对应步骤
    router.push({
      path: steps[index].path,
      query: { taskId: currentTaskId.value }
    });
    emit('step-change', index);
  }
};

// 加载任务进度
  const loadTaskProgress = async () => {
    // 添加taskId非空检查
    if (!currentTaskId.value || currentTaskId.value === 'null') {
      console.log('任务ID不存在，跳过进度查询');
      return;
    }
    
    try {
      const response = await axios.get(`/api/v1/tasks/${currentTaskId.value}/progress`);
      
      if (response.data.code === 200 && response.data.data.progress) {
        const progress = response.data.data.progress;
        completedSteps.value = [];
        
        // 根据任务进度更新已完成步骤
        if (progress.script_completed) completedSteps.value.push(0);
        if (progress.character_scene_completed) completedSteps.value.push(1);
        if (progress.storyboard_completed) completedSteps.value.push(2);
        if (progress.media_generated) completedSteps.value.push(3);
        if (progress.video_synthesized) completedSteps.value.push(4);
        if (progress.model_completed) completedSteps.value.push(5);
      }
    } catch (error) {
      console.error('加载任务进度失败:', error);
      // 降级方案：基于当前路径和localStorage推断
      updateCompletedStepsFromLocalStorage();
    }
  };

// 从localStorage推断已完成步骤
const updateCompletedStepsFromLocalStorage = () => {
  const completedStepsFromLocal = [];
  
  // 检查每个步骤的完成状态
  if (localStorage.getItem('scriptCompleted') === 'true') {
    completedStepsFromLocal.push(0);
  }
  if (localStorage.getItem('characterSceneCompleted') === 'true') {
    completedStepsFromLocal.push(1);
  }
  if (localStorage.getItem('storyboardCompleted') === 'true') {
    completedStepsFromLocal.push(2);
  }
  
  completedSteps.value = completedStepsFromLocal;
};

// 更新任务ID
const updateTaskId = (newTaskId: string) => {
  currentTaskId.value = newTaskId;
  localStorage.setItem('currentTaskId', newTaskId);
  loadTaskProgress();
};

// 暴露方法给父组件
defineExpose({
  updateTaskId,
  loadTaskProgress
});

// 生命周期钩子
onMounted(() => {
  determineCurrentStep();
  loadTaskProgress();
});
</script>

<style scoped>
.flow-navigation {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.flow-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1rem;
}

.flow-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  position: relative;
}

/* 连接线 */
.flow-steps::before {
  content: '';
  position: absolute;
  top: 1.25rem;
  left: 1.25rem;
  right: 1.25rem;
  height: 2px;
  background: #e2e8f0;
  z-index: 0;
}

.flow-step {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #f1f5f9;
  border-radius: 8px;
  cursor: not-allowed;
  opacity: 0.6;
  transition: all 0.3s ease;
  z-index: 1;
  min-width: 120px;
}

.flow-step:hover:not(.editable) {
  background: #e2e8f0;
}

.flow-step.editable {
  cursor: pointer;
  opacity: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.flow-step.editable:hover {
  background: #eff6ff;
  border-color: #3b82f6;
  transform: translateY(-1px);
}

.flow-step.active {
  background: #dbeafe;
  border: 1px solid #3b82f6;
  opacity: 1;
  cursor: default;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.flow-step.completed {
  background: #d1fae5;
  border: 1px solid #10b981;
  opacity: 1;
}

.flow-step.completed.editable:hover {
  background: #a7f3d0;
  border-color: #059669;
}

.step-number {
  width: 1.75rem;
  height: 1.75rem;
  background: #94a3b8;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
}

.flow-step.active .step-number {
  background: #3b82f6;
}

.flow-step.completed .step-number {
  background: #10b981;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  white-space: nowrap;
}

.flow-step.active .step-title {
  color: #1d4ed8;
}

.flow-step.completed .step-title {
  color: #065f46;
}

.step-status {
  color: #10b981;
  font-size: 1rem;
  font-weight: bold;
  margin-left: auto;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .flow-steps {
    flex-direction: column;
  }
  
  .flow-steps::before {
    display: none;
  }
  
  .flow-step {
    min-width: auto;
  }
}
</style>