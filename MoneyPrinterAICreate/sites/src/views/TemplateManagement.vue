<template>
  <div class="template-management-container">
    <!-- 列表页面 -->
    <el-container class="template-list-page">
      <el-main>
        <!-- 搜索和操作栏 -->
        <div class="search-filter-bar">
          <div class="left-filters">
            <span class="filter-label">模板状态：</span>
            <el-select 
              v-model="searchParams.statusFilter"
              placeholder="全部状态"
              clearable
              class="filter-select"
            >
              <el-option value="" label="全部状态"></el-option>
              <el-option value="active" label="激活"></el-option>
              <el-option value="inactive" label="停用"></el-option>
            </el-select>
          </div>
          <div class="right-actions">
            <span class="filter-label">模板名称：</span>
            <el-input 
              v-model="searchParams.searchName"
              placeholder="搜索模板名称"
              clearable
              style="width: 200px;"
            ></el-input>
            <el-button type="primary" @click="handleSearch">
              查询
            </el-button>
            <el-button @click="refreshList">
              重置
            </el-button>
            <el-button type="success" @click="handleAddTemplate">
              新增
            </el-button>
          </div>
        </div>

        <!-- 模板表格 -->
        <div class="table-container">
          <el-table 
            v-loading="isLoading" 
            :data="templates" 
            class="template-table"
            border
            stripe
          >
            <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
            <el-table-column prop="id" label="模板ID" align="center" width="80"></el-table-column>
            <el-table-column prop="template_name" label="模板名称" align="center" min-width="150"></el-table-column>
            <el-table-column label="状态" align="center" width="100">
              <template #default="scope">
                <el-tag :type="getTemplateStatusType(scope.row.status)">
                  {{ getTemplateStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="script_prompt" label="剧本创作提示词" align="center" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="character_prompt" label="角色创建提示词" align="center" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="scene_prompt" label="场景创建提示词" align="center" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="shot_prompt" label="分镜制作提示词" align="center" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="image_description_prompt" label="画面描述提示词" align="center" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="bgm_prompt" label="背景音乐提示词" align="center" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="video_generation_prompt" label="视频生成提示词" align="center" min-width="150" show-overflow-tooltip></el-table-column>
            <el-table-column prop="operator" label="操作人" align="center" width="120"></el-table-column>
            <el-table-column label="创建时间" align="center" width="180">
              <template #default="scope">
                {{ formatDateText(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="200" fixed="right">
              <template #default="scope">
                <div class="action-buttons">
                  <el-button type="primary" size="small" @click="handleEditTemplate(scope.row)">
                    编辑
                  </el-button>
                  <el-button 
                    :type="scope.row.status === 'active' ? 'warning' : 'success'" 
                    size="small" 
                    @click="toggleTemplateStatus(scope.row.id, scope.row.status === 'inactive')"
                  >
                    {{ scope.row.status === 'active' ? '停用' : '激活' }}
                  </el-button>
                  <el-popconfirm
                    :title="`确认删除模板 ${scope.row.template_name} 吗？`"
                    confirm-button-text="确认"
                    cancel-button-text="取消"
                    @confirm="handleDeleteTemplate(scope.row.id, scope.row.template_name)"
                  >
                    <template #reference>
                      <el-button 
                        type="danger" 
                        size="small"
                      >
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

    <!-- 新增/编辑模板弹框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="templateFormRef"
        :model="formData"
        :rules="formRules"
        label-width="150px"
        class="template-form"
      >
        <el-form-item label="模板名称" prop="template_name">
          <el-input
            v-model="formData.template_name"
            placeholder="请输入模板名称"
            maxlength="255"
          ></el-input>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="formData.status"
            active-value="active"
            inactive-value="inactive"
            active-text="激活"
            inactive-text="停用"
          ></el-switch>
        </el-form-item>

        <el-form-item label="剧本创作提示词" prop="script_prompt">
          <el-input
            v-model="formData.script_prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入剧本创作提示词"
          ></el-input>
        </el-form-item>

        <el-form-item label="角色创建提示词" prop="character_prompt">
          <el-input
            v-model="formData.character_prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入角色创建提示词"
          ></el-input>
        </el-form-item>

        <el-form-item label="场景创建提示词" prop="scene_prompt">
          <el-input
            v-model="formData.scene_prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入场景创建提示词"
          ></el-input>
        </el-form-item>

        <el-form-item label="分镜制作提示词" prop="shot_prompt">
          <el-input
            v-model="formData.shot_prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入分镜制作提示词"
          ></el-input>
        </el-form-item>

        <el-form-item label="画面描述生成提示词" prop="image_description_prompt">
          <el-input
            v-model="formData.image_description_prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入画面描述生成提示词"
          ></el-input>
        </el-form-item>

        <el-form-item label="背景音乐创造提示词" prop="bgm_prompt">
          <el-input
            v-model="formData.bgm_prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入背景音乐创造提示词"
          ></el-input>
        </el-form-item>

        <el-form-item label="视频画面生成提示词" prop="video_generation_prompt">
          <el-input
            v-model="formData.video_generation_prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入视频画面生成提示词"
          ></el-input>
        </el-form-item>

        <!-- 操作人由后端自动赋值 -->
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="handleFormSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 表格数据相关
const templates = ref<any[]>([])
const total = ref(0)
const isLoading = ref(false)
const currentPageNum = ref(1)
const searchParams = reactive({
  statusFilter: '',
  searchName: '',
  pageSize: 10
})

// 弹窗相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const templateFormRef = ref()

// 表单数据
const formData = reactive({
  id: '',
  template_name: '',
  status: 'active',
  script_prompt: '',
  character_prompt: '',
  scene_prompt: '',
  shot_prompt: '',
  image_description_prompt: '',
  bgm_prompt: '',
  video_generation_prompt: '',

})

// 表单验证规则
const formRules = reactive({
  template_name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { max: 255, message: '模板名称不能超过255个字符', trigger: 'blur' }
  ],

})

// 获取模板列表
async function getTemplates() {
  isLoading.value = true
  try {
    const response = await axios.get('/api/v1/templates', {
      params: {
        page: currentPageNum.value,
        page_size: searchParams.pageSize,
        status: searchParams.statusFilter || undefined,
        keyword: searchParams.searchName || undefined
      }
    })
    templates.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取模板列表失败: ' + (error.response?.data?.detail || error.message))
    templates.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

// 查询
function handleSearch() {
  currentPageNum.value = 1
  getTemplates()
}

// 重置
function refreshList() {
  searchParams.statusFilter = ''
  searchParams.searchName = ''
  currentPageNum.value = 1
  getTemplates()
}

// 新增模板
function handleAddTemplate() {
  dialogTitle.value = '新增模板'
  resetForm()
  dialogVisible.value = true
}

// 编辑模板
function handleEditTemplate(template: any) {
  dialogTitle.value = '编辑模板'
  formData.id = template.id
  formData.template_name = template.template_name
  formData.status = template.status
  formData.script_prompt = template.script_prompt || ''
  formData.character_prompt = template.character_prompt || ''
  formData.scene_prompt = template.scene_prompt || ''
  formData.shot_prompt = template.shot_prompt || ''
  formData.image_description_prompt = template.image_description_prompt || ''
  formData.bgm_prompt = template.bgm_prompt || ''
  formData.video_generation_prompt = template.video_generation_prompt || ''

  dialogVisible.value = true
}

// 切换模板状态
async function toggleTemplateStatus(id: number, isActive: boolean) {
  try {
    await axios.put(`/api/v1/templates/${id}`, {
      status: isActive ? 'active' : 'inactive'
    })
    ElMessage.success(`模板${isActive ? '激活' : '停用'}成功`)
    getTemplates()
  } catch (error) {
    ElMessage.error(`模板${isActive ? '激活' : '停用'}失败: ` + (error.response?.data?.detail || error.message))
  }
}

// 删除模板
async function handleDeleteTemplate(id: number, name: string) {
  try {
    await axios.delete(`/api/v1/templates/${id}`)
    ElMessage.success(`模板 ${name} 删除成功`)
    getTemplates()
  } catch (error) {
    ElMessage.error(`模板删除失败: ` + (error.response?.data?.detail || error.message))
  }
}

// 表单提交
async function handleFormSubmit() {
  if (!templateFormRef.value) return
  
  try {
    await templateFormRef.value.validate()
    
    if (formData.id) {
      // 更新模板
      // 移除id字段，后端不需要
      const updateData = { ...formData }
      delete updateData.id
      await axios.put(`/api/v1/templates/${formData.id}`, updateData)
      ElMessage.success('模板更新成功')
    } else {
      // 创建模板
      await axios.post('/api/v1/templates', formData)
      ElMessage.success('模板添加成功')
    }
    
    dialogVisible.value = false
    getTemplates()
  } catch (error) {
    if (error.name === 'Error') {
      ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// 关闭弹窗
function handleDialogClose() {
  dialogVisible.value = false
  resetForm()
  if (templateFormRef.value) {
    templateFormRef.value.resetFields()
  }
}

// 重置表单
function resetForm() {
  formData.id = ''
  formData.template_name = ''
  formData.status = 'active'
  formData.script_prompt = ''
  formData.character_prompt = ''
  formData.scene_prompt = ''
  formData.shot_prompt = ''
  formData.image_description_prompt = ''
  formData.bgm_prompt = ''
  formData.video_generation_prompt = ''

}

// 分页相关
function handleSizeChange(size: number) {
  searchParams.pageSize = size
  getTemplates()
}

function handleCurrentChange(current: number) {
  currentPageNum.value = current
  getTemplates()
}

// 获取模板状态标签类型
function getTemplateStatusType(status: string) {
  return status === 'active' ? 'success' : 'danger'
}

// 获取模板状态文本
function getTemplateStatusText(status: string) {
  return status === 'active' ? '激活' : '停用'
}

// 格式化日期
function formatDateText(dateString: string) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 初始化
onMounted(() => {
  getTemplates()
})
</script>

<style scoped>
.template-management-container {
  height: 100%;
}

.template-list-page {
  height: 100%;
  background-color: #f5f7fa;
}

.el-main {
  padding: 20px;
}

.search-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.left-filters,
.right-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  color: #606266;
  font-size: 14px;
}

.filter-select {
  width: 150px;
}

.right-actions .el-button {
  margin-left: 8px;
}

.table-container {
  background-color: #fff;
  border-radius: 6px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.template-table {
  width: 100%;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  background-color: #fff;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.template-form {
  max-height: 500px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 适配不同屏幕尺寸 */
@media (max-width: 1200px) {
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .left-filters,
  .right-actions {
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .el-main {
    padding: 10px;
  }
  
  .left-filters,
  .right-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .filter-select,
  .right-actions .el-input {
    width: 100%;
  }
  
  .right-actions .el-button {
    margin-left: 0;
  }
}
</style>