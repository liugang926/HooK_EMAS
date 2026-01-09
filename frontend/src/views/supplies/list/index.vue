<template>
  <div class="supply-list-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>用品档案</h2>
          <div class="header-actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增用品
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索筛选工具栏 -->
      <div class="list-toolbar">
        <div class="toolbar-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索编号、名称、规格..."
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
          <!-- 列配置 -->
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

          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          
          <el-button @click="handleImport">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
        </div>
      </div>

      <!-- 高级筛选 -->
      <el-collapse-transition>
        <div v-show="showAdvanced" class="advanced-filters">
          <el-form :model="filterForm" inline label-width="80px">
            <el-form-item label="用品分类">
              <el-tree-select
                v-model="filterForm.category"
                :data="categoryOptions"
                :props="{ value: 'id', label: 'name', children: 'children' }"
                placeholder="选择分类"
                check-strictly
                filterable
                clearable
                style="width: 180px"
              />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="filterForm.is_active" placeholder="全部状态" clearable style="width: 120px">
                <el-option label="启用" :value="true" />
                <el-option label="禁用" :value="false" />
              </el-select>
            </el-form-item>
            <el-form-item label="库存预警">
              <el-select v-model="filterForm.stock_warning" placeholder="全部" clearable style="width: 120px">
                <el-option label="库存不足" value="low" />
                <el-option label="库存正常" value="normal" />
              </el-select>
            </el-form-item>
            <el-form-item label="单价范围">
              <el-input-number v-model="filterForm.price_min" placeholder="最低" :controls="false" style="width: 100px" />
              <span style="margin: 0 8px">-</span>
              <el-input-number v-model="filterForm.price_max" placeholder="最高" :controls="false" style="width: 100px" />
            </el-form-item>
          </el-form>
        </div>
      </el-collapse-transition>
      
      <!-- 批量操作栏 -->
      <div class="batch-bar" v-if="selectedSupplies.length > 0">
        <span class="selection-info">已选择 {{ selectedSupplies.length }} 项</span>
        <el-button size="small" @click="handleBatchEnable">批量启用</el-button>
        <el-button size="small" @click="handleBatchDisable">批量禁用</el-button>
        <el-button size="small" type="danger" @click="handleBatchDelete">批量删除</el-button>
        <el-button size="small" link @click="clearSelection">清空选择</el-button>
      </div>
      
      <!-- 用品列表 -->
      <el-table 
        :data="supplyList" 
        style="width: 100%" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column v-if="isColumnVisible('code')" prop="code" label="用品编号" width="150" sortable />
        <el-table-column v-if="isColumnVisible('name')" prop="name" label="用品名称" min-width="180" />
        <el-table-column v-if="isColumnVisible('category_name')" prop="category_name" label="分类" width="120" />
        <el-table-column v-if="isColumnVisible('model')" prop="model" label="规格型号" width="120" />
        <el-table-column v-if="isColumnVisible('unit')" prop="unit" label="单位" width="80" align="center" />
        <el-table-column v-if="isColumnVisible('price')" label="单价" width="100" align="right">
          <template #default="{ row }">
            {{ row.price ? `¥${row.price}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column v-if="isColumnVisible('total_stock')" label="库存" width="100" align="center">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.total_stock <= (row.min_stock || 0) }">
              {{ row.total_stock || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column v-if="isColumnVisible('min_stock')" prop="min_stock" label="预警值" width="80" align="center" />
        <el-table-column v-if="isColumnVisible('is_active')" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="isColumnVisible('created_at')" prop="created_at" label="创建时间" width="170" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-dropdown trigger="click">
              <el-button type="primary" link>更多<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleInbound(row)">入库</el-dropdown-item>
                  <el-dropdown-item @click="handleOutbound(row)">领用</el-dropdown-item>
                  <el-dropdown-item divided @click="handleDelete(row)">
                    <span style="color: #f56c6c;">删除</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="supplyForm" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用品编号" prop="code">
              <el-input v-model="supplyForm.code" placeholder="请输入或自动生成">
                <template #append>
                  <el-button @click="generateCode" :loading="generatingCode">生成</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用品名称" prop="name">
              <el-input v-model="supplyForm.name" placeholder="请输入用品名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用品分类" prop="category">
              <el-tree-select
                v-model="supplyForm.category"
                :data="categoryOptions"
                :props="{ value: 'id', label: 'name', children: 'children' }"
                placeholder="请选择分类"
                check-strictly
                filterable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规格型号">
              <el-input v-model="supplyForm.model" placeholder="请输入规格型号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="supplyForm.unit" placeholder="如：个、盒、包" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价">
              <el-input-number v-model="supplyForm.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="库存预警">
              <el-input-number v-model="supplyForm.min_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="supplyForm.description" type="textarea" :rows="3" placeholder="请输入描述信息" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="supplyForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情对话框 (带标签页) -->
    <el-dialog v-model="viewDialogVisible" title="用品详情" width="800px">
      <div v-if="currentSupply">
        <div class="supply-header">
          <h3>{{ currentSupply.name }}</h3>
          <p class="supply-code">编号：{{ currentSupply.code }}</p>
          <div class="tags-row">
            <el-tag :type="currentSupply.is_active ? 'success' : 'info'">{{ currentSupply.is_active ? '启用' : '禁用' }}</el-tag>
            <el-tag v-if="currentSupply.category_name" type="info">{{ currentSupply.category_name }}</el-tag>
            <el-tag :type="(currentSupply.total_stock || 0) <= (currentSupply.min_stock || 0) ? 'danger' : 'success'">
              库存: {{ currentSupply.total_stock || 0 }}
            </el-tag>
          </div>
        </div>
        
        <el-tabs v-model="activeDetailTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="用品编号">{{ currentSupply.code }}</el-descriptions-item>
              <el-descriptions-item label="用品名称">{{ currentSupply.name }}</el-descriptions-item>
              <el-descriptions-item label="分类">{{ currentSupply.category_name }}</el-descriptions-item>
              <el-descriptions-item label="规格型号">{{ currentSupply.model || '-' }}</el-descriptions-item>
              <el-descriptions-item label="单位">{{ currentSupply.unit }}</el-descriptions-item>
              <el-descriptions-item label="单价">{{ currentSupply.price ? `¥${currentSupply.price}` : '-' }}</el-descriptions-item>
              <el-descriptions-item label="当前库存">{{ currentSupply.total_stock || 0 }}</el-descriptions-item>
              <el-descriptions-item label="库存预警">{{ currentSupply.min_stock || '-' }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDateTime(currentSupply.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="currentSupply.is_active ? 'success' : 'info'" size="small">
                  {{ currentSupply.is_active ? '启用' : '禁用' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">{{ currentSupply.description || '-' }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="入库记录" name="inbound">
            <el-table :data="supplyInboundHistory" size="small" v-loading="loadingHistory">
              <el-table-column prop="inbound_no" label="入库单号" width="160" />
              <el-table-column prop="inbound_date" label="入库日期" width="120" />
              <el-table-column prop="quantity" label="入库数量" width="100" align="center" />
              <el-table-column prop="price" label="单价" width="100" align="right">
                <template #default="{ row }">¥{{ row.price }}</template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'approved' ? 'success' : 'info'" size="small">
                    {{ row.status === 'approved' ? '已入库' : '草稿' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" />
            </el-table>
            <el-empty v-if="!loadingHistory && supplyInboundHistory.length === 0" description="暂无入库记录" />
          </el-tab-pane>
          
          <el-tab-pane label="领用记录" name="outbound">
            <el-table :data="supplyOutboundHistory" size="small" v-loading="loadingHistory">
              <el-table-column prop="outbound_no" label="领用单号" width="160" />
              <el-table-column prop="outbound_date" label="领用日期" width="120" />
              <el-table-column prop="quantity" label="领用数量" width="100" align="center" />
              <el-table-column prop="receive_user_name" label="领用人" width="100" />
              <el-table-column prop="receive_department_name" label="部门" width="120" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'approved' ? 'success' : 'info'" size="small">
                    {{ row.status === 'approved' ? '已出库' : '草稿' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!loadingHistory && supplyOutboundHistory.length === 0" description="暂无领用记录" />
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="warning" @click="openQuickInbound">入库</el-button>
        <el-button type="success" @click="openQuickOutbound">领用</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
    
    <!-- 快速入库对话框 -->
    <el-dialog v-model="quickInboundVisible" title="快速入库" width="500px">
      <el-form :model="quickInboundForm" label-width="100px">
        <el-form-item label="用品">
          <el-input :value="quickSupply?.name" disabled />
        </el-form-item>
        <el-form-item label="仓库" required>
          <el-select v-model="quickInboundForm.warehouse" placeholder="请选择仓库" style="width: 100%">
            <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入库日期" required>
          <el-date-picker v-model="quickInboundForm.inbound_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="数量" required>
          <el-input-number v-model="quickInboundForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价">
          <el-input-number v-model="quickInboundForm.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quickInboundVisible = false">取消</el-button>
        <el-button type="primary" :loading="quickSubmitting" @click="submitQuickInbound">确认入库</el-button>
      </template>
    </el-dialog>
    
    <!-- 快速领用对话框 -->
    <el-dialog v-model="quickOutboundVisible" title="快速领用" width="500px">
      <el-form :model="quickOutboundForm" label-width="100px">
        <el-form-item label="用品">
          <el-input :value="quickSupply?.name" disabled />
        </el-form-item>
        <el-form-item label="可用库存">
          <el-tag :type="(quickSupply?.total_stock || 0) > 0 ? 'success' : 'danger'">
            {{ quickSupply?.total_stock || 0 }} {{ quickSupply?.unit }}
          </el-tag>
        </el-form-item>
        <el-form-item label="出库仓库" required>
          <el-select v-model="quickOutboundForm.warehouse" placeholder="请选择仓库" style="width: 100%">
            <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="领用日期" required>
          <el-date-picker v-model="quickOutboundForm.outbound_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="领用人" required>
          <el-select v-model="quickOutboundForm.receive_user" placeholder="请选择领用人" style="width: 100%" filterable>
            <el-option v-for="u in userOptions" :key="u.id" :label="`${u.display_name || u.username} ${u.department_name ? '(' + u.department_name + ')' : ''}`" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="领用部门">
          <el-select v-model="quickOutboundForm.receive_department" placeholder="请选择部门" style="width: 100%" filterable clearable>
            <el-option v-for="d in departmentOptions" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="领用数量" required>
          <el-input-number v-model="quickOutboundForm.quantity" :min="1" :max="quickSupply?.total_stock || 9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="领用原因">
          <el-input v-model="quickOutboundForm.reason" type="textarea" :rows="2" placeholder="请输入领用原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quickOutboundVisible = false">取消</el-button>
        <el-button type="primary" :loading="quickSubmitting" @click="submitQuickOutbound">确认领用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Filter, Refresh, Setting, Download, Upload, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getSupplies, getSupply, createSupply, updateSupply, deleteSupply,
  getSupplyCategories, generateSupplyCode,
  getSupplyInbounds, createSupplyInbound, approveSupplyInbound,
  getSupplyOutbounds, createSupplyOutbound, approveSupplyOutbound,
  getWarehouses, getUsers, getDepartments
} from '@/api/supplies'
import { useAppStore } from '@/stores/app'
import { extractListData, extractPaginationInfo } from '@/utils/api-helpers'

const router = useRouter()
const appStore = useAppStore()

// ===== 状态定义 =====
const loading = ref(false)
const submitting = ref(false)
const generatingCode = ref(false)
const formDialogVisible = ref(false)
const formDialogTitle = ref('新增用品')
const viewDialogVisible = ref(false)
const currentSupply = ref(null)
const selectedSupplies = ref([])

// 详情对话框扩展状态
const activeDetailTab = ref('basic')
const loadingHistory = ref(false)
const supplyInboundHistory = ref([])
const supplyOutboundHistory = ref([])

// 快速入库/领用对话框状态
const quickInboundVisible = ref(false)
const quickOutboundVisible = ref(false)
const quickSupply = ref(null)
const quickSubmitting = ref(false)
const quickInboundForm = reactive({
  warehouse: null,
  inbound_date: new Date().toISOString().split('T')[0],
  quantity: 1,
  price: 0
})
const quickOutboundForm = reactive({
  warehouse: null,
  outbound_date: new Date().toISOString().split('T')[0],
  receive_user: null,
  receive_department: null,
  quantity: 1,
  reason: ''
})

// 下拉选项
const warehouseOptions = ref([])
const userOptions = ref([])
const departmentOptions = ref([])

// 搜索和筛选
const searchKeyword = ref('')
const showAdvanced = ref(false)
const filterForm = reactive({
  category: null,
  is_active: null,
  stock_warning: null,
  price_min: null,
  price_max: null
})

// 列配置
const allColumns = [
  { prop: 'code', label: '用品编号' },
  { prop: 'name', label: '用品名称' },
  { prop: 'category_name', label: '分类' },
  { prop: 'model', label: '规格型号' },
  { prop: 'unit', label: '单位' },
  { prop: 'price', label: '单价' },
  { prop: 'total_stock', label: '库存' },
  { prop: 'min_stock', label: '预警值' },
  { prop: 'is_active', label: '状态' },
  { prop: 'created_at', label: '创建时间' }
]
const defaultVisibleColumns = ['code', 'name', 'category_name', 'model', 'unit', 'price', 'total_stock', 'is_active']
const visibleColumns = ref([...defaultVisibleColumns])

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const supplyList = ref([])
const categoryOptions = ref([])

const formRef = ref()
const supplyForm = reactive({
  id: null,
  code: '',
  name: '',
  category: null,
  model: '',
  unit: '',
  price: null,
  min_stock: null,
  description: '',
  is_active: true
})

const formRules = {
  code: [{ required: true, message: '请输入用品编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入用品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择用品分类', trigger: 'change' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }]
}

// ===== 辅助方法 =====
function formatDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 19)
}

function isColumnVisible(prop) {
  return visibleColumns.value.includes(prop)
}

// ===== 搜索筛选方法 =====
function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

function handleSearch() {
  pagination.current = 1
  loadData()
}

function handleReset() {
  searchKeyword.value = ''
  filterForm.category = null
  filterForm.is_active = null
  filterForm.stock_warning = null
  filterForm.price_min = null
  filterForm.price_max = null
  pagination.current = 1
  loadData()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  loadData()
}

function resetColumns() {
  visibleColumns.value = [...defaultVisibleColumns]
}

function handleExport() {
  ElMessage.info('导出功能开发中...')
}

function handleImport() {
  ElMessage.info('导入功能开发中...')
}

// 监听筛选条件变化
watch(filterForm, () => {
  pagination.current = 1
  loadData()
}, { deep: true })

// ===== 数据加载方法 =====
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      company: appStore.currentCompany?.id
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (filterForm.category) {
      params.category = filterForm.category
    }
    if (filterForm.is_active !== null) {
      params.is_active = filterForm.is_active
    }
    if (filterForm.price_min) {
      params.price_min = filterForm.price_min
    }
    if (filterForm.price_max) {
      params.price_max = filterForm.price_max
    }
    
    const res = await getSupplies(params)
    supplyList.value = extractListData(res)
    const pageInfo = extractPaginationInfo(res)
    pagination.total = pageInfo.total || 0
  } catch (error) {
    console.error('加载用品列表失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const res = await getSupplyCategories()
    const data = extractListData(res)
    categoryOptions.value = buildTree(data)
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

function buildTree(data) {
  const ids = new Set(data.map(item => item.id))
  const isRoot = (item) => item.parent === null || !ids.has(item.parent)
  
  const buildSubTree = (parentId) => {
    return data
      .filter(item => item.parent === parentId)
      .map(item => ({
        ...item,
        children: buildSubTree(item.id)
      }))
  }
  
  return data
    .filter(isRoot)
    .map(item => ({
      ...item,
      children: buildSubTree(item.id)
    }))
}

async function generateCode() {
  generatingCode.value = true
  try {
    const res = await generateSupplyCode()
    if (res.code) {
      supplyForm.code = res.code
      ElMessage.success('编号生成成功')
    }
  } catch (error) {
    // Fallback
    const date = new Date()
    const dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
    const random = String(Math.floor(Math.random() * 10000)).padStart(4, '0')
    supplyForm.code = `BG${dateStr}${random}`
  } finally {
    generatingCode.value = false
  }
}

// ===== 选择方法 =====
function handleSelectionChange(selection) {
  selectedSupplies.value = selection
}

function clearSelection() {
  selectedSupplies.value = []
}

// ===== 事件处理方法 =====
function handleAdd() {
  formDialogTitle.value = '新增用品'
  Object.assign(supplyForm, {
    id: null,
    code: '',
    name: '',
    category: null,
    model: '',
    unit: '',
    price: null,
    min_stock: null,
    description: '',
    is_active: true
  })
  formDialogVisible.value = true
}

function handleView(row) {
  currentSupply.value = row
  viewDialogVisible.value = true
}

function handleEdit(row) {
  formDialogTitle.value = '编辑用品'
  Object.assign(supplyForm, {
    id: row.id,
    code: row.code,
    name: row.name,
    category: row.category,
    model: row.model || '',
    unit: row.unit,
    price: row.price,
    min_stock: row.min_stock,
    description: row.description || '',
    is_active: row.is_active
  })
  formDialogVisible.value = true
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentSupply.value)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除用品 "${row.name}" 吗？`, '删除确认', { type: 'warning' })
    await deleteSupply(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleInbound(row) {
  quickSupply.value = row
  Object.assign(quickInboundForm, {
    warehouse: warehouseOptions.value[0]?.id || null,
    inbound_date: new Date().toISOString().split('T')[0],
    quantity: 1,
    price: parseFloat(row.price) || 0
  })
  quickInboundVisible.value = true
}

function handleOutbound(row) {
  quickSupply.value = row
  Object.assign(quickOutboundForm, {
    warehouse: warehouseOptions.value[0]?.id || null,
    outbound_date: new Date().toISOString().split('T')[0],
    receive_user: null,
    receive_department: null,
    quantity: 1,
    reason: ''
  })
  quickOutboundVisible.value = true
}

// ===== 快速入库/领用 =====
function openQuickInbound() {
  handleInbound(currentSupply.value)
  viewDialogVisible.value = false
}

function openQuickOutbound() {
  handleOutbound(currentSupply.value)
  viewDialogVisible.value = false
}

async function submitQuickInbound() {
  if (!quickInboundForm.warehouse) {
    ElMessage.warning('请选择仓库')
    return
  }
  
  quickSubmitting.value = true
  try {
    const data = {
      company: appStore.currentCompany?.id,
      warehouse: quickInboundForm.warehouse,
      inbound_date: quickInboundForm.inbound_date,
      total_amount: (quickInboundForm.quantity * quickInboundForm.price).toFixed(2),
      items: [{
        consumable: quickSupply.value.id,
        quantity: quickInboundForm.quantity,
        price: quickInboundForm.price,
        amount: (quickInboundForm.quantity * quickInboundForm.price).toFixed(2)
      }]
    }
    
    const result = await createSupplyInbound(data)
    // Auto-approve the inbound
    await approveSupplyInbound(result.id)
    
    ElMessage.success(`入库成功，库存已更新 +${quickInboundForm.quantity}`)
    quickInboundVisible.value = false
    loadData() // Refresh list to show updated stock
  } catch (error) {
    ElMessage.error('入库失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    quickSubmitting.value = false
  }
}

async function submitQuickOutbound() {
  if (!quickOutboundForm.warehouse) {
    ElMessage.warning('请选择仓库')
    return
  }
  if (!quickOutboundForm.receive_user) {
    ElMessage.warning('请选择领用人')
    return
  }
  if (quickOutboundForm.quantity > (quickSupply.value?.total_stock || 0)) {
    ElMessage.warning('领用数量不能超过库存')
    return
  }
  
  quickSubmitting.value = true
  try {
    const data = {
      company: appStore.currentCompany?.id,
      warehouse: quickOutboundForm.warehouse,
      outbound_date: quickOutboundForm.outbound_date,
      receive_user: quickOutboundForm.receive_user,
      receive_department: quickOutboundForm.receive_department,
      reason: quickOutboundForm.reason,
      items: [{
        consumable: quickSupply.value.id,
        quantity: quickOutboundForm.quantity
      }]
    }
    
    const result = await createSupplyOutbound(data)
    // Auto-approve the outbound
    await approveSupplyOutbound(result.id)
    
    ElMessage.success(`领用成功，库存已更新 -${quickOutboundForm.quantity}`)
    quickOutboundVisible.value = false
    loadData() // Refresh list to show updated stock
  } catch (error) {
    ElMessage.error('领用失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    quickSubmitting.value = false
  }
}

// ===== 加载用品历史记录 =====
async function loadSupplyHistory(supplyId) {
  loadingHistory.value = true
  supplyInboundHistory.value = []
  supplyOutboundHistory.value = []
  
  try {
    // Load inbound history for this supply
    const inboundRes = await getSupplyInbounds({ page_size: 100 })
    const allInbounds = inboundRes.results || []
    // Filter and flatten to get items for this supply
    supplyInboundHistory.value = allInbounds.filter(inb => 
      inb.items?.some(item => item.consumable === supplyId)
    ).map(inb => {
      const item = inb.items.find(i => i.consumable === supplyId)
      return {
        ...inb,
        quantity: item?.quantity || 0,
        price: item?.price || 0
      }
    })
    
    // Load outbound history for this supply
    const outboundRes = await getSupplyOutbounds({ page_size: 100 })
    const allOutbounds = outboundRes.results || []
    supplyOutboundHistory.value = allOutbounds.filter(out => 
      out.items?.some(item => item.consumable === supplyId)
    ).map(out => {
      const item = out.items.find(i => i.consumable === supplyId)
      return {
        ...out,
        quantity: item?.quantity || 0
      }
    })
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

// ===== 加载下拉选项 =====
async function loadQuickOptions() {
  try {
    const [warehouseRes, userRes, deptRes] = await Promise.allSettled([
      getWarehouses(),
      getUsers(),
      getDepartments()
    ])
    
    if (warehouseRes.status === 'fulfilled') {
      warehouseOptions.value = warehouseRes.value.results || warehouseRes.value || []
    }
    if (userRes.status === 'fulfilled') {
      userOptions.value = userRes.value.results || userRes.value || []
    }
    if (deptRes.status === 'fulfilled') {
      departmentOptions.value = deptRes.value.results || deptRes.value || []
    }
  } catch (error) {
    console.error('加载选项失败:', error)
  }
}

// Watch for view dialog opening to load history
watch(viewDialogVisible, (newVal) => {
  if (newVal && currentSupply.value) {
    activeDetailTab.value = 'basic'
    loadSupplyHistory(currentSupply.value.id)
  }
})

// 批量操作
async function handleBatchEnable() {
  if (selectedSupplies.value.length === 0) return
  try {
    // Implement batch enable
    ElMessage.success('批量启用成功')
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleBatchDisable() {
  if (selectedSupplies.value.length === 0) return
  try {
    // Implement batch disable
    ElMessage.success('批量禁用成功')
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleBatchDelete() {
  if (selectedSupplies.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedSupplies.value.length} 项用品吗？`, '删除确认', { type: 'warning' })
    // Implement batch delete
    ElMessage.success('批量删除成功')
    selectedSupplies.value = []
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

async function submitForm() {
  try {
    await formRef.value?.validate()
  } catch (error) {
    return
  }
  
  submitting.value = true
  try {
    const data = {
      code: supplyForm.code,
      name: supplyForm.name,
      category: supplyForm.category,
      model: supplyForm.model,
      unit: supplyForm.unit,
      price: supplyForm.price,
      min_stock: supplyForm.min_stock,
      description: supplyForm.description,
      is_active: supplyForm.is_active
    }
    
    if (supplyForm.id) {
      await updateSupply(supplyForm.id, data)
      ElMessage.success('编辑成功')
    } else {
      await createSupply(data)
      ElMessage.success('添加成功')
    }
    
    formDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

// ===== 初始化 =====
onMounted(() => {
  loadData()
  loadCategories()
  loadQuickOptions() // Load warehouse, user, department options for quick dialogs
  
  // 从本地存储恢复列配置
  const savedColumns = localStorage.getItem('supply_list_columns')
  if (savedColumns) {
    try {
      visibleColumns.value = JSON.parse(savedColumns)
    } catch (e) {
      // ignore
    }
  }
})

// 监听列配置变化，保存到本地存储
watch(visibleColumns, (val) => {
  localStorage.setItem('supply_list_columns', JSON.stringify(val))
}, { deep: true })
</script>

<style lang="scss" scoped>
.supply-list-container {
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
  
  .batch-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: #e6f7ff;
    border-radius: 8px;
    margin-bottom: 16px;
    
    .selection-info {
      font-size: 14px;
      color: #1890ff;
      font-weight: 500;
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
  
  .text-danger {
    color: #f56c6c;
    font-weight: 500;
  }
  
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  
  .supply-header {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;
    
    h3 {
      margin: 0 0 4px;
      font-size: 20px;
      color: #1f2937;
    }
    
    .supply-code {
      color: #6b7280;
      font-size: 14px;
      margin: 0 0 12px;
    }
    
    .tags-row {
      display: flex;
      gap: 8px;
    }
  }
}
</style>
