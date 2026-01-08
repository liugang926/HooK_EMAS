<template>
  <div class="consumable-stock-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>实时库存</h2>
          <div>
            <el-button type="success" @click="handleBatchInbound">
              <el-icon><Plus /></el-icon>
              批量入库
            </el-button>
          </div>
        </div>
      </template>
      
      <el-row :gutter="20" class="stat-row">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ stockList.length }}</div>
            <div class="stat-label">耗材种类</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card warning">
            <div class="stat-value">{{ warningCount }}</div>
            <div class="stat-label">库存预警</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card info">
            <div class="stat-value">¥ {{ totalValue }}</div>
            <div class="stat-label">库存总值</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card success">
            <div class="stat-value">{{ totalStock }}</div>
            <div class="stat-label">库存总量</div>
          </div>
        </el-col>
      </el-row>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="库存状态">
          <el-select v-model="stockFilter" placeholder="全部" clearable style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="正常" value="normal" />
            <el-option label="预警" value="warning" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredStockList" style="width: 100%">
        <el-table-column prop="name" label="耗材名称" min-width="150" />
        <el-table-column prop="code" label="编号" width="100" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price" label="单价" width="100">
          <template #default="{ row }">
            ¥ {{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="当前库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stock <= row.minStock ? 'danger' : 'success'">{{ row.stock }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="minStock" label="安全库存" width="100" />
        <el-table-column prop="location" label="存放位置" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="success" link @click="handleInbound(row)">入库</el-button>
            <el-button type="warning" link @click="handleOutbound(row)">出库</el-button>
            <el-button type="primary" link @click="handleViewRecord(row)">记录</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 入库弹窗 -->
    <el-dialog v-model="inboundDialogVisible" title="耗材入库" width="500px">
      <el-form :model="inboundForm" label-width="100px">
        <el-form-item label="耗材">
          <span class="consumable-info">{{ inboundForm.name }} ({{ inboundForm.code }})</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <el-tag type="info">{{ inboundForm.currentStock }} {{ inboundForm.unit }}</el-tag>
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="inboundForm.quantity" :min="1" style="width: 200px" />
          <span style="margin-left: 10px">{{ inboundForm.unit }}</span>
        </el-form-item>
        <el-form-item label="入库日期">
          <el-date-picker v-model="inboundForm.date" type="date" placeholder="请选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="inboundForm.supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="inboundForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="inboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitInbound">确认入库</el-button>
      </template>
    </el-dialog>
    
    <!-- 出库弹窗 -->
    <el-dialog v-model="outboundDialogVisible" title="耗材出库" width="500px">
      <el-form :model="outboundForm" label-width="100px">
        <el-form-item label="耗材">
          <span class="consumable-info">{{ outboundForm.name }} ({{ outboundForm.code }})</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <el-tag :type="outboundForm.currentStock <= outboundForm.minStock ? 'danger' : 'success'">
            {{ outboundForm.currentStock }} {{ outboundForm.unit }}
          </el-tag>
        </el-form-item>
        <el-form-item label="出库数量">
          <el-input-number v-model="outboundForm.quantity" :min="1" :max="outboundForm.currentStock" style="width: 200px" />
          <span style="margin-left: 10px">{{ outboundForm.unit }}</span>
        </el-form-item>
        <el-form-item label="出库类型">
          <el-select v-model="outboundForm.type" placeholder="请选择" style="width: 100%">
            <el-option label="领用" value="use" />
            <el-option label="报损" value="damage" />
            <el-option label="调拨" value="transfer" />
          </el-select>
        </el-form-item>
        <el-form-item label="领用人" v-if="outboundForm.type === 'use'">
          <el-select v-model="outboundForm.userId" placeholder="请选择领用人" style="width: 100%">
            <el-option label="张三" value="1" />
            <el-option label="李四" value="2" />
            <el-option label="王五" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="出库日期">
          <el-date-picker v-model="outboundForm.date" type="date" placeholder="请选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="outboundForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="outboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOutbound">确认出库</el-button>
      </template>
    </el-dialog>
    
    <!-- 出入库记录弹窗 -->
    <el-dialog v-model="recordDialogVisible" title="出入库记录" width="700px">
      <div class="record-info" v-if="currentConsumable">
        <span>耗材：{{ currentConsumable.name }} ({{ currentConsumable.code }})</span>
        <span>当前库存：<el-tag>{{ currentConsumable.stock }}</el-tag></span>
      </div>
      <el-table :data="recordList" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.type === 'in' ? 'success' : 'warning'">
              {{ row.type === 'in' ? '入库' : '出库' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100">
          <template #default="{ row }">
            <span :class="row.type === 'in' ? 'text-success' : 'text-warning'">
              {{ row.type === 'in' ? '+' : '-' }}{{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="remark" label="备注" />
      </el-table>
      <template #footer>
        <el-button @click="recordDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const stockFilter = ref('')

const stockList = ref([
  { id: 1, code: 'HC-0001', name: 'A4打印纸', category: '办公用品', unit: '包', price: '25.00', stock: 50, minStock: 20, location: '仓库A' },
  { id: 2, code: 'HC-0002', name: '签字笔', category: '办公用品', unit: '支', price: '3.00', stock: 10, minStock: 50, location: '仓库A' },
  { id: 3, code: 'HC-0003', name: '文件夹', category: '办公用品', unit: '个', price: '8.00', stock: 100, minStock: 30, location: '仓库B' },
  { id: 4, code: 'HC-0004', name: '墨盒', category: '电子耗材', unit: '个', price: '180.00', stock: 5, minStock: 10, location: '仓库A' },
  { id: 5, code: 'HC-0005', name: '订书机', category: '办公用品', unit: '个', price: '15.00', stock: 25, minStock: 10, location: '仓库B' }
])

// 统计数据
const warningCount = computed(() => stockList.value.filter(item => item.stock <= item.minStock).length)
const totalValue = computed(() => {
  return stockList.value.reduce((sum, item) => sum + (parseFloat(item.price) * item.stock), 0).toFixed(2)
})
const totalStock = computed(() => stockList.value.reduce((sum, item) => sum + item.stock, 0))

const filteredStockList = computed(() => {
  if (!stockFilter.value) return stockList.value
  if (stockFilter.value === 'warning') {
    return stockList.value.filter(item => item.stock <= item.minStock)
  }
  return stockList.value.filter(item => item.stock > item.minStock)
})

// 入库弹窗
const inboundDialogVisible = ref(false)
const inboundForm = ref({
  id: null,
  code: '',
  name: '',
  unit: '',
  currentStock: 0,
  quantity: 1,
  date: new Date(),
  supplier: '',
  remark: ''
})

// 出库弹窗
const outboundDialogVisible = ref(false)
const outboundForm = ref({
  id: null,
  code: '',
  name: '',
  unit: '',
  currentStock: 0,
  minStock: 0,
  quantity: 1,
  type: 'use',
  userId: '',
  date: new Date(),
  remark: ''
})

// 记录弹窗
const recordDialogVisible = ref(false)
const currentConsumable = ref(null)
const recordList = ref([])

function handleFilter() {
  ElMessage.success('筛选完成')
}

function handleBatchInbound() {
  ElMessage.info('批量入库功能，可上传Excel批量导入')
}

function handleInbound(row) {
  inboundForm.value = {
    id: row.id,
    code: row.code,
    name: row.name,
    unit: row.unit,
    currentStock: row.stock,
    quantity: 1,
    date: new Date(),
    supplier: '',
    remark: ''
  }
  inboundDialogVisible.value = true
}

function handleOutbound(row) {
  outboundForm.value = {
    id: row.id,
    code: row.code,
    name: row.name,
    unit: row.unit,
    currentStock: row.stock,
    minStock: row.minStock,
    quantity: 1,
    type: 'use',
    userId: '',
    date: new Date(),
    remark: ''
  }
  outboundDialogVisible.value = true
}

function handleViewRecord(row) {
  currentConsumable.value = row
  // 模拟记录数据
  recordList.value = [
    { id: 1, date: '2024-01-15', type: 'in', quantity: 100, operator: '管理员', remark: '采购入库' },
    { id: 2, date: '2024-01-18', type: 'out', quantity: 20, operator: '张三', remark: '部门领用' },
    { id: 3, date: '2024-01-20', type: 'out', quantity: 30, operator: '李四', remark: '项目使用' },
    { id: 4, date: '2024-01-22', type: 'in', quantity: 50, operator: '管理员', remark: '补货入库' }
  ]
  recordDialogVisible.value = true
}

function submitInbound() {
  if (inboundForm.value.quantity <= 0) {
    ElMessage.warning('入库数量必须大于0')
    return
  }
  const index = stockList.value.findIndex(item => item.id === inboundForm.value.id)
  if (index !== -1) {
    stockList.value[index].stock += inboundForm.value.quantity
  }
  ElMessage.success(`入库成功！入库数量：${inboundForm.value.quantity} ${inboundForm.value.unit}`)
  inboundDialogVisible.value = false
}

function submitOutbound() {
  if (outboundForm.value.quantity <= 0) {
    ElMessage.warning('出库数量必须大于0')
    return
  }
  if (outboundForm.value.quantity > outboundForm.value.currentStock) {
    ElMessage.warning('出库数量不能超过当前库存')
    return
  }
  const index = stockList.value.findIndex(item => item.id === outboundForm.value.id)
  if (index !== -1) {
    stockList.value[index].stock -= outboundForm.value.quantity
    // 检查是否低于安全库存
    if (stockList.value[index].stock <= stockList.value[index].minStock) {
      ElMessage.warning(`注意：${stockList.value[index].name} 库存已低于安全库存！`)
    }
  }
  ElMessage.success(`出库成功！出库数量：${outboundForm.value.quantity} ${outboundForm.value.unit}`)
  outboundDialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.consumable-stock-container {
  .page-card { 
    border-radius: 16px; 
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    h2 { margin: 0; font-size: 18px; color: #1f2937; }
  }
  
  .stat-row { margin-bottom: 20px; }
  
  .stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 20px;
    color: #fff;
    
    &.warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    &.info { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    &.success { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    
    .stat-value { font-size: 28px; font-weight: bold; }
    .stat-label { font-size: 14px; opacity: 0.9; margin-top: 4px; }
  }
  
  .filter-form { margin-bottom: 16px; }
  
  .text-danger { color: #f56c6c; font-weight: bold; }
  .text-success { color: #67c23a; font-weight: bold; }
  .text-warning { color: #e6a23c; font-weight: bold; }
  
  .consumable-info {
    font-weight: 500;
    color: #303133;
  }
  
  .record-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 8px;
    margin-bottom: 16px;
  }
}
</style>
