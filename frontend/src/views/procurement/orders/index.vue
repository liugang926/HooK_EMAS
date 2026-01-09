<template>
  <div class="purchase-orders-container">
    <DynamicList
      ref="listRef"
      module="purchase_order"
      :actions="['create', 'view', 'export']"
      search-placeholder="搜索订单编号、供应商..."
      create-button-text="新建订单"
      @create="handleCreate"
      @view="handleView"
    >
      <!-- Custom status column -->
      <template #column-status="{ row, value }">
        <el-tag :type="getStatusType(row.status)">
          {{ getStatusLabel(row.status) }}
        </el-tag>
      </template>
      
      <!-- Custom row actions with workflow buttons -->
      <template #row-actions="{ row }">
        <el-button type="primary" link @click.stop="handleView(row)">查看</el-button>
        <el-button 
          v-if="row.status === 'pending'" 
          type="success" 
          link 
          @click.stop="handleReceive(row)"
        >
          验收入库
        </el-button>
        <el-button 
          v-if="row.status === 'pending'" 
          type="danger" 
          link 
          @click.stop="handleCancel(row)"
        >
          取消
        </el-button>
      </template>
      
      <!-- Custom batch actions -->
      <template #batch-actions="{ selected }">
        <el-button size="small" type="success" @click="handleBatchReceive(selected)">
          批量验收
        </el-button>
        <el-button size="small" type="danger" @click="handleBatchCancel(selected)">
          批量取消
        </el-button>
      </template>
    </DynamicList>
    
    <!-- View Detail Dialog -->
    <el-dialog v-model="viewDialogVisible" title="订单详情" width="800px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单编号">{{ currentOrder.order_code || currentOrder.code }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusLabel(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentOrder.supplier_name || currentOrder.supplier }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentOrder.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="下单日期">{{ formatDate(currentOrder.order_date || currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="交付日期">{{ formatDate(currentOrder.delivery_date) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥ {{ currentOrder.total_amount || '0.00' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
      
      <div v-if="currentOrder?.items?.length" style="margin-top: 20px">
        <h4>订单明细</h4>
        <el-table :data="currentOrder.items" border size="small">
          <el-table-column prop="name" label="物品名称" />
          <el-table-column prop="specification" label="规格" width="120" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="unit_price" label="单价" width="100">
            <template #default="{ row }">¥ {{ row.unit_price }}</template>
          </el-table-column>
          <el-table-column prop="subtotal" label="小计" width="100">
            <template #default="{ row }">¥ {{ row.subtotal || (row.quantity * row.unit_price).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button 
          v-if="currentOrder?.status === 'pending'" 
          type="success" 
          @click="handleReceiveFromView"
        >
          验收入库
        </el-button>
      </template>
    </el-dialog>
    
    <!-- Receive Dialog -->
    <el-dialog v-model="receiveDialogVisible" title="验收入库" width="600px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单编号">{{ currentOrder.order_code || currentOrder.code }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentOrder.supplier_name || currentOrder.supplier }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥ {{ currentOrder.total_amount || '0.00' }}</el-descriptions-item>
        <el-descriptions-item label="预计交付">{{ formatDate(currentOrder.delivery_date) || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <el-form style="margin-top: 20px" label-width="100px" :model="receiveForm">
        <el-form-item label="实际到货日期">
          <el-date-picker 
            v-model="receiveForm.receive_date" 
            type="date" 
            placeholder="请选择" 
            value-format="YYYY-MM-DD"
            style="width: 100%" 
          />
        </el-form-item>
        <el-form-item label="验收结果">
          <el-radio-group v-model="receiveForm.result">
            <el-radio value="pass">验收合格</el-radio>
            <el-radio value="partial">部分合格</el-radio>
            <el-radio value="fail">验收不合格</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="验收说明">
          <el-input v-model="receiveForm.remark" type="textarea" :rows="3" placeholder="请输入验收说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="receiveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="confirmReceive">确认入库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import DynamicList from '@/components/list/DynamicList.vue'
import request from '@/api/request'

const listRef = ref(null)
const viewDialogVisible = ref(false)
const receiveDialogVisible = ref(false)
const currentOrder = ref(null)
const submitting = ref(false)

// Receive form
const receiveForm = reactive({
  receive_date: new Date().toISOString().slice(0, 10),
  result: 'pass',
  remark: ''
})

// Status helpers
function getStatusType(status) {
  const types = {
    draft: 'info',
    pending: 'warning',
    approved: 'primary',
    received: 'success',
    cancelled: 'danger',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

function getStatusLabel(status) {
  const labels = {
    draft: '草稿',
    pending: '待收货',
    approved: '已审批',
    received: '已收货',
    cancelled: '已取消',
    rejected: '已拒绝'
  }
  return labels[status] || status
}

// Format date
function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.split('T')[0]
}

// Handle create - redirect to DynamicForm
function handleCreate() {
  // DynamicList will handle this
}

// Handle view
function handleView(row) {
  currentOrder.value = row
  viewDialogVisible.value = true
}

// Handle receive
function handleReceive(row) {
  currentOrder.value = row
  receiveForm.receive_date = new Date().toISOString().slice(0, 10)
  receiveForm.result = 'pass'
  receiveForm.remark = ''
  receiveDialogVisible.value = true
}

function handleReceiveFromView() {
  viewDialogVisible.value = false
  handleReceive(currentOrder.value)
}

// Confirm receive
async function confirmReceive() {
  if (!currentOrder.value) return
  
  submitting.value = true
  try {
    await request.post(`/procurement/orders/${currentOrder.value.id}/receive/`, {
      receive_date: receiveForm.receive_date,
      result: receiveForm.result,
      remark: receiveForm.remark
    })
    
    ElMessage.success('验收入库成功')
    receiveDialogVisible.value = false
    listRef.value?.loadData()
  } catch (error) {
    ElMessage.error('验收失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

// Handle cancel
async function handleCancel(row) {
  try {
    await ElMessageBox.confirm('确定要取消该订单吗？', '取消确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.post(`/procurement/orders/${row.id}/cancel/`)
    ElMessage.success('订单已取消')
    listRef.value?.loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

// Batch receive
async function handleBatchReceive(selected) {
  const pendingOrders = selected.filter(o => o.status === 'pending')
  if (pendingOrders.length === 0) {
    ElMessage.warning('没有可验收的订单')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要批量验收 ${pendingOrders.length} 个订单吗？`,
      '批量验收确认',
      { type: 'info' }
    )
    
    const ids = pendingOrders.map(o => o.id)
    await request.post('/procurement/orders/bulk_receive/', { ids })
    
    ElMessage.success('批量验收成功')
    listRef.value?.loadData()
    listRef.value?.clearSelection()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量验收失败')
    }
  }
}

// Batch cancel
async function handleBatchCancel(selected) {
  const pendingOrders = selected.filter(o => o.status === 'pending')
  if (pendingOrders.length === 0) {
    ElMessage.warning('没有可取消的订单')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要批量取消 ${pendingOrders.length} 个订单吗？`,
      '批量取消确认',
      { type: 'warning' }
    )
    
    const ids = pendingOrders.map(o => o.id)
    await request.post('/procurement/orders/bulk_cancel/', { ids })
    
    ElMessage.success('批量取消成功')
    listRef.value?.loadData()
    listRef.value?.clearSelection()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量取消失败')
    }
  }
}
</script>

<style lang="scss" scoped>
.purchase-orders-container {
  width: 100%;
}
</style>
