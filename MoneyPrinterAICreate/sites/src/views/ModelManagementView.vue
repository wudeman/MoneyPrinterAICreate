<template>
  <div class="model-management-container">
    <!-- 列表页面 -->
    <el-container class="model-list-page">
      <el-main>
        <!-- 搜索和操作栏 -->
        <div class="search-filter-bar">
          <div class="left-filters">
            <span class="filter-label">模型类型：</span>
            <el-select 
              v-model="searchParams.modelTypeFilter"
              placeholder="全部模型类型"
              clearable
              class="filter-select"
            >
              <el-option value="" label="全部模型类型"></el-option>
              <el-option value="text" label="文本模型"></el-option>
              <el-option value="image" label="图像模型"></el-option>
              <el-option value="video" label="视频模型"></el-option>
              <el-option value="audio" label="音频模型"></el-option>
            </el-select>
          </div>
          <div class="right-actions">
            <span class="filter-label">模型名称：</span>
            <el-input 
              v-model="searchParams.searchName"
              placeholder="搜索模型名称"
              clearable
            ></el-input>
            <el-button type="primary" @click="handleSearch">
              查询
            </el-button>
            <el-button @click="refreshList">
              重置
            </el-button>
            <el-button type="success" @click="handleAddModel">
              新增
            </el-button>
          </div>
        </div>

        <!-- 模型表格 -->
        <div class="table-container">
          <el-table 
            v-loading="isLoading" 
            :data="paginatedModels" 
            class="model-table"
            border
            stripe
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" align="center"></el-table-column>
            <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
            <el-table-column prop="display_name" label="展示名称" align="center" min-width="120"></el-table-column>
            <el-table-column prop="model_name" label="模型名称" align="center" min-width="120"></el-table-column>
            <el-table-column prop="model_provider" label="模型供应商" align="center" min-width="120"></el-table-column>
            <el-table-column prop="base_url" label="调用地址" align="center" min-width="200">
              <template #default="scope">
                <el-tooltip :content="scope.row.base_url || '无'" placement="top">
                  <div class="text-truncate">{{ scope.row.base_url || '无' }}</div>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="api_key" label="密钥" align="center" min-width="180">
              <template #default="scope">
                <div class="key-display">
                  <el-input
                    v-if="keyVisibility[scope.row.id]"
                    v-model="scope.row.api_key"
                    type="text"
                    readonly
                    size="small"
                    class="key-input"
                  >
                    <template #append>
                      <el-button 
                        @click="toggleKeyVisibility(scope.row.id)"
                        :icon="View"
                        size="small"
                      />
                    </template>
                  </el-input>
                  <el-input
                    v-else
                    :model-value="scope.row.api_key ? '●'.repeat(12) : '无'"
                    type="password"
                    readonly
                    size="small"
                    class="key-input"
                  >
                    <template #append>
                      <el-button 
                        @click="toggleKeyVisibility(scope.row.id)"
                        :icon="Hide"
                        size="small"
                      />
                    </template>
                  </el-input>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="模型类型" align="center" width="100">
              <template #default="scope">
                <el-tag :type="getModelTypeTagType(scope.row.model_type)">
                  {{ getModelTypeText(scope.row.model_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="参考图" align="center" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.support_reference_image ? 'success' : 'info'" size="small">
                  {{ scope.row.support_reference_image ? '支持' : '不支持' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="多参考图" align="center" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.support_multiple_reference_images ? 'success' : 'info'" size="small">
                  {{ scope.row.support_multiple_reference_images ? '支持' : '不支持' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="首帧" align="center" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.support_first_frame ? 'success' : 'info'" size="small">
                  {{ scope.row.support_first_frame ? '支持' : '不支持' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="尾帧" align="center" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.support_last_frame ? 'success' : 'info'" size="small">
                  {{ scope.row.support_last_frame ? '支持' : '不支持' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" align="center" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
                  {{ scope.row.status === 1 ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="operator" label="操作人" align="center" width="100"></el-table-column>
            <el-table-column label="更新时间" align="center" width="160">
              <template #default="scope">
                {{ formatUpdateTimeText(scope.row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="200" fixed="right">
              <template #default="scope">
                <div class="action-buttons">
                  <el-button type="primary" size="small" @click="handleEditModel(scope.row)">
                    编辑
                  </el-button>
                  <el-button 
                    :type="scope.row.status === 1 ? 'warning' : 'success'" 
                    size="small" 
                    @click="toggleModelStatus(scope.row.id, scope.row.status === 0)"
                  >
                    {{ scope.row.status === 1 ? '禁用' : '启用' }}
                  </el-button>
                  <el-popconfirm
                    :title="`确认删除模型 ${scope.row.display_name} 吗？`"
                    confirm-button-text="确认"
                    cancel-button-text="取消"
                    @confirm="handleDeleteModel(scope.row.id, scope.row.display_name)"
                  >
                    <template #reference>
                      <el-button type="danger" size="small">
                        删除
                      </el-button>
                    </template>
                  </el-popconfirm>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页控件 -->
        <div class="pagination-container">
          <el-pagination
            v-if="total > 0"
            v-model:current-page="currentPageNum"
            v-model:page-size="searchParams.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-main>
    </el-container>

    <!-- 新增/编辑模型弹框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
      :destroy-on-close="true"
    >
      <el-form
        ref="modelFormRef"
        :model="formData"
        label-width="100px"
        :rules="formRules"
        class="model-form"
      >
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-form-item label="展示名称" prop="display_name">
          <el-input
            v-model="formData.display_name"
            placeholder="请输入模型展示名称"
            maxlength="50"
            show-word-limit
          ></el-input>
        </el-form-item>
        
        <el-form-item label="模型名称" prop="model_name">
          <el-input
            v-model="formData.model_name"
            placeholder="请输入模型名称"
            maxlength="50"
            show-word-limit
          ></el-input>
        </el-form-item>
        
        <el-form-item label="模型供应商" prop="model_provider">
          <el-input
            v-model="formData.model_provider"
            placeholder="请输入模型供应商"
            maxlength="50"
            show-word-limit
          ></el-input>
        </el-form-item>
        
        <el-form-item label="调用地址">
          <el-input 
            v-model="formData.base_url"
            placeholder="请输入模型调用地址"
            clearable
          ></el-input>
        </el-form-item>
        
        <el-form-item label="密钥">
          <el-input 
            v-model="formData.api_key"
            :type="showApiKey ? 'text' : 'password'"
            :placeholder="isEditMode ? '输入新密钥或留空保持原密钥' : '请输入模型密钥（若有）'"
          >
            <template #append>
              <el-button 
                :icon="showApiKey ? View : Hide" 
                @click="showApiKey = !showApiKey"
              />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="模型类型" prop="model_type">
          <el-select 
            v-model="formData.model_type"
            placeholder="请选择模型类型"
            style="width: 100%"
          >
            <el-option value="text" label="文本模型"></el-option>
            <el-option value="image" label="图像模型"></el-option>
            <el-option value="video" label="视频模型"></el-option>
            <el-option value="audio" label="音频模型"></el-option>
          </el-select>
        </el-form-item>

        <el-divider content-position="left">特性支持</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="参考图支持">
              <el-switch v-model="formData.support_reference_image"></el-switch>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="多参考图支持">
              <el-switch v-model="formData.support_multiple_reference_images"></el-switch>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="首帧支持">
              <el-switch v-model="formData.support_first_frame"></el-switch>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="尾帧支持">
              <el-switch v-model="formData.support_last_frame"></el-switch>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="状态">
          <el-switch
            v-model="formData.status"
            active-text="启用"
            inactive-text="禁用"
          ></el-switch>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveModel" :loading="isSaving">
            {{ isEditMode ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, nextTick } from 'vue';
import { 
  Search, Plus, View, Hide
} from '@element-plus/icons-vue';
import type { ElForm } from 'element-plus';
import { ElMessage } from 'element-plus';

// 模型接口定义
interface LLMModel {
  id: number;
  display_name: string;
  model_name: string;
  base_url?: string | null;
  api_key?: string | null;
  model_type: string;
  support_reference_image: boolean;
  support_multiple_reference_images: boolean;
  support_first_frame: boolean;
  support_last_frame: boolean;
  status: number;
  operator?: string;
  updated_at?: string;
  created_at?: string;
}

// 表单数据接口定义
interface ModelFormData {
  display_name: string;
  model_name: string;
  base_url: string;
  api_key: string;
  model_type: string;
  support_reference_image: boolean;
  support_multiple_reference_images: boolean;
  support_first_frame: boolean;
  support_last_frame: boolean;
  status: boolean;
}

// 搜索参数
const searchParams = reactive({
  searchName: '',
  modelTypeFilter: '',
  pageSize: 10
});

// 页面状态
const currentPageNum = ref(1);
const isLoading = ref(false);
const isSaving = ref(false);
const models = ref<LLMModel[]>([]);
const total = ref(0);
const modelFormRef = ref<InstanceType<typeof ElForm>>();

// 弹框相关状态
const dialogVisible = ref(false);
const isEditMode = ref(false);
const showApiKey = ref(false);
const selectedModel = ref<LLMModel | null>(null);
const dialogTitle = computed(() => isEditMode.value ? `编辑模型: ${selectedModel.value?.display_name}` : '新增模型');

// 密钥显示状态
const keyVisibility = ref<Record<number, boolean>>({});

// 表单验证规则
const formRules = {
  display_name: [
    { required: true, message: '请输入模型展示名称', trigger: 'blur' },
    { min: 1, max: 50, message: '展示名称长度应在 1 到 50 个字符之间', trigger: 'blur' }
  ],
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 1, max: 50, message: '模型名称长度应在 1 到 50 个字符之间', trigger: 'blur' }
  ],
  model_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ]
};

// 表单数据
const formData = reactive<ModelFormData>({
  display_name: '',
  model_name: '',
  model_provider: '',
  base_url: '',
  api_key: '',
  model_type: 'text',
  support_reference_image: false,
  support_multiple_reference_images: false,
  support_first_frame: false,
  support_last_frame: false,
  status: true
});

// 计算属性
const paginatedModels = computed(() => models.value);

// 方法
const fetchModels = async () => {
  isLoading.value = true;
  try {
    const response = await fetch('/api/v1/models/list', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        page: currentPageNum.value,
        page_size: searchParams.pageSize,
        display_name: searchParams.searchName,
        model_type: searchParams.modelTypeFilter || null
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || errorData.error || '获取模型列表失败');
    }
    
    const data = await response.json();
    models.value = data.models || [];
    total.value = data.total || 0;
    ElMessage.success('模型列表加载成功');
  } catch (error: any) {
    console.error('获取模型列表失败:', error);
    ElMessage.error(error.message || '获取模型列表失败，请重试');
  } finally {
    isLoading.value = false;
  }
};

const getModelTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    'text': '文本模型',
    'image': '图像模型',
    'video': '视频模型',
    'audio': '音频模型'
  };
  return typeMap[type] || type;
};

const getModelTypeTagType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'text': '',
    'image': 'warning',
    'video': 'success',
    'audio': 'info'
  };
  return typeMap[type] || '';
};

const formatUpdateTimeText = (timeStr?: string): string => {
  if (!timeStr) return '-';
  try {
    const date = new Date(timeStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return timeStr;
  }
};

const toggleKeyVisibility = (modelId: number) => {
  keyVisibility.value[modelId] = !keyVisibility.value[modelId];
};

const handleSearch = () => {
  currentPageNum.value = 1;
  fetchModels();
};

const handleAddModel = () => {
  resetForm();
  isEditMode.value = false;
  showApiKey.value = false;
  dialogVisible.value = true;
  selectedModel.value = null;
  
  nextTick(() => {
    modelFormRef.value?.clearValidate();
  });
};

const handleEditModel = (model: LLMModel) => {
  selectedModel.value = model;
  isEditMode.value = true;
  showApiKey.value = false;
  
  // 填充表单数据
  Object.assign(formData, {
    display_name: model.display_name,
    model_name: model.model_name,
    model_provider: model.model_provider || '',
    base_url: model.base_url || '',
    api_key: '', // 不显示原密钥
    model_type: model.model_type,
    support_reference_image: model.support_reference_image,
    support_multiple_reference_images: model.support_multiple_reference_images,
    support_first_frame: model.support_first_frame,
    support_last_frame: model.support_last_frame,
    status: model.status === 1
  });
  
  dialogVisible.value = true;
  
  nextTick(() => {
    modelFormRef.value?.clearValidate();
  });
};

const handleDeleteModel = async (modelId: number, displayName: string) => {
  isLoading.value = true;
  try {
    const response = await fetch(`/api/v1/models/${modelId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || errorData.error || '删除模型失败');
    }
    
    models.value = models.value.filter(model => model.id !== modelId);
    ElMessage.success(`模型 ${displayName} 删除成功`);
  } catch (error: any) {
    console.error('删除模型失败:', error);
    ElMessage.error(error.message || '删除模型失败，请重试');
  } finally {
    isLoading.value = false;
  }
};

const toggleModelStatus = async (modelId: number, enable: boolean) => {
  isLoading.value = true;
  try {
    const response = await fetch(`/api/v1/models/${modelId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: enable ? 1 : 0
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || errorData.error || '更新模型状态失败');
    }
    
    const result = await response.json();
    const modelIndex = models.value.findIndex(m => m.id === modelId);
    if (modelIndex !== -1) {
      models.value[modelIndex] = result;
    }
    
    ElMessage.success(`模型状态已${enable ? '启用' : '禁用'}`);
  } catch (error: any) {
    console.error('更新模型状态失败:', error);
    ElMessage.error(error.message || '更新模型状态失败，请重试');
  } finally {
    isLoading.value = false;
  }
};

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  searchParams.pageSize = size;
  currentPageNum.value = 1;
  fetchModels();
};

// 处理当前页变化
const handleCurrentChange = (current: number) => {
  currentPageNum.value = current;
  fetchModels();
};

const refreshList = () => {
  searchParams.searchName = '';
  searchParams.modelTypeFilter = '';
  currentPageNum.value = 1;
  fetchModels();
};

const resetForm = () => {
  Object.assign(formData, {
    display_name: '',
    model_name: '',
    model_provider: '',
    base_url: '',
    api_key: '',
    model_type: 'text',
    support_reference_image: false,
    support_multiple_reference_images: false,
    support_first_frame: false,
    support_last_frame: false,
    status: true
  });
};

const handleSaveModel = async () => {
  try {
    await modelFormRef.value?.validate();
    
    isSaving.value = true;
    
    let apiUrl = '';
    let method = '';
    let body: any = {};
    
    if (!isEditMode.value) {
      // 添加新模型
      apiUrl = '/api/v1/models/add';
      method = 'POST';
      body = {
        display_name: formData.display_name,
        model_name: formData.model_name,
        model_provider: formData.model_provider || undefined,
        base_url: formData.base_url || undefined,
        api_key: formData.api_key || undefined,
        model_type: formData.model_type,
        support_reference_image: formData.support_reference_image,
        support_multiple_reference_images: formData.support_multiple_reference_images,
        support_first_frame: formData.support_first_frame,
        support_last_frame: formData.support_last_frame,
        status: formData.status ? 1 : 0
      };
    } else if (isEditMode.value && selectedModel.value) {
      // 更新模型
      apiUrl = `/api/v1/models/${selectedModel.value.id}`;
      method = 'PUT';
      body = {
        display_name: formData.display_name,
        model_name: formData.model_name,
        model_provider: formData.model_provider || undefined,
        base_url: formData.base_url || undefined,
        model_type: formData.model_type,
        support_reference_image: formData.support_reference_image,
        support_multiple_reference_images: formData.support_multiple_reference_images,
        support_first_frame: formData.support_first_frame,
        support_last_frame: formData.support_last_frame,
        status: formData.status ? 1 : 0
      };
      // 只有在输入了新密钥时才更新
      if (formData.api_key) {
        body.api_key = formData.api_key;
      }
    }
    
    const response = await fetch(apiUrl, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || errorData.error || '保存模型失败');
    }
    
    const result = await response.json();
    
    if (!isEditMode.value) {
      models.value.unshift(result);
      ElMessage.success('模型创建成功！');
    } else if (isEditMode.value && selectedModel.value) {
      const modelIndex = models.value.findIndex(m => m.id === selectedModel.value?.id);
      if (modelIndex !== -1) {
        models.value[modelIndex] = result;
      }
      ElMessage.success('模型更新成功！');
    }
    
    dialogVisible.value = false;
    fetchModels();
  } catch (error: any) {
    console.error('保存模型失败:', error);
    ElMessage.error(error.message || '保存模型失败，请重试');
  } finally {
    isSaving.value = false;
  }
};

// 处理复选框选择
const selectedRows = ref<LLMModel[]>([]);
const handleSelectionChange = (val: LLMModel[]) => {
  selectedRows.value = val;
};

// 组件挂载时获取模型列表
  onMounted(() => {
    fetchModels();
  });
</script>

<style scoped>
.model-management-container {
  padding: 20px;
  background-color: #ffffff;
  width: 100%;
  box-sizing: border-box;
  min-height: calc(100vh - 40px);
}

.model-list-page {
  width: 100%;
  margin: 0 auto;
}
.search-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 16px 20px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 16px;
  gap: 12px;
}

.filter-label {
  margin-right: 8px;
  white-space: nowrap;
  color: #606266;
  font-size: 14px;
}

.filter-select {
  width: 200px;
}

.search-input {
  width: 200px;
}

.left-filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.right-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-container {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.model-table {
  width: 100%;
  border-radius: 8px;
}

.model-table :deep(.el-table__header-wrapper) {
  background-color: #f5f7fa;
}

.model-table :deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  padding: 16px 0;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.key-display {
  display: flex;
  align-items: center;
}

.key-input {
  width: 180px;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
  align-items: center;
}

.model-form {
  margin-top: 10px;
}

.model-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.model-form :deep(.el-divider--horizontal) {
  margin: 20px 0;
}

.model-form :deep(.el-switch) {
  margin-left: 8px;
}

/* 弹框样式优化 */
:deep(.el-dialog__header) {
  padding: 20px 20px 10px;
  border-bottom: 1px solid #e9ecef;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px;
  border-top: 1px solid #e9ecef;
}

/* 响应式布局 */
@media screen and (max-width: 1200px) {
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .left-filters,
  .right-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}

@media screen and (max-width: 768px) {
  .model-management-container {
    padding: 12px;
  }
  
  .search-filter-bar {
    padding: 12px;
    margin-bottom: 12px;
  }
  
  .filter-select,
  .search-input {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .right-actions {
    flex-wrap: wrap;
  }
  
  .pagination-container {
    padding: 12px 0;
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 5% auto;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  .action-buttons .el-button {
    margin: 1px 0;
  }
}
</style>