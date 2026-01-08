<template>
  <div class="asset-maintenance-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>资产维保</h2>
          <el-button type="primary" @click="handleNewMaintenance">
            <el-icon><Plus /></el-icon>
            新建维保
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选工具栏 -->
      <div class="list-toolbar">
        <div class="toolbar-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索单号、资产名称..."
            clearable
            style="width: 280px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="toggleAdvanced">
            <el-icon><Filter /></el-icon>
            {{ showAdvanced ? '收起筛选' : '高级筛选' }}
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </div>
        <div class="toolbar-actions">
          <el-popover placement="bottom-end" :width="280" trigger="click">
            <template #reference>
              <el-button>
                <el-icon><Setting /></el-icon>
                列设置
              </el-button>
            </template>
            <div class="column-settings">
              <div class="column-settings-header">
                <span>显示列配置</span>
                <el-button type="primary" link size="small" @click="resetColumns">恢复默认</el-button>
              </div>
              <el-checkbox-group v-model="visibleColumns" class="column-list">
                <div v-for="col in allColumns" :key="col.prop" class="column-item">
                  <el-checkbox :value="col.prop">{{ col.label }}</el-checkbox>
                </div>
              </el-checkbox-group>
            </div>
          </el-popover>
        </div>
      </div>

      <!-- 高级筛选 -->
      <el-collapse-transition>
        <div v-show="showAdvanced" class="advanced-filters">
          <el-form :model="filterForm" inline label-width="80px">
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 140px">
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item label="维保类型">
              <el-select v-model="filterForm.maintenance_type" placeholder="全部类型" clearable style="width: 140px">
                <el-option label="维修" value="repair" />
                <el-option label="保养" value="maintenance" />
                <el-option label="检测" value="inspection" />
                <el-option label="升级" value="upgrade" />
              </el-select>
            </el-form-item>
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="filterForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 240px"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-collapse-transition>
      
      <el-table :data="maintenanceList" style="width: 100%" v-loading="loading">
        <el-table-column prop="maintenance_no" label="维保单号" width="150" />
        <el-table-column prop="asset_name" label="资产名称" min-width="150" />
        <el-table-column prop="maintenance_type_display" label="维保类型" width="100" />
        <el-table-column label="维保费用" width="120">
          <template #default="{ row }">
            ¥ {{ row.cost || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120">
          <template #default="{ row }">
            {{ row.end_date || '进行中' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button 
              v-if="row.status === 'in_progress'" 
              type="success" 
              link 
              @click="handleComplete(row)"
            >
              完成
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="loadMaintenanceList"
        />
      </div>
    </el-card>
    
    <!-- 新建维保对话框 -->
    <el-dialog v-model="maintenanceDialogVisible" title="新建维保" width="700px">
      <el-form ref="maintenanceFormRef" :model="maintenanceForm" :rules="maintenanceRules" label-width="100px">
        <el-form-item label="选择资产" prop="asset">
          <el-select
            v-model="maintenanceForm.asset"
            filterable
            remote
            :remote-method="searchAssets"
            :loading="searchingAssets"
            placeholder="请选择资产"
            style="width: 100%"
          >
            <el-option
              v-for="asset in availableAssets"
              :key="asset.id"
              :label="`${asset.name} (${asset.asset_code})`"
              :value="asset.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维保类型" prop="maintenance_type">
          <el-select v-model="maintenanceForm.maintenance_type" placeholder="请选择维保类型" style="width: 100%">
            <el-option label="保养" value="maintenance" />
            <el-option label="维修" value="repair" />
            <el-option label="检测" value="inspection" />
            <el-option label="升级" value="upgrade" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="维保费用">
          <el-input-number v-model="maintenanceForm.cost" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="维保供应商">
          <el-input v-model="maintenanceForm.vendor" placeholder="请输入维保供应商" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="maintenanceForm.start_date"
            type="date"
            placeholder="请选择开始日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预计结束">
          <el-date-picker
            v-model="maintenanceForm.expected_end_date"
            type="date"
            placeholder="请选择预计结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="维保说明">
          <el-input v-model="maintenanceForm.description" type="textarea" :rows="3" placeholder="请输入维保说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="maintenanceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitMaintenance">确认</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="维保详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item label="维保单号">{{ currentRecord.maintenance_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord.status)">{{ getStatusLabel(currentRecord.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="资产名称">{{ currentRecord.asset_name }}</el-descriptions-item>
        <el-descriptions-item label="维保类型">{{ currentRecord.maintenance_type_display }}</el-descriptions-item>
        <el-descriptions-item label="维保费用">¥ {{ currentRecord.cost || '0.00' }}</el-descriptions-item>
        <el-descriptions-item label="维保供应商">{{ currentRecord.vendor || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentRecord.start_date }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{ currentRecord.end_date || '进行中' }}</el-descriptions-item>
        <el-descriptions-item label="维保说明" :span="2">{{ currentRecord.description || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button 
          v-if="currentRecord && currentRecord.status === 'in_progress'" 
          type="success" 
          @click="handleCompleteFromDetail"
        >
          标记完成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { Plus, Search, Filter, Refresh, Setting } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const submitting = ref(false)
const maintenanceDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const currentRecord = ref(null)
const searchingAssets = ref(false)

// 搜索和筛选
const searchKeyword = ref('')
const showAdvanced = ref(false)
const filterForm = reactive({
  status: null,
  maintenance_type: null,
  dateRange: null
})

// 列配置
const allColumns = [
  { prop: 'maintenance_no', label: '维保单号' },
  { prop: 'asset_name', label: '资产名称' },
  { prop: 'maintenance_type_display', label: '维保类型' },
  { prop: 'cost', label: '维保费用' },
  { prop: 'start_date', label: '开始日期' },
  { prop: 'end_date', label: '结束日期' },
  { prop: 'status', label: '状态' }
]
const visibleColumns = ref(['maintenance_no', 'asset_name', 'maintenance_type_display', 'cost', 'start_date', 'end_date', 'status'])

function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

function handleSearch() {
  pagination.current = 1
  loadMaintenanceList()
}

function handleReset() {
  searchKeyword.value = ''
  filterForm.status = null
  filterForm.maintenance_type = null
  filterForm.dateRange = null
  pagination.current = 1
  loadMaintenanceList()
}

function resetColumns() {
  visibleColumns.value = ['maintenance_no', 'asset_name', 'maintenance_type_display', 'cost', 'start_date', 'end_date', 'status']
}

function isColumnVisible(prop) {
  return visibleColumns.value.includes(prop)
}

// 监听筛选条件变化
watch(filterForm, () => {
  pagination.current = 1
  loadMaintenanceList()
}, { deep: true })

const maintenanceFormRef = ref()

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const maintenanceList = ref([])
const availableAssets = ref([])

const maintenanceForm = reactive({
  asset: null,
  maintenance_type: '',
  cost: 0,
  vendor: '',
  start_date: new Date().toISOString().split('T')[0],
  expected_end_date: '',
  description: ''
})

const maintenanceRules = {
  asset: [{ required: true, message: '请选择资产', trigger: 'change' }],
  maintenance_type: [{ required: true, message: '请选择维保类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

// 状态映射
const statusMap = {
  pending: { label: '待处理', type: 'info' },
  in_progress: { label: '进行中', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
  cancelled: { label: '已取消', type: 'info' }
}

function getStatusType(status) {
  return statusMap[status]?.type || 'info'
}

function getStatusLabel(status) {
  return statusMap[status]?.label || status
}

// 加载维保记录
async function loadMaintenanceList() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    
    // 添加搜索条件
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.maintenance_type) {
      params.maintenance_type = filterForm.maintenance_type
    }
    if (filterForm.dateRange?.[0]) {
      params.start_date_after = filterForm.dateRange[0]
    }
    if (filterForm.dateRange?.[1]) {
      params.start_date_before = filterForm.dateRange[1]
    }
    
    const res = await request.get('/assets/maintenances/', { params })
    maintenanceList.value = res?.results || res || []
    pagination.total = res?.count || 0
  } catch (error) {
    console.error('加载维保记录失败:', error)
    ElMessage.error('加载维保记录失败')
  } finally {
    loading.value = false
  }
}

// 搜索资产
async function searchAssets(query) {
  searchingAssets.value = true
  try {
    const res = await request.get('/assets/list/', {
      params: {
        search: query,
        page_size: 50
      }
    })
    availableAssets.value = res?.results || res || []
  } catch (error) {
    console.error('搜索资产失败:', error)
  } finally {
    searchingAssets.value = false
  }
}

function handleNewMaintenance() {
  maintenanceForm.asset = null
  maintenanceForm.maintenance_type = ''
  maintenanceForm.cost = 0
  maintenanceForm.vendor = ''
  maintenanceForm.start_date = new Date().toISOString().split('T')[0]
  maintenanceForm.expected_end_date = ''
  maintenanceForm.description = ''
  searchAssets('') // 加载资产
  maintenanceDialogVisible.value = true
}

function handleView(row) {
  currentRecord.value = row
  viewDialogVisible.value = true
}

async function handleComplete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要将维保单 "${row.maintenance_no}" 标记为已完成吗？`,
      '完成确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
    
    await request.post(`/assets/maintenances/${row.id}/complete/`, {
      end_date: new Date().toISOString().split('T')[0]
    })
    
    ElMessage.success('维保已完成')
    loadMaintenanceList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('完成维保失败:', error)
      ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

function handleCompleteFromDetail() {
  viewDialogVisible.value = false
  handleComplete(currentRecord.value)
}

async function submitMaintenance() {
  try {
    await maintenanceFormRef.value?.validate()
  } catch (error) {
    return
  }
  
  submitting.value = true
  try {
    const data = {
      asset: maintenanceForm.asset,
      maintenance_type: maintenanceForm.maintenance_type,
      cost: maintenanceForm.cost,
      vendor: maintenanceForm.vendor,
      start_date: maintenanceForm.start_date,
      expected_end_date: maintenanceForm.expected_end_date || null,
      description: maintenanceForm.description
    }
    
    await request.post('/assets/maintenances/', data)
    ElMessage.success('维保记录创建成功')
    maintenanceDialogVisible.value = false
    loadMaintenanceList()
  } catch (error) {
    console.error('创建维保失败:', error)
    ElMessage.error('创建失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadMaintenanceList()
})
</script>

<style lang="scss" scoped>
.asset-maintenance-container {
  .list-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    
    .toolbar-search {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    
    .toolbar-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  
  .advanced-filters {
    padding: 16px;
    background: #fafafa;
    border-radius: 8px;
    margin-bottom: 16px;
    border: 1px dashed #e5e7eb;
    
    :deep(.el-form-item) {
      margin-bottom: 8px;
    }
  }
  
  .column-settings {
    .column-settings-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #e5e7eb;
      font-weight: 500;
    }
    
    .column-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      max-height: 300px;
      overflow-y: auto;
    }
    
    .column-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 8px;
      border-radius: 4px;
      
      &:hover {
        background: #f5f7fa;
      }
    }
  }
  
  .page-card {
    border-radius: 16px;
    
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        font-size: 18px;
        color: #1f2937;
      }
    }
  }
  
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
