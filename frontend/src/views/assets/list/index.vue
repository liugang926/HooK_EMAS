<template>
  <div class="asset-list-container">
    <!-- 搜索筛选区 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="资产编号">
          <el-input v-model="filterForm.asset_code" placeholder="请输入资产编号" clearable />
        </el-form-item>
        <el-form-item label="资产名称">
          <el-input v-model="filterForm.name" placeholder="请输入资产名称" clearable />
        </el-form-item>
        <el-form-item label="资产分类">
          <CategorySelect v-model="filterForm.categoryPath" @change="handleFilterCategoryChange" />
        </el-form-item>
        <el-form-item label="资产状态">
          <el-select v-model="filterForm.status" placeholder="请选择状态" clearable style="width: 140px">
            <el-option label="使用中" value="in_use" />
            <el-option label="闲置" value="idle" />
            <el-option label="借用中" value="borrowed" />
            <el-option label="维修中" value="maintenance" />
            <el-option label="已处置" value="disposed" />
          </el-select>
        </el-form-item>
        <el-form-item label="使用部门">
          <DepartmentSelect v-model="filterForm.using_department" style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 操作按钮区 -->
    <el-card class="action-card">
      <div class="action-bar">
        <div class="left-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增资产
          </el-button>
          <el-button @click="handleImport"><el-icon><Upload /></el-icon>批量导入</el-button>
          <el-button @click="handleExport" :loading="exporting"><el-icon><Download /></el-icon>{{ exporting ? '导出中...' : '导出' }}</el-button>
          <el-dropdown @command="handleBatchAction" :disabled="selectedAssets.length === 0">
            <el-button :disabled="selectedAssets.length === 0">
              批量操作
              <el-badge v-if="selectedAssets.length > 0" :value="selectedAssets.length" class="batch-badge" />
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="receive">
                  <el-icon><User /></el-icon>批量领用
                </el-dropdown-item>
                <el-dropdown-item command="return">
                  <el-icon><Refresh /></el-icon>批量退还
                </el-dropdown-item>
                <el-dropdown-item command="transfer">
                  <el-icon><ArrowDown /></el-icon>批量调拨
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <span style="color: #f56c6c;">批量删除</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="right-actions">
          <!-- 列设置 -->
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
          <el-button-group>
            <el-button :type="viewMode === 'table' ? 'primary' : 'default'" @click="viewMode = 'table'">
              <el-icon><List /></el-icon>
            </el-button>
            <el-button :type="viewMode === 'card' ? 'primary' : 'default'" @click="viewMode = 'card'">
              <el-icon><Grid /></el-icon>
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-card>
    
    <!-- 资产列表 -->
    <el-card class="list-card" v-loading="loading">
      <!-- 表格视图 -->
      <el-table v-if="viewMode === 'table'" :data="assetList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column v-if="isColumnVisible('image')" label="资产图片" width="80">
          <template #default="{ row }">
            <el-image :src="row.image || defaultImage" fit="cover" class="asset-image" />
          </template>
        </el-table-column>
        <el-table-column v-if="isColumnVisible('asset_code')" prop="asset_code" label="资产编号" width="150" sortable />
        <el-table-column v-if="isColumnVisible('name')" prop="name" label="资产名称" min-width="150" />
        <el-table-column v-if="isColumnVisible('category_name')" prop="category_name" label="资产分类" width="120" />
        <el-table-column v-if="isColumnVisible('brand')" prop="brand" label="品牌" width="100" />
        <el-table-column v-if="isColumnVisible('model')" prop="model" label="型号" width="120" />
        <el-table-column v-if="isColumnVisible('status')" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="isColumnVisible('using_user_name')" prop="using_user_name" label="使用人" width="100" />
        <el-table-column v-if="isColumnVisible('using_department_name')" prop="using_department_name" label="使用部门" width="120" />
        <el-table-column v-if="isColumnVisible('location_name')" prop="location_name" label="存放位置" width="120" />
        <el-table-column v-if="isColumnVisible('original_value')" label="原值(元)" width="120" align="right">
          <template #default="{ row }">{{ formatMoney(row.original_value) }}</template>
        </el-table-column>
        <el-table-column v-if="isColumnVisible('purchase_date')" prop="purchase_date" label="购置日期" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-dropdown trigger="click">
              <el-button type="primary" link>更多<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleReceive(row)">领用</el-dropdown-item>
                  <el-dropdown-item @click="handleBorrow(row)">借用</el-dropdown-item>
                  <el-dropdown-item @click="handleTransfer(row)">调拨</el-dropdown-item>
                  <el-dropdown-item @click="handleMaintenance(row)">维保</el-dropdown-item>
                  <el-dropdown-item divided @click="handleDelete(row)">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 卡片视图 -->
      <div v-else class="card-view">
        <el-row :gutter="20">
          <el-col v-for="asset in assetList" :key="asset.id" :xs="24" :sm="12" :md="8" :lg="6">
            <div class="asset-card" @click="handleView(asset)">
              <div class="card-image">
                <el-image :src="asset.image || defaultImage" fit="cover" />
                <el-tag :type="getStatusType(asset.status)" class="status-tag">
                  {{ getStatusLabel(asset.status) }}
                </el-tag>
              </div>
              <div class="card-content">
                <h3 class="asset-name">{{ asset.name }}</h3>
                <p class="asset-code">{{ asset.asset_code }}</p>
                <div class="asset-info">
                  <span>{{ asset.category_name }}</span>
                  <span v-if="asset.brand">{{ asset.brand }}</span>
                </div>
                <div class="asset-user">
                  <el-icon><User /></el-icon>
                  {{ asset.using_user_name || '未分配' }}
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
    
    <!-- 资产详情弹窗 -->
    <AssetDetail v-model="detailVisible" :asset="currentAsset" @edit="handleEdit" />
    
    <!-- 资产表单弹窗 -->
    <AssetForm v-model="formVisible" :asset="editingAsset" @success="handleFormSuccess" />
    
    <!-- 批量导入弹窗 -->
    <ImportDialog v-model="importDialogVisible" @success="handleImportSuccess" />
    
    <!-- 批量操作弹窗 -->
    <BatchOperationDialog 
      v-model="batchOperationVisible" 
      :operation-type="batchOperationType"
      :selected-assets="selectedAssets"
      @success="handleBatchOperationSuccess" 
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Upload, Download, ArrowDown, List, Grid, User, Setting } from '@element-plus/icons-vue'
import { CategorySelect, DepartmentSelect } from '@/components/common'
import AssetDetail from './components/AssetDetail.vue'
import AssetForm from './components/AssetForm.vue'
import ImportDialog from './components/ImportDialog.vue'
import BatchOperationDialog from './components/BatchOperationDialog.vue'
import { getAssets, deleteAsset, exportAssets, batchDeleteAssets } from '@/api/assets'

const router = useRouter()

// 状态
const loading = ref(false)
const viewMode = ref('table')
const selectedAssets = ref([])
const detailVisible = ref(false)
const formVisible = ref(false)
const currentAsset = ref(null)
const editingAsset = ref(null)

// 批量操作状态
const importDialogVisible = ref(false)
const batchOperationVisible = ref(false)
const batchOperationType = ref('receive') // 'receive', 'return', 'transfer'
const exporting = ref(false)

// 列配置
const allColumns = [
  { prop: 'image', label: '资产图片' },
  { prop: 'asset_code', label: '资产编号' },
  { prop: 'name', label: '资产名称' },
  { prop: 'category_name', label: '资产分类' },
  { prop: 'brand', label: '品牌' },
  { prop: 'model', label: '型号' },
  { prop: 'status', label: '状态' },
  { prop: 'using_user_name', label: '使用人' },
  { prop: 'using_department_name', label: '使用部门' },
  { prop: 'location_name', label: '存放位置' },
  { prop: 'original_value', label: '原值(元)' },
  { prop: 'purchase_date', label: '购置日期' }
]
const defaultVisibleColumns = ['image', 'asset_code', 'name', 'category_name', 'brand', 'model', 'status', 'using_user_name', 'using_department_name', 'location_name', 'original_value']
const visibleColumns = ref([...defaultVisibleColumns])

function isColumnVisible(prop) {
  return visibleColumns.value.includes(prop)
}

function resetColumns() {
  visibleColumns.value = [...defaultVisibleColumns]
}

// 监听列配置变化，保存到本地存储
watch(visibleColumns, (val) => {
  localStorage.setItem('asset_list_columns', JSON.stringify(val))
}, { deep: true })

// 默认图片
const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCBmaWxsPSIjZjNmNGY2IiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzlhOWE5YSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuaXoOWbvueJhzwvdGV4dD48L3N2Zz4='

// 筛选表单
const filterForm = reactive({
  asset_code: '',
  name: '',
  category: null,
  categoryPath: [],
  status: '',
  using_department: null
})

// 分页
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

// 资产列表
const assetList = ref([])

// 状态映射
const statusMap = {
  idle: { label: '闲置', type: 'warning' },
  in_use: { label: '使用中', type: 'success' },
  borrowed: { label: '借用中', type: 'primary' },
  maintenance: { label: '维修中', type: 'danger' },
  disposed: { label: '已处置', type: 'info' }
}

function getStatusType(status) { return statusMap[status]?.type || 'info' }
function getStatusLabel(status) { return statusMap[status]?.label || status }
function formatMoney(value) { return value?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) || '0.00' }

// 加载资产列表
async function loadAssets() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: filterForm.name || filterForm.asset_code || undefined,
      category: filterForm.category || undefined,
      status: filterForm.status || undefined,
      using_department: filterForm.using_department || undefined
    }
    const res = await getAssets(params)
    assetList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('加载资产列表失败:', error)
    ElMessage.error('加载资产列表失败')
  } finally {
    loading.value = false
  }
}

function handleFilterCategoryChange(path, lastId) { filterForm.category = lastId }

function handleSearch() {
  pagination.current = 1
  loadAssets()
}

function handleReset() {
  Object.assign(filterForm, { asset_code: '', name: '', category: null, categoryPath: [], status: '', using_department: null })
  handleSearch()
}

function handleAdd() {
  editingAsset.value = null
  formVisible.value = true
}

function handleView(row) {
  currentAsset.value = row
  detailVisible.value = true
}

function handleEdit(row) {
  editingAsset.value = row
  formVisible.value = true
}

function handleFormSuccess() {
  loadAssets()
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除资产 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteAsset(row.id)
      ElMessage.success('删除成功')
      loadAssets()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

function handleSelectionChange(selection) { selectedAssets.value = selection }
function handlePageChange(page) { pagination.current = page; loadAssets() }
function handleSizeChange(size) { pagination.pageSize = size; pagination.current = 1; loadAssets() }

// 批量导入
function handleImport() { 
  importDialogVisible.value = true 
}

// 处理导入成功
function handleImportSuccess() {
  loadAssets()
}

// 导出资产
async function handleExport() { 
  exporting.value = true
  try {
    // 如果有选中的资产，只导出选中的；否则导出全部（或按当前筛选条件）
    const params = {}
    if (selectedAssets.value.length > 0) {
      params.ids = selectedAssets.value.map(a => a.id)
    } else {
      // 使用当前筛选条件
      params.filters = {
        search: filterForm.name || filterForm.asset_code || undefined,
        category: filterForm.category || undefined,
        status: filterForm.status || undefined,
        using_department: filterForm.using_department || undefined
      }
    }
    
    const response = await exportAssets(params)
    
    // 创建下载链接
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
    link.download = `assets_export_${timestamp}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    const exportCount = selectedAssets.value.length > 0 ? selectedAssets.value.length : '全部'
    ElMessage.success(`成功导出 ${exportCount} 条资产数据`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 批量操作
function handleBatchAction(command) { 
  if (command === 'delete') {
    handleBatchDelete()
    return
  }
  
  // 检查是否选中了资产
  if (selectedAssets.value.length === 0) {
    ElMessage.warning('请先选择要操作的资产')
    return
  }
  
  // 验证资产状态
  if (command === 'receive') {
    const invalidAssets = selectedAssets.value.filter(a => a.status !== 'idle')
    if (invalidAssets.length > 0) {
      ElMessage.warning(`有 ${invalidAssets.length} 项资产状态不是"闲置"，无法领用`)
      return
    }
    batchOperationType.value = 'receive'
  } else if (command === 'return') {
    const invalidAssets = selectedAssets.value.filter(a => !['in_use', 'borrowed'].includes(a.status))
    if (invalidAssets.length > 0) {
      ElMessage.warning(`有 ${invalidAssets.length} 项资产状态不允许退还`)
      return
    }
    batchOperationType.value = 'return'
  } else if (command === 'transfer') {
    batchOperationType.value = 'transfer'
  }
  
  batchOperationVisible.value = true
}

// 批量删除
async function handleBatchDelete() {
  if (selectedAssets.value.length === 0) {
    ElMessage.warning('请先选择要删除的资产')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedAssets.value.length} 项资产吗？删除后可在回收站中恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const result = await batchDeleteAssets(selectedAssets.value.map(a => a.id))
    
    if (result.success) {
      ElMessage.success(result.message || '删除成功')
      selectedAssets.value = []
      loadAssets()
    } else {
      ElMessage.error(result.message || '删除失败')
      if (result.invalid_assets?.length > 0) {
        ElMessageBox.alert(
          `<div style="max-height: 300px; overflow: auto;">
            <ul style="margin: 0; padding-left: 20px;">
              ${result.invalid_assets.map(a => `<li>${a}</li>`).join('')}
            </ul>
          </div>`,
          '以下资产无法删除',
          {
            dangerouslyUseHTMLString: true,
            confirmButtonText: '知道了'
          }
        )
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量操作成功
function handleBatchOperationSuccess() {
  selectedAssets.value = []
  loadAssets()
}
function handleReceive(row) { router.push({ path: '/assets/receive', query: { id: row.id } }) }
function handleBorrow(row) { router.push({ path: '/assets/borrow', query: { id: row.id } }) }
function handleTransfer(row) { router.push({ path: '/assets/transfer', query: { id: row.id } }) }
function handleMaintenance(row) { router.push({ path: '/assets/maintenance', query: { id: row.id } }) }

onMounted(() => {
  loadAssets()
  // 从本地存储恢复列配置
  const savedColumns = localStorage.getItem('asset_list_columns')
  if (savedColumns) {
    try {
      visibleColumns.value = JSON.parse(savedColumns)
    } catch (e) {
      // ignore
    }
  }
})
</script>

<style lang="scss" scoped>
.asset-list-container {
  .filter-card, .action-card, .list-card { border-radius: 16px; margin-bottom: 16px; }
  
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .left-actions { display: flex; gap: 12px; align-items: center; }
    .right-actions { display: flex; gap: 12px; align-items: center; }
  }
  
  .batch-badge {
    margin-left: 4px;
    :deep(.el-badge__content) {
      font-size: 10px;
      height: 16px;
      line-height: 16px;
      padding: 0 5px;
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
  
  .asset-image { width: 50px; height: 50px; border-radius: 8px; }
  
  .card-view {
    .asset-card {
      border-radius: 12px;
      overflow: hidden;
      background: #fff;
      border: 1px solid #e5e7eb;
      margin-bottom: 16px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); transform: translateY(-2px); }
      
      .card-image {
        position: relative;
        height: 160px;
        background: #f9fafb;
        :deep(.el-image) { width: 100%; height: 100%; }
        .status-tag { position: absolute; top: 8px; right: 8px; }
      }
      
      .card-content {
        padding: 16px;
        .asset-name { font-size: 16px; font-weight: 600; color: #1f2937; margin: 0 0 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .asset-code { font-size: 12px; color: #9ca3af; margin: 0 0 8px; }
        .asset-info { display: flex; gap: 8px; margin-bottom: 8px; span { font-size: 12px; color: #6b7280; background: #f3f4f6; padding: 2px 8px; border-radius: 4px; } }
        .asset-user { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #4b5563; }
      }
    }
  }
  
  .pagination-container { display: flex; justify-content: flex-end; margin-top: 20px; }
}
</style>
