<template>
  <div class="supplies-outbound-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>领用管理</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增领用
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="领用单号">
          <el-input v-model="filterForm.search" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已完成" value="approved" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="outboundList" style="width: 100%" v-loading="loading">
        <el-table-column prop="outbound_no" label="领用单号" width="160" />
        <el-table-column prop="warehouse_name" label="出库仓库" width="120" />
        <el-table-column prop="receive_user_name" label="领用人" width="100" />
        <el-table-column prop="receive_department_name" label="领用部门" width="120" />
        <el-table-column prop="outbound_date" label="领用日期" width="120" />
        <el-table-column prop="item_count" label="品项数" width="100" align="center" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)" v-if="row.status === 'draft'">编辑</el-button>
            <el-button type="success" link @click="handleApprove(row)" v-if="row.status === 'draft'">确认</el-button>
            <el-button type="danger" link @click="handleDelete(row)" v-if="row.status === 'draft'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="900px" destroy-on-close>
      <el-form :model="outboundForm" label-width="100px" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="出库仓库" prop="warehouse">
              <el-select v-model="outboundForm.warehouse" placeholder="请选择" style="width: 100%">
                <el-option v-for="item in warehouseOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="领用日期" prop="outbound_date">
              <el-date-picker v-model="outboundForm.outbound_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="领用人">
              <el-select v-model="outboundForm.receive_user" placeholder="请选择" style="width: 100%" filterable>
                <el-option v-for="item in userOptions" :key="item.id" :label="item.display_name || item.username" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="领用部门">
              <el-select v-model="outboundForm.receive_department" placeholder="请选择" style="width: 100%" filterable clearable>
                <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="领用原因">
              <el-input v-model="outboundForm.reason" placeholder="请输入领用原因" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">领用明细</el-divider>
        
        <el-table :data="outboundForm.items" style="width: 100%" border>
          <el-table-column label="用品" min-width="200">
            <template #default="{ row, $index }">
              <el-select v-model="row.consumable" placeholder="选择用品" style="width: 100%" filterable @change="onSupplyChange($index)">
                <el-option v-for="item in supplyOptions" :key="item.id" :label="`${item.code} - ${item.name}`" :value="item.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="可用库存" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ 'text-danger': getAvailableStock(row.consumable) < row.quantity }">
                {{ getAvailableStock(row.consumable) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="领用数量" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" :max="getAvailableStock(row.consumable) || 9999" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)" :disabled="outboundForm.items.length <= 1">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-button type="primary" link @click="addItem" style="margin-top: 10px">
          <el-icon><Plus /></el-icon> 添加明细
        </el-button>
        
        <el-form-item label="备注" style="margin-top: 16px">
          <el-input v-model="outboundForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getSupplyOutbounds, createSupplyOutbound, updateSupplyOutbound, 
  deleteSupplyOutbound, approveSupplyOutbound,
  getSupplies, getWarehouses, getUsers, getDepartments 
} from '@/api/supplies'

const loading = ref(false)
const submitting = ref(false)
const filterForm = reactive({ search: '', status: '' })
const outboundList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const statusMap = {
  draft: { type: 'info', label: '草稿' },
  pending: { type: 'warning', label: '待审核' },
  approved: { type: 'success', label: '已完成' },
  cancelled: { type: 'danger', label: '已取消' }
}

const warehouseOptions = ref([])
const userOptions = ref([])
const departmentOptions = ref([])
const supplyOptions = ref([])

async function loadData() {
  loading.value = true
  try {
    const params = { 
      page: pagination.page, 
      page_size: pagination.pageSize
    }
    if (filterForm.search) params.search = filterForm.search
    if (filterForm.status) params.status = filterForm.status
    
    const res = await getSupplyOutbounds(params)
    outboundList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('加载领用单失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  try {
    const [warehouseRes, userRes, deptRes, supplyRes] = await Promise.allSettled([
      getWarehouses(),
      getUsers(),
      getDepartments(),
      getSupplies({ is_active: true })
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
    if (supplyRes.status === 'fulfilled') {
      supplyOptions.value = supplyRes.value.results || supplyRes.value || []
    }
  } catch (error) {
    console.error('加载选项失败:', error)
  }
}

function getAvailableStock(consumableId) {
  if (!consumableId) return 0
  const supply = supplyOptions.value.find(s => s.id === consumableId)
  return supply?.total_stock || 0
}

function handleSearch() { 
  pagination.page = 1
  loadData() 
}

function handleReset() { 
  filterForm.search = ''
  filterForm.status = ''
  handleSearch() 
}

const formDialogVisible = ref(false)
const formDialogTitle = ref('新增领用')
const formRef = ref(null)
const outboundForm = reactive({
  id: null, 
  warehouse: null, 
  outbound_date: new Date().toISOString().split('T')[0],
  receive_user: null, 
  receive_department: null, 
  reason: '',
  items: [{ consumable: null, quantity: 1 }], 
  remark: ''
})

function handleAdd() {
  formDialogTitle.value = '新增领用'
  Object.assign(outboundForm, { 
    id: null, 
    warehouse: warehouseOptions.value[0]?.id || null, 
    outbound_date: new Date().toISOString().split('T')[0], 
    receive_user: null, 
    receive_department: null,
    reason: '',
    items: [{ consumable: null, quantity: 1 }], 
    remark: '' 
  })
  formDialogVisible.value = true
}

function handleView(row) { 
  ElMessage.info('查看领用单: ' + row.outbound_no) 
}

function handleEdit(row) { 
  formDialogTitle.value = '编辑领用'
  formDialogVisible.value = true 
}

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('确认领用将扣减库存，是否继续？', '确认', { type: 'warning' })
    await approveSupplyOutbound(row.id)
    ElMessage.success('领用确认成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除该领用单？', '确认', { type: 'warning' })
    await deleteSupplyOutbound(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function addItem() { 
  outboundForm.items.push({ consumable: null, quantity: 1 }) 
}

function removeItem(index) { 
  outboundForm.items.splice(index, 1) 
}

function onSupplyChange(index) {
  // Can add additional logic here if needed
}

async function submitForm() {
  if (!outboundForm.warehouse) { 
    ElMessage.warning('请选择出库仓库')
    return 
  }
  if (!outboundForm.receive_user) { 
    ElMessage.warning('请选择领用人')
    return 
  }
  if (outboundForm.items.some(i => !i.consumable)) { 
    ElMessage.warning('请选择用品')
    return 
  }
  
  // Check stock availability
  for (const item of outboundForm.items) {
    const stock = getAvailableStock(item.consumable)
    if (item.quantity > stock) {
      const supply = supplyOptions.value.find(s => s.id === item.consumable)
      ElMessage.warning(`${supply?.name || '用品'} 库存不足，当前库存: ${stock}`)
      return
    }
  }
  
  submitting.value = true
  try {
    const data = {
      warehouse: outboundForm.warehouse, 
      outbound_date: outboundForm.outbound_date,
      receive_user: outboundForm.receive_user, 
      receive_department: outboundForm.receive_department,
      reason: outboundForm.reason,
      remark: outboundForm.remark,
      items: outboundForm.items.map(i => ({ 
        consumable: i.consumable, 
        quantity: i.quantity
      }))
    }
    
    if (outboundForm.id) {
      await updateSupplyOutbound(outboundForm.id, data)
    } else {
      await createSupplyOutbound(data)
    }
    
    ElMessage.success('保存成功')
    formDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => { 
  loadData()
  loadOptions() 
})
</script>

<style lang="scss" scoped>
.supplies-outbound-container {
  .page-card { border-radius: 16px; }
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  .filter-form { margin-bottom: 16px; }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
  .text-danger { color: #f56c6c; }
}
</style>
