<template>
  <div class="purchase-orders-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>采购订单</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建订单
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="订单状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="待收货" value="pending" />
            <el-option label="已收货" value="received" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredList" style="width: 100%">
        <el-table-column prop="orderCode" label="订单编号" width="150" />
        <el-table-column prop="supplier" label="供应商" width="150" />
        <el-table-column prop="amount" label="订单金额" width="120" />
        <el-table-column prop="orderDate" label="下单日期" width="120" />
        <el-table-column prop="deliveryDate" label="交付日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 'pending'" type="success" link @click="handleReceive(row)">验收入库</el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="handleCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="订单详情" width="800px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单编号">{{ currentOrder.orderCode }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(currentOrder.status)">{{ currentOrder.statusLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentOrder.supplier }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentOrder.contact || '张经理' }}</el-descriptions-item>
        <el-descriptions-item label="下单日期">{{ currentOrder.orderDate }}</el-descriptions-item>
        <el-descriptions-item label="交付日期">{{ currentOrder.deliveryDate }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">{{ currentOrder.amount }}</el-descriptions-item>
        <el-descriptions-item label="关联申请">{{ currentOrder.requestCode || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
      
      <div v-if="currentOrder?.items?.length" style="margin-top: 20px">
        <h4>订单明细</h4>
        <el-table :data="currentOrder.items" border size="small">
          <el-table-column prop="name" label="物品名称" />
          <el-table-column prop="spec" label="规格" width="120" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="price" label="单价" width="100" />
          <el-table-column prop="total" label="小计" width="100" />
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button v-if="currentOrder?.status === 'pending'" type="success" @click="handleReceiveFromView">验收入库</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建订单弹窗 -->
    <el-dialog v-model="formDialogVisible" title="新建采购订单" width="800px">
      <el-form :model="orderForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-select v-model="orderForm.supplierId" placeholder="请选择供应商" style="width: 100%">
                <el-option 
                  v-for="s in supplierOptions" 
                  :key="s.id" 
                  :label="s.name" 
                  :value="s.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计交付日期">
              <el-date-picker v-model="orderForm.deliveryDate" type="date" placeholder="请选择" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="关联申请">
          <el-select v-model="orderForm.requestId" placeholder="请选择（可选）" clearable style="width: 100%">
            <el-option 
              v-for="r in requestOptions" 
              :key="r.id" 
              :label="`${r.code} - ${r.title}`" 
              :value="r.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="订单明细">
          <el-table :data="orderForm.items" border size="small" style="width: 100%">
            <el-table-column label="物品名称" min-width="150">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="物品名称" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="规格" width="120">
              <template #default="{ row }">
                <el-input v-model="row.spec" placeholder="规格" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="数量" width="100">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" size="small" style="width: 80px" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width: 100px" />
              </template>
            </el-table-column>
            <el-table-column label="小计" width="100">
              <template #default="{ row }">
                ¥ {{ ((row.quantity || 0) * (row.price || 0)).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
                <el-button type="danger" link size="small" @click="removeItem($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button type="primary" link @click="addItem" style="margin-top: 10px">
            <el-icon><Plus /></el-icon> 添加明细
          </el-button>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单总额">
              <el-tag type="warning" size="large">¥ {{ totalAmount }}</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="备注">
          <el-input v-model="orderForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">创建订单</el-button>
      </template>
    </el-dialog>
    
    <!-- 验收入库弹窗 -->
    <el-dialog v-model="receiveDialogVisible" title="验收入库" width="600px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单编号">{{ currentOrder.orderCode }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentOrder.supplier }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">{{ currentOrder.amount }}</el-descriptions-item>
        <el-descriptions-item label="预计交付">{{ currentOrder.deliveryDate }}</el-descriptions-item>
      </el-descriptions>
      
      <el-form style="margin-top: 20px" label-width="100px">
        <el-form-item label="实际到货日期">
          <el-date-picker v-model="receiveForm.receiveDate" type="date" placeholder="请选择" style="width: 100%" />
        </el-form-item>
        <el-form-item label="验收结果">
          <el-radio-group v-model="receiveForm.result">
            <el-radio label="pass">验收合格</el-radio>
            <el-radio label="partial">部分合格</el-radio>
            <el-radio label="fail">验收不合格</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="验收说明">
          <el-input v-model="receiveForm.remark" type="textarea" :rows="3" placeholder="请输入验收说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="receiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmReceive">确认入库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const filterStatus = ref('')

const orderList = ref([
  { 
    id: 1, 
    orderCode: 'PO-2024-0001', 
    supplier: '联想科技', 
    amount: '¥48,500', 
    orderDate: '2024-01-12', 
    deliveryDate: '2024-01-20', 
    status: 'pending', 
    statusLabel: '待收货',
    contact: '张经理',
    requestCode: 'CGSQ-2024-0001',
    items: [
      { name: 'ThinkPad X1 Carbon', spec: 'i7/16G/512G', quantity: 5, price: 7700, total: '¥38,500' },
      { name: 'Dell显示器', spec: '27寸 4K', quantity: 5, price: 2000, total: '¥10,000' }
    ]
  },
  { 
    id: 2, 
    orderCode: 'PO-2024-0002', 
    supplier: 'Dell中国', 
    amount: '¥15,000', 
    orderDate: '2024-01-15', 
    deliveryDate: '2024-01-25', 
    status: 'received', 
    statusLabel: '已收货',
    items: []
  }
])

const filteredList = computed(() => {
  if (!filterStatus.value) return orderList.value
  return orderList.value.filter(item => item.status === filterStatus.value)
})

const supplierOptions = ref([
  { id: 1, name: '联想科技' },
  { id: 2, name: 'Dell中国' },
  { id: 3, name: 'HP中国' },
  { id: 4, name: '华为技术' }
])

const requestOptions = ref([
  { id: 1, code: 'CGSQ-2024-0001', title: '研发部电脑采购申请' },
  { id: 3, code: 'CGSQ-2024-0003', title: '市场部投影仪采购' }
])

// 查看弹窗
const viewDialogVisible = ref(false)
const currentOrder = ref(null)

// 新建弹窗
const formDialogVisible = ref(false)
const orderForm = reactive({
  supplierId: '',
  deliveryDate: '',
  requestId: '',
  items: [],
  remark: ''
})

const totalAmount = computed(() => {
  return orderForm.items.reduce((sum, item) => sum + (item.quantity || 0) * (item.price || 0), 0).toFixed(2)
})

// 验收弹窗
const receiveDialogVisible = ref(false)
const receiveForm = reactive({
  receiveDate: new Date(),
  result: 'pass',
  remark: ''
})

let idCounter = 100

function getStatusType(status) {
  const types = { draft: 'info', pending: 'warning', received: 'success', cancelled: 'danger' }
  return types[status] || 'info'
}

function handleFilter() {
  ElMessage.success('筛选完成')
}

function handleView(row) {
  currentOrder.value = row
  viewDialogVisible.value = true
}

function handleAdd() {
  orderForm.supplierId = ''
  orderForm.deliveryDate = ''
  orderForm.requestId = ''
  orderForm.items = [{ name: '', spec: '', quantity: 1, price: 0 }]
  orderForm.remark = ''
  formDialogVisible.value = true
}

function handleReceive(row) {
  currentOrder.value = row
  receiveForm.receiveDate = new Date()
  receiveForm.result = 'pass'
  receiveForm.remark = ''
  receiveDialogVisible.value = true
}

function handleReceiveFromView() {
  viewDialogVisible.value = false
  handleReceive(currentOrder.value)
}

function handleCancel(row) {
  ElMessageBox.confirm('确定要取消该订单吗？', '取消确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = 'cancelled'
    row.statusLabel = '已取消'
    ElMessage.success('订单已取消')
  }).catch(() => {})
}

function addItem() {
  orderForm.items.push({ name: '', spec: '', quantity: 1, price: 0 })
}

function removeItem(index) {
  orderForm.items.splice(index, 1)
}

function submitOrder() {
  if (!orderForm.supplierId) {
    ElMessage.warning('请选择供应商')
    return
  }
  if (orderForm.items.length === 0 || !orderForm.items[0].name) {
    ElMessage.warning('请添加订单明细')
    return
  }
  
  const supplier = supplierOptions.value.find(s => s.id === orderForm.supplierId)
  orderList.value.push({
    id: ++idCounter,
    orderCode: `PO-2024-${String(orderList.value.length + 1).padStart(4, '0')}`,
    supplier: supplier ? supplier.name : '',
    amount: `¥${totalAmount.value}`,
    orderDate: new Date().toISOString().slice(0, 10),
    deliveryDate: orderForm.deliveryDate ? orderForm.deliveryDate.toISOString().slice(0, 10) : '',
    status: 'pending',
    statusLabel: '待收货',
    items: [...orderForm.items],
    remark: orderForm.remark
  })
  
  ElMessage.success('订单创建成功')
  formDialogVisible.value = false
}

function confirmReceive() {
  const index = orderList.value.findIndex(item => item.id === currentOrder.value.id)
  if (index !== -1) {
    orderList.value[index].status = 'received'
    orderList.value[index].statusLabel = '已收货'
  }
  ElMessage.success('验收入库成功')
  receiveDialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.purchase-orders-container {
  .page-card { border-radius: 16px; }
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  .filter-form { margin-bottom: 16px; }
}
</style>
