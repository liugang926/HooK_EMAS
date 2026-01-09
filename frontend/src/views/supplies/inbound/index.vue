<template>
  <div class="supplies-inbound-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>入库管理</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增入库
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="入库单号">
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
      
      <el-table :data="inboundList" style="width: 100%" v-loading="loading">
        <el-table-column prop="inbound_no" label="入库单号" width="160" />
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="supplier_name" label="供应商" width="150" />
        <el-table-column prop="inbound_date" label="入库日期" width="120" />
        <el-table-column prop="item_count" label="品项数" width="100" align="center" />
        <el-table-column label="金额" width="120">
          <template #default="{ row }">{{ row.total_amount }}</template>
        </el-table-column>
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
      <el-form :model="inboundForm" label-width="100px" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="仓库" prop="warehouse">
              <el-select v-model="inboundForm.warehouse" placeholder="请选择" style="width: 100%">
                <el-option v-for="item in warehouseOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="入库日期" prop="inbound_date">
              <el-date-picker v-model="inboundForm.inbound_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="供应商">
              <el-select v-model="inboundForm.supplier" placeholder="请选择" style="width: 100%" clearable filterable>
                <el-option v-for="item in supplierOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">入库明细</el-divider>
        
        <el-table :data="inboundForm.items" style="width: 100%" border>
          <el-table-column label="用品" min-width="200">
            <template #default="{ row, $index }">
              <el-select v-model="row.consumable" placeholder="选择用品" style="width: 100%" filterable @change="onSupplyChange($index)">
                <el-option v-for="item in supplyOptions" :key="item.id" :label="`${item.code} - ${item.name}`" :value="item.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="单价" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120">
            <template #default="{ row }">
              {{ ((row.quantity || 0) * (row.price || 0)).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)" :disabled="inboundForm.items.length <= 1">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-button type="primary" link @click="addItem" style="margin-top: 10px">
          <el-icon><Plus /></el-icon> 添加明细
        </el-button>
        
        <el-form-item label="备注" style="margin-top: 16px">
          <el-input v-model="inboundForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
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
  getSupplyInbounds, createSupplyInbound, updateSupplyInbound, 
  deleteSupplyInbound, approveSupplyInbound,
  getSupplies, getWarehouses, getSuppliers 
} from '@/api/supplies'

const loading = ref(false)
const submitting = ref(false)
const filterForm = reactive({ search: '', status: '' })
const inboundList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const statusMap = {
  draft: { type: 'info', label: '草稿' },
  pending: { type: 'warning', label: '待审核' },
  approved: { type: 'success', label: '已完成' },
  cancelled: { type: 'danger', label: '已取消' }
}

const warehouseOptions = ref([])
const supplierOptions = ref([])
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
    
    const res = await getSupplyInbounds(params)
    inboundList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('加载入库单失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  try {
    const [warehouseRes, supplierRes, supplyRes] = await Promise.allSettled([
      getWarehouses(),
      getSuppliers(),
      getSupplies({ is_active: true })
    ])
    
    if (warehouseRes.status === 'fulfilled') {
      warehouseOptions.value = warehouseRes.value.results || warehouseRes.value || []
    }
    if (supplierRes.status === 'fulfilled') {
      supplierOptions.value = supplierRes.value.results || supplierRes.value || []
    }
    if (supplyRes.status === 'fulfilled') {
      supplyOptions.value = supplyRes.value.results || supplyRes.value || []
    }
  } catch (error) {
    console.error('加载选项失败:', error)
  }
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
const formDialogTitle = ref('新增入库')
const formRef = ref(null)
const inboundForm = reactive({
  id: null, 
  warehouse: null, 
  inbound_date: new Date().toISOString().split('T')[0],
  supplier: null, 
  items: [{ consumable: null, quantity: 1, price: 0 }], 
  remark: ''
})

function handleAdd() {
  formDialogTitle.value = '新增入库'
  Object.assign(inboundForm, { 
    id: null, 
    warehouse: warehouseOptions.value[0]?.id || null, 
    inbound_date: new Date().toISOString().split('T')[0], 
    supplier: null, 
    items: [{ consumable: null, quantity: 1, price: 0 }], 
    remark: '' 
  })
  formDialogVisible.value = true
}

function handleView(row) { 
  ElMessage.info('查看入库单: ' + row.inbound_no) 
}

function handleEdit(row) { 
  formDialogTitle.value = '编辑入库'
  formDialogVisible.value = true 
}

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('确认入库将更新库存，是否继续？', '确认', { type: 'warning' })
    await approveSupplyInbound(row.id)
    ElMessage.success('入库确认成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除该入库单？', '确认', { type: 'warning' })
    await deleteSupplyInbound(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function addItem() { 
  inboundForm.items.push({ consumable: null, quantity: 1, price: 0 }) 
}

function removeItem(index) { 
  inboundForm.items.splice(index, 1) 
}

function onSupplyChange(index) {
  const item = inboundForm.items[index]
  const supply = supplyOptions.value.find(s => s.id === item.consumable)
  if (supply) item.price = parseFloat(supply.price) || 0
}

async function submitForm() {
  if (!inboundForm.warehouse) { 
    ElMessage.warning('请选择仓库')
    return 
  }
  if (inboundForm.items.some(i => !i.consumable)) { 
    ElMessage.warning('请选择用品')
    return 
  }
  
  submitting.value = true
  try {
    const totalAmount = inboundForm.items.reduce((sum, i) => sum + (i.quantity * i.price), 0)
    const data = {
      warehouse: inboundForm.warehouse, 
      inbound_date: inboundForm.inbound_date,
      supplier: inboundForm.supplier, 
      total_amount: totalAmount.toFixed(2), 
      remark: inboundForm.remark,
      items: inboundForm.items.map(i => ({ 
        consumable: i.consumable, 
        quantity: i.quantity, 
        price: i.price, 
        amount: (i.quantity * i.price).toFixed(2) 
      }))
    }
    
    if (inboundForm.id) {
      await updateSupplyInbound(inboundForm.id, data)
    } else {
      await createSupplyInbound(data)
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
.supplies-inbound-container {
  .page-card { border-radius: 16px; }
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  .filter-form { margin-bottom: 16px; }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>
