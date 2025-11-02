<template>
  <div class="dict-management-container">
    <!-- 列表页面 -->
    <el-container class="dict-list-page">
      <el-main>
        <!-- 搜索和操作栏 -->
        <div class="search-filter-bar">
          <div class="left-filters">
            <span class="filter-label">状态：</span>
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
            
            <span class="filter-label">字典类型：</span>
            <el-select 
              v-model="searchParams.typeFilter"
              placeholder="全部类型"
              clearable
              class="filter-select"
            >
              <el-option value="" label="全部类型"></el-option>
              <el-option 
                v-for="type in dictTypes" 
                :key="type" 
                :value="type" 
                :label="type"
              ></el-option>
            </el-select>
          </div>
          <div class="right-actions">
            <span class="filter-label">搜索：</span>
            <el-input 
              v-model="searchParams.searchKeyword"
              placeholder="搜索字典名称/键/值/描述"
              clearable
              style="width: 200px;"
            ></el-input>
            <el-button type="primary" @click="handleSearch">
              查询
            </el-button>
            <el-button @click="refreshList">
              重置
            </el-button>
            <el-button type="success" @click="handleAddDict">
              新增
            </el-button>
          </div>
        </div>

        <!-- 字典表格 -->
        <div class="table-container">
          <el-table 
            v-loading="isLoading" 
            :data="dicts" 
            class="dict-table"
            border
            stripe
          >
            <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
            <el-table-column prop="dict_name" label="字典名称" align="center" min-width="120"></el-table-column>
            <el-table-column prop="dict_key" label="字典键" align="center" min-width="100"></el-table-column>
            <el-table-column prop="dict_value" label="字典值" align="center" min-width="120"></el-table-column>
            <el-table-column prop="dict_type" label="字典类型" align="center" min-width="100"></el-table-column>
            <el-table-column prop="description" label="描述" align="center" min-width="150">
              <template #default="scope">
                <el-tooltip :content="scope.row.description || '无'" placement="top">
                  <div class="text-truncate">{{ scope.row.description || '无' }}</div>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="sort_order" label="排序" align="center" width="80"></el-table-column>
            <el-table-column prop="status" label="状态" align="center" width="80">
              <template #default="scope">
                <el-switch
                  v-model="scope.row.status"
                  active-value="active"
                  inactive-value="inactive"
                  @change="toggleDictStatus(scope.row.id, scope.row.status === 'active')"
                  :active-text="'激活'"
                  :inactive-text="'停用'"
                />
              </template>
            </el-table-column>
            <el-table-column prop="operator" label="操作人" align="center" width="100"></el-table-column>
            <el-table-column prop="created_at" label="创建时间" align="center" min-width="150">
              <template #default="scope">
                <span>{{ formatDateText(scope.row.created_at) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="180">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleEditDict(scope.row)"
                >
                  编辑
                </el-button>
                <el-popconfirm
                  :title="`确认删除字典 ${scope.row.dict_name} 吗？`"
                  confirm-button-text="确认"
                  cancel-button-text="取消"
                  @confirm="handleDeleteDict(scope.row.id, scope.row.dict_name)"
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

    <!-- 新增/编辑字典弹框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="dictFormRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="dict-form"
      >
        <el-form-item label="字典名称" prop="dict_name">
          <el-input v-model="formData.dict_name" placeholder="请输入字典名称"></el-input>
        </el-form-item>
        <el-form-item label="字典键" prop="dict_key">
          <el-input v-model="formData.dict_key" placeholder="请输入字典键"></el-input>
        </el-form-item>
        <el-form-item label="字典值" prop="dict_value">
          <el-input v-model="formData.dict_value" placeholder="请输入字典值"></el-input>
        </el-form-item>
        <el-form-item label="字典类型" prop="dict_type">
          <el-input v-model="formData.dict_type" placeholder="请输入字典类型（用于分类）"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="formData.description" 
            placeholder="请输入字典描述" 
            type="textarea"
            :rows="2"
          ></el-input>
        </el-form-item>
        <el-form-item label="排序序号">
          <el-input-number 
            v-model="formData.sort_order" 
            :min="0" 
            :max="999"
            placeholder="请输入排序序号"
          ></el-input-number>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="handleFormSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElForm, ElFormInstance } from 'element-plus'
import axios from 'axios'

// 响应式数据
const dicts = ref<any[]>([])
const total = ref(0)
const isLoading = ref(false)
const currentPageNum = ref(1)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dictTypes = ref<string[]>([])

// 表单相关
const dictFormRef = ref<ElFormInstance>()

const formData = reactive({
  id: '',
  dict_name: '',
  dict_key: '',
  dict_value: '',
  dict_type: '',
  description: '',
  sort_order: 0
})

// 搜索参数
const searchParams = reactive({
  statusFilter: '',
  typeFilter: '',
  searchKeyword: '',
  pageSize: 10
})

// 表单验证规则
const rules = {
  dict_name: [
    { required: true, message: '请输入字典名称', trigger: 'blur' }
  ],
  dict_key: [
    { required: true, message: '请输入字典键', trigger: 'blur' }
  ],
  dict_value: [
    { required: true, message: '请输入字典值', trigger: 'blur' }
  ],
  dict_type: [
    { required: true, message: '请输入字典类型', trigger: 'blur' }
  ]
}

// 获取字典列表
async function getDicts() {
  isLoading.value = true
  try {
    const response = await axios.get('/api/v1/dicts', {
      params: {
        page: currentPageNum.value,
        page_size: searchParams.pageSize,
        status: searchParams.statusFilter || undefined,
        dict_type: searchParams.typeFilter || undefined,
        keyword: searchParams.searchKeyword || undefined
      }
    })
    dicts.value = response.data.items
    total.value = response.data.total
  } catch (error: any) {
    ElMessage.error('获取字典列表失败: ' + (error.response?.data?.detail || error.message))
    dicts.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

// 获取字典类型列表
async function getDictTypes() {
  try {
    const response = await axios.get('/api/v1/dicts/type/list')
    dictTypes.value = response.data
  } catch (error: any) {
    console.error('获取字典类型失败:', error)
    dictTypes.value = []
  }
}

// 查询
function handleSearch() {
  currentPageNum.value = 1
  getDicts()
}

// 重置
function refreshList() {
  searchParams.statusFilter = ''
  searchParams.typeFilter = ''
  searchParams.searchKeyword = ''
  currentPageNum.value = 1
  getDicts()
}

// 新增字典
function handleAddDict() {
  dialogTitle.value = '新增字典'
  resetForm()
  dialogVisible.value = true
}

// 编辑字典
function handleEditDict(dictItem: any) {
  dialogTitle.value = '编辑字典'
  formData.id = dictItem.id
  formData.dict_name = dictItem.dict_name
  formData.dict_key = dictItem.dict_key
  formData.dict_value = dictItem.dict_value
  formData.dict_type = dictItem.dict_type
  formData.description = dictItem.description || ''
  formData.sort_order = dictItem.sort_order || 0

  dialogVisible.value = true
}

// 切换字典状态
async function toggleDictStatus(id: number, isActive: boolean) {
  try {
    await axios.put(`/api/v1/dicts/${id}`, {
      status: isActive ? 'active' : 'inactive'
    })
    ElMessage.success(`字典${isActive ? '激活' : '停用'}成功`)
  } catch (error: any) {
    ElMessage.error(`字典${isActive ? '激活' : '停用'}失败: ` + (error.response?.data?.detail || error.message))
    // 失败时恢复原状态
    const dict = dicts.value.find(d => d.id === id)
    if (dict) {
      dict.status = isActive ? 'inactive' : 'active'
    }
  }
}

// 删除字典
async function handleDeleteDict(id: number, name: string) {
  try {
    await axios.delete(`/api/v1/dicts/${id}`)
    ElMessage.success(`字典 ${name} 删除成功`)
    getDicts()
  } catch (error: any) {
    ElMessage.error(`字典删除失败: ` + (error.response?.data?.detail || error.message))
  }
}

// 表单提交
async function handleFormSubmit() {
  if (!dictFormRef.value) return
  
  try {
    await dictFormRef.value.validate()
    
    if (formData.id) {
      // 更新字典
      // 移除id字段，后端不需要
      const updateData = { ...formData }
      delete updateData.id
      await axios.put(`/api/v1/dicts/${formData.id}`, updateData)
      ElMessage.success('字典更新成功')
    } else {
      // 创建字典
      await axios.post('/api/v1/dicts', formData)
      ElMessage.success('字典添加成功')
    }
    
    dialogVisible.value = false
    getDicts()
    getDictTypes() // 刷新字典类型列表
  } catch (error: any) {
    if (error.name === 'Error') {
      ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// 关闭弹窗
function handleDialogClose() {
  dialogVisible.value = false
  resetForm()
  if (dictFormRef.value) {
    dictFormRef.value.resetFields()
  }
}

// 重置表单
function resetForm() {
  formData.id = ''
  formData.dict_name = ''
  formData.dict_key = ''
  formData.dict_value = ''
  formData.dict_type = ''
  formData.description = ''
  formData.sort_order = 0
}

// 分页相关
function handleSizeChange(size: number) {
  searchParams.pageSize = size
  getDicts()
}

function handleCurrentChange(current: number) {
  currentPageNum.value = current
  getDicts()
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
  getDicts()
  getDictTypes()
})
</script>

<style scoped>
.dict-management-container {
  padding: 20px;
  background-color: #ffffff;
  width: 100%;
  box-sizing: border-box;
  min-height: calc(100vh - 40px);
}

.dict-list-page {
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

.left-filters {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.right-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table-container {
  margin-bottom: 16px;
}

.dict-table {
  width: 100%;
  background-color: #fff;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 0;
}

.dict-form {
  padding: 0 10px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .dict-management-container {
    padding: 10px;
  }
  
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .left-filters,
  .right-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .filter-select,
  .right-actions .el-input {
    width: 100%;
  }
  
  .right-actions {
    flex-direction: column;
  }
  
  .pagination-container {
    justify-content: center;
  }
}

@media (max-width: 1200px) {
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .left-filters,
  .right-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>