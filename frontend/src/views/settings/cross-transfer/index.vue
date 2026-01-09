<template>
  <div class="cross-transfer-container">
    <div class="page-header">
      <div class="header-left">
        <h2>跨公司资产调拨</h2>
        <el-tag type="info" size="small" style="margin-left: 12px">
          财务审计跟踪
        </el-tag>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新建调拨单
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <div class="stat-card pending">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待审批</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card processing">
          <div class="stat-icon">
            <el-icon><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.processing }}</div>
            <div class="stat-label">审批中</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card completed">
          <div class="stat-icon">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card total">
          <div class="stat-icon">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ formatAmount(stats.totalAmount) }}</div>
            <div class="stat-label">调拨总额</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Filters -->
    <div class="filter-bar">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索调拨单号、资产..."
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="状态" clearable @change="loadTransfers">
            <el-option label="待审批" value="pending" />
            <el-option label="调出公司已审批" value="approved_from" />
            <el-option label="全部已审批" value="approved_all" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterType" placeholder="调拨类型" clearable @change="loadTransfers">
            <el-option label="调拨" value="transfer" />
            <el-option label="租赁" value="lease" />
            <el-option label="划拨" value="allocation" />
            <el-option label="出售" value="sale" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="loadTransfers"
          />
        </el-col>
      </el-row>
    </div>

    <!-- Transfer Table -->
    <el-table
      v-loading="loading"
      :data="transfers"
      stripe
      border
      style="width: 100%"
    >
      <el-table-column prop="transfer_no" label="调拨单号" min-width="140" fixed="left">
        <template #default="{ row }">
          <el-link type="primary" @click="showDetail(row)">{{ row.transfer_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="from_company_name" label="调出公司" min-width="120" />
      <el-table-column prop="to_company_name" label="调入公司" min-width="120" />
      <el-table-column prop="transfer_type_display" label="类型" width="80" />
      <el-table-column prop="settlement_type_display" label="结算方式" width="100" />
      <el-table-column prop="transfer_date" label="调拨日期" width="110" />
      <el-table-column label="资产数量" width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small">{{ row.items?.length || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="总金额" width="120" align="right">
        <template #default="{ row }">
          ¥{{ formatAmount(calculateTotal(row)) }}
        </template>
      </el-table-column>
      <el-table-column prop="status_display" label="状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="审批状态" width="160">
        <template #default="{ row }">
          <div class="approval-status">
            <div class="approval-item">
              <span class="label">调出:</span>
              <el-icon v-if="row.from_company_approved_at" color="#67c23a"><Check /></el-icon>
              <el-icon v-else color="#e6a23c"><Clock /></el-icon>
            </div>
            <div class="approval-item">
              <span class="label">调入:</span>
              <el-icon v-if="row.to_company_approved_at" color="#67c23a"><Check /></el-icon>
              <el-icon v-else color="#e6a23c"><Clock /></el-icon>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="canApprove(row, 'from')"
            type="success"
            link
            size="small"
            @click="approveTransfer(row, 'from')"
          >
            调出审批
          </el-button>
          <el-button
            v-if="canApprove(row, 'to')"
            type="success"
            link
            size="small"
            @click="approveTransfer(row, 'to')"
          >
            调入审批
          </el-button>
          <el-button
            v-if="row.status === 'approved_all'"
            type="primary"
            link
            size="small"
            @click="completeTransfer(row)"
          >
            完成
          </el-button>
          <el-button
            v-if="row.status === 'pending'"
            type="danger"
            link
            size="small"
            @click="rejectTransfer(row)"
          >
            拒绝
          </el-button>
          <el-button type="primary" link size="small" @click="showDetail(row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTransfers"
        @current-change="loadTransfers"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建跨公司调拨单"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="调出公司" prop="from_company">
              <el-select v-model="formData.from_company" placeholder="选择调出公司" style="width: 100%">
                <el-option
                  v-for="company in companies"
                  :key="company.id"
                  :label="company.name"
                  :value="company.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调入公司" prop="to_company">
              <el-select
                v-model="formData.to_company"
                placeholder="选择调入公司"
                style="width: 100%"
                :disabled="!formData.from_company"
              >
                <el-option
                  v-for="company in companies.filter(c => c.id !== formData.from_company)"
                  :key="company.id"
                  :label="company.name"
                  :value="company.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="调拨类型" prop="transfer_type">
              <el-select v-model="formData.transfer_type" style="width: 100%">
                <el-option label="调拨" value="transfer" />
                <el-option label="租赁" value="lease" />
                <el-option label="划拨" value="allocation" />
                <el-option label="出售" value="sale" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结算方式" prop="settlement_type">
              <el-select v-model="formData.settlement_type" style="width: 100%">
                <el-option label="内部结算" value="internal" />
                <el-option label="成本分摊" value="cost_allocation" />
                <el-option label="市场价" value="market_price" />
                <el-option label="账面净值" value="book_value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="调拨日期" prop="transfer_date">
          <el-date-picker
            v-model="formData.transfer_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="调拨说明">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="输入调拨原因或备注"
          />
        </el-form-item>

        <el-divider content-position="left">调拨资产</el-divider>
        
        <div class="asset-select-section">
          <el-button type="primary" @click="openAssetSelector" :disabled="!formData.from_company">
            <el-icon><Plus /></el-icon>
            选择资产
          </el-button>
          
          <el-table :data="formData.items" style="margin-top: 12px" border v-if="formData.items.length">
            <el-table-column prop="asset_name" label="资产名称" />
            <el-table-column prop="asset_code" label="资产编号" width="140" />
            <el-table-column label="数量" width="100" align="center">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="结算价格" width="150">
              <template #default="{ row }">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ $index }">
                <el-button type="danger" link size="small" @click="removeItem($index)">
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <el-empty v-else description="暂未选择资产" :image-size="60" />
        </div>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          创建调拨单
        </el-button>
      </template>
    </el-dialog>

    <!-- Asset Selector Dialog -->
    <el-dialog
      v-model="assetSelectorVisible"
      title="选择资产"
      width="900px"
    >
      <el-input
        v-model="assetSearchQuery"
        placeholder="搜索资产名称或编号..."
        clearable
        style="margin-bottom: 16px"
        @input="searchAssets"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-table
        :data="availableAssets"
        v-loading="assetsLoading"
        @selection-change="handleAssetSelection"
        max-height="400"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="name" label="资产名称" />
        <el-table-column prop="asset_code" label="资产编号" width="140" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="original_value" label="原值" width="100" align="right">
          <template #default="{ row }">
            ¥{{ formatAmount(row.original_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_value" label="净值" width="100" align="right">
          <template #default="{ row }">
            ¥{{ formatAmount(row.current_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="80" />
      </el-table>

      <template #footer>
        <el-button @click="assetSelectorVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAssetSelection">
          确定 ({{ selectedAssets.length }}项)
        </el-button>
      </template>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="调拨单详情"
      width="800px"
    >
      <template v-if="currentTransfer">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="调拨单号">{{ currentTransfer.transfer_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTransfer.status)">{{ currentTransfer.status_display }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="调出公司">{{ currentTransfer.from_company_name }}</el-descriptions-item>
          <el-descriptions-item label="调入公司">{{ currentTransfer.to_company_name }}</el-descriptions-item>
          <el-descriptions-item label="调拨类型">{{ currentTransfer.transfer_type_display }}</el-descriptions-item>
          <el-descriptions-item label="结算方式">{{ currentTransfer.settlement_type_display }}</el-descriptions-item>
          <el-descriptions-item label="调拨日期">{{ currentTransfer.transfer_date }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTransfer.created_at }}</el-descriptions-item>
          <el-descriptions-item label="调拨说明" :span="2">
            {{ currentTransfer.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">审批信息</el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="调出公司审批人">
            {{ currentTransfer.from_company_approver_name || '待审批' }}
          </el-descriptions-item>
          <el-descriptions-item label="调出公司审批时间">
            {{ currentTransfer.from_company_approved_at || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="调入公司审批人">
            {{ currentTransfer.to_company_approver_name || '待审批' }}
          </el-descriptions-item>
          <el-descriptions-item label="调入公司审批时间">
            {{ currentTransfer.to_company_approved_at || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">调拨资产明细</el-divider>
        <el-table :data="currentTransfer.items" border>
          <el-table-column prop="asset_name" label="资产名称" />
          <el-table-column prop="asset_code" label="资产编号" width="140" />
          <el-table-column prop="quantity" label="数量" width="80" align="center" />
          <el-table-column label="结算价格" width="120" align="right">
            <template #default="{ row }">
              ¥{{ formatAmount(row.price) }}
            </template>
          </el-table-column>
        </el-table>
        
        <div class="detail-footer">
          <span class="total-label">调拨总额：</span>
          <span class="total-value">¥{{ formatAmount(calculateTotal(currentTransfer)) }}</span>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Clock, Loading, Check, Coin } from '@element-plus/icons-vue'
import request from '@/api/request'
import { useAppStore } from '@/stores/app'
import { extractListData, extractPaginationInfo } from '@/utils/api-helpers'

const appStore = useAppStore()

// State
const loading = ref(false)
const transfers = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const filterStatus = ref(null)
const filterType = ref(null)
const dateRange = ref(null)
const companies = ref([])

const stats = reactive({
  pending: 0,
  processing: 0,
  completed: 0,
  totalAmount: 0
})

// Dialog state
const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const assetSelectorVisible = ref(false)
const currentTransfer = ref(null)
const formRef = ref(null)
const submitting = ref(false)

const formData = reactive({
  from_company: null,
  to_company: null,
  transfer_type: 'transfer',
  settlement_type: 'internal',
  transfer_date: new Date().toISOString().slice(0, 10),
  description: '',
  items: []
})

const formRules = {
  from_company: [{ required: true, message: '请选择调出公司', trigger: 'change' }],
  to_company: [{ required: true, message: '请选择调入公司', trigger: 'change' }],
  transfer_type: [{ required: true, message: '请选择调拨类型', trigger: 'change' }],
  settlement_type: [{ required: true, message: '请选择结算方式', trigger: 'change' }],
  transfer_date: [{ required: true, message: '请选择调拨日期', trigger: 'change' }]
}

// Asset selector state
const assetSearchQuery = ref('')
const availableAssets = ref([])
const selectedAssets = ref([])
const assetsLoading = ref(false)

// Methods
const loadTransfers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      status: filterStatus.value || undefined,
      transfer_type: filterType.value || undefined,
      transfer_date_after: dateRange.value?.[0] || undefined,
      transfer_date_before: dateRange.value?.[1] || undefined
    }
    const res = await request.get('/organizations/cross-transfers/', { params })
    transfers.value = extractListData(res)
    const pageInfo = extractPaginationInfo(res)
    total.value = pageInfo.total || transfers.value.length
    
    // Update stats
    updateStats()
  } catch (error) {
    console.error('Failed to load transfers:', error)
    ElMessage.error('加载调拨单失败')
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const allTransfers = transfers.value
  stats.pending = allTransfers.filter(t => t.status === 'pending').length
  stats.processing = allTransfers.filter(t => ['approved_from'].includes(t.status)).length
  stats.completed = allTransfers.filter(t => t.status === 'completed').length
  stats.totalAmount = allTransfers.reduce((sum, t) => sum + calculateTotal(t), 0)
}

const loadCompanies = async () => {
  try {
    const res = await request.get('/organizations/companies/')
    companies.value = extractListData(res)
  } catch (error) {
    console.error('Failed to load companies:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadTransfers()
}

const formatAmount = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const calculateTotal = (transfer) => {
  if (!transfer?.items) return 0
  return transfer.items.reduce((sum, item) => sum + (parseFloat(item.price) || 0) * (item.quantity || 1), 0)
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    approved_from: 'info',
    approved_all: 'success',
    rejected: 'danger',
    completed: 'success'
  }
  return types[status] || 'info'
}

const canApprove = (row, side) => {
  const currentCompanyId = appStore.currentCompany?.id
  if (!currentCompanyId) return false
  
  if (side === 'from') {
    return row.from_company === currentCompanyId && !row.from_company_approved_at && row.status !== 'rejected'
  } else {
    return row.to_company === currentCompanyId && !row.to_company_approved_at && row.status !== 'rejected' && row.status !== 'pending'
  }
}

const openCreateDialog = () => {
  formData.from_company = appStore.currentCompany?.id || null
  formData.to_company = null
  formData.transfer_type = 'transfer'
  formData.settlement_type = 'internal'
  formData.transfer_date = new Date().toISOString().slice(0, 10)
  formData.description = ''
  formData.items = []
  createDialogVisible.value = true
}

const openAssetSelector = async () => {
  if (!formData.from_company) {
    ElMessage.warning('请先选择调出公司')
    return
  }
  assetSearchQuery.value = ''
  selectedAssets.value = []
  await loadAvailableAssets()
  assetSelectorVisible.value = true
}

const loadAvailableAssets = async () => {
  assetsLoading.value = true
  try {
    const params = {
      company: formData.from_company,
      status: 'in_use',
      search: assetSearchQuery.value || undefined
    }
    const res = await request.get('/assets/assets/', { params })
    availableAssets.value = extractListData(res)
  } catch (error) {
    console.error('Failed to load assets:', error)
  } finally {
    assetsLoading.value = false
  }
}

const searchAssets = () => {
  loadAvailableAssets()
}

const handleAssetSelection = (selection) => {
  selectedAssets.value = selection
}

const confirmAssetSelection = () => {
  selectedAssets.value.forEach(asset => {
    // Check if already added
    if (!formData.items.find(item => item.asset === asset.id)) {
      formData.items.push({
        asset: asset.id,
        asset_name: asset.name,
        asset_code: asset.asset_code,
        quantity: 1,
        price: formData.settlement_type === 'book_value' ? asset.current_value : asset.original_value
      })
    }
  })
  assetSelectorVisible.value = false
}

const removeItem = (index) => {
  formData.items.splice(index, 1)
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (formData.items.length === 0) {
      ElMessage.warning('请至少选择一项资产')
      return
    }
    
    submitting.value = true
    
    const data = {
      from_company: formData.from_company,
      to_company: formData.to_company,
      transfer_type: formData.transfer_type,
      settlement_type: formData.settlement_type,
      transfer_date: formData.transfer_date,
      description: formData.description,
      items: formData.items.map(item => ({
        asset: item.asset,
        quantity: item.quantity,
        price: item.price
      }))
    }
    
    await request.post('/organizations/cross-transfers/', data)
    ElMessage.success('调拨单创建成功')
    createDialogVisible.value = false
    loadTransfers()
  } catch (error) {
    if (error !== false) {
      console.error('Submit failed:', error)
      ElMessage.error(error.response?.data?.msg || '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const showDetail = (row) => {
  currentTransfer.value = row
  detailDialogVisible.value = true
}

const approveTransfer = async (row, side) => {
  try {
    await ElMessageBox.confirm(
      `确定要审批通过此调拨单吗？`,
      '审批确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
    
    await request.post(`/organizations/cross-transfers/${row.id}/approve/`, { side })
    ElMessage.success('审批通过')
    loadTransfers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '审批失败')
    }
  }
}

const rejectTransfer = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝调拨', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '输入拒绝原因...'
    })
    
    await request.post(`/organizations/cross-transfers/${row.id}/reject/`, { reason: value })
    ElMessage.success('已拒绝')
    loadTransfers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '操作失败')
    }
  }
}

const completeTransfer = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要完成此调拨单吗？资产将转移到目标公司。',
      '完成确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    await request.post(`/organizations/cross-transfers/${row.id}/complete/`)
    ElMessage.success('调拨完成')
    loadTransfers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '操作失败')
    }
  }
}

// Lifecycle
onMounted(() => {
  loadCompanies()
  loadTransfers()
})
</script>

<style scoped>
.cross-transfer-container {
  padding: 20px;
  background: var(--el-bg-color);
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.header-left {
  display: flex;
  align-items: center;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  color: #fff;
}

.stat-card.pending {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.stat-card.processing {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
}

.stat-card.completed {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
}

.stat-card.total {
  background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.filter-bar {
  margin-bottom: 16px;
}

.approval-status {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.approval-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.approval-item .label {
  color: var(--el-text-color-secondary);
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.asset-select-section {
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.detail-footer {
  margin-top: 16px;
  text-align: right;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.total-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.total-value {
  font-size: 20px;
  font-weight: bold;
  color: var(--el-color-primary);
  margin-left: 8px;
}
</style>
