<template>
  <div class="purchase-requests-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>采购申请</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建申请
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="申请状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredList" style="width: 100%">
        <el-table-column prop="requestCode" label="申请单号" width="150" />
        <el-table-column prop="title" label="申请标题" min-width="200" />
        <el-table-column prop="applicant" label="申请人" width="100" />
        <el-table-column prop="amount" label="预算金额" width="120" />
        <el-table-column prop="applyDate" label="申请日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 'draft'" type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" type="success" link @click="handleSubmit(row)">提交</el-button>
            <el-button v-if="row.status === 'pending'" type="success" link @click="handleApprove(row)">审批</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="申请详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRequest">
        <el-descriptions-item label="申请单号">{{ currentRequest.requestCode }}</el-descriptions-item>
        <el-descriptions-item label="申请状态">
          <el-tag :type="getStatusType(currentRequest.status)">{{ currentRequest.statusLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="申请标题" :span="2">{{ currentRequest.title }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentRequest.applicant }}</el-descriptions-item>
        <el-descriptions-item label="申请日期">{{ currentRequest.applyDate }}</el-descriptions-item>
        <el-descriptions-item label="预算金额">{{ currentRequest.amount }}</el-descriptions-item>
        <el-descriptions-item label="申请部门">{{ currentRequest.department || '研发部' }}</el-descriptions-item>
        <el-descriptions-item label="申请说明" :span="2">{{ currentRequest.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
      
      <div v-if="currentRequest?.items?.length" style="margin-top: 20px">
        <h4>采购明细</h4>
        <el-table :data="currentRequest.items" border size="small">
          <el-table-column prop="name" label="物品名称" />
          <el-table-column prop="spec" label="规格" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="price" label="预估单价" width="100" />
          <el-table-column prop="total" label="小计" width="100" />
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button v-if="currentRequest?.status === 'draft'" type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="800px">
      <el-form :model="requestForm" label-width="100px" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="申请标题" prop="title">
              <el-input v-model="requestForm.title" placeholder="请输入申请标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="申请部门">
              <el-select v-model="requestForm.department" placeholder="请选择" style="width: 100%">
                <el-option label="研发部" value="研发部" />
                <el-option label="市场部" value="市场部" />
                <el-option label="财务部" value="财务部" />
                <el-option label="行政部" value="行政部" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="采购明细">
          <el-table :data="requestForm.items" border size="small" style="width: 100%">
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
            <el-table-column label="预估单价" width="120">
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
            <el-form-item label="预算总额">
              <el-tag type="warning" size="large">¥ {{ totalAmount }}</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="申请说明">
          <el-input v-model="requestForm.remark" type="textarea" :rows="3" placeholder="请输入申请说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="info" @click="saveDraft">保存草稿</el-button>
        <el-button type="primary" @click="submitRequest">提交申请</el-button>
      </template>
    </el-dialog>
    
    <!-- 审批弹窗 -->
    <el-dialog v-model="approveDialogVisible" title="审批采购申请" width="500px">
      <el-descriptions :column="1" border v-if="currentRequest">
        <el-descriptions-item label="申请单号">{{ currentRequest.requestCode }}</el-descriptions-item>
        <el-descriptions-item label="申请标题">{{ currentRequest.title }}</el-descriptions-item>
        <el-descriptions-item label="预算金额">{{ currentRequest.amount }}</el-descriptions-item>
      </el-descriptions>
      <el-form style="margin-top: 20px" label-width="100px">
        <el-form-item label="审批意见">
          <el-input v-model="approveForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="rejectRequest">拒绝</el-button>
        <el-button type="success" @click="approveRequest">通过</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const filterStatus = ref('')
const formRef = ref(null)

const requestList = ref([
  { 
    id: 1, 
    requestCode: 'CGSQ-2024-0001', 
    title: '研发部电脑采购申请', 
    applicant: '张三', 
    amount: '¥50,000', 
    applyDate: '2024-01-10', 
    status: 'pending', 
    statusLabel: '待审批',
    department: '研发部',
    remark: '研发部需要采购10台高性能电脑用于项目开发',
    items: [
      { name: 'ThinkPad X1 Carbon', spec: 'i7/16G/512G', quantity: 5, price: 8000, total: '¥40,000' },
      { name: 'Dell显示器', spec: '27寸 4K', quantity: 5, price: 2000, total: '¥10,000' }
    ]
  },
  { 
    id: 2, 
    requestCode: 'CGSQ-2024-0002', 
    title: '办公用品采购申请', 
    applicant: '李四', 
    amount: '¥5,000', 
    applyDate: '2024-01-12', 
    status: 'draft', 
    statusLabel: '草稿',
    department: '行政部',
    items: []
  },
  { 
    id: 3, 
    requestCode: 'CGSQ-2024-0003', 
    title: '市场部投影仪采购', 
    applicant: '王五', 
    amount: '¥15,000', 
    applyDate: '2024-01-08', 
    status: 'approved', 
    statusLabel: '已通过',
    department: '市场部',
    items: []
  }
])

const filteredList = computed(() => {
  if (!filterStatus.value) return requestList.value
  return requestList.value.filter(item => item.status === filterStatus.value)
})

// 查看弹窗
const viewDialogVisible = ref(false)
const currentRequest = ref(null)

// 表单弹窗
const formDialogVisible = ref(false)
const formDialogTitle = ref('新建采购申请')
const requestForm = reactive({
  id: null,
  title: '',
  department: '',
  items: [],
  remark: ''
})

const totalAmount = computed(() => {
  return requestForm.items.reduce((sum, item) => sum + (item.quantity || 0) * (item.price || 0), 0).toFixed(2)
})

// 审批弹窗
const approveDialogVisible = ref(false)
const approveForm = reactive({
  comment: ''
})

let idCounter = 100

function getStatusType(status) {
  const types = { draft: 'info', pending: 'warning', approved: 'success', rejected: 'danger' }
  return types[status] || 'info'
}

function handleFilter() {
  ElMessage.success('筛选完成')
}

function handleView(row) {
  currentRequest.value = row
  viewDialogVisible.value = true
}

function handleAdd() {
  formDialogTitle.value = '新建采购申请'
  requestForm.id = null
  requestForm.title = ''
  requestForm.department = ''
  requestForm.items = [{ name: '', spec: '', quantity: 1, price: 0 }]
  requestForm.remark = ''
  formDialogVisible.value = true
}

function handleEdit(row) {
  formDialogTitle.value = '编辑采购申请'
  requestForm.id = row.id
  requestForm.title = row.title
  requestForm.department = row.department
  requestForm.items = row.items?.length ? [...row.items] : [{ name: '', spec: '', quantity: 1, price: 0 }]
  requestForm.remark = row.remark || ''
  formDialogVisible.value = true
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentRequest.value)
}

function handleSubmit(row) {
  row.status = 'pending'
  row.statusLabel = '待审批'
  ElMessage.success('申请已提交审批')
}

function handleApprove(row) {
  currentRequest.value = row
  approveForm.comment = ''
  approveDialogVisible.value = true
}

function addItem() {
  requestForm.items.push({ name: '', spec: '', quantity: 1, price: 0 })
}

function removeItem(index) {
  requestForm.items.splice(index, 1)
}

function saveDraft() {
  if (!requestForm.title) {
    ElMessage.warning('请输入申请标题')
    return
  }
  
  if (requestForm.id) {
    const index = requestList.value.findIndex(item => item.id === requestForm.id)
    if (index !== -1) {
      Object.assign(requestList.value[index], {
        title: requestForm.title,
        department: requestForm.department,
        items: [...requestForm.items],
        remark: requestForm.remark,
        amount: `¥${totalAmount.value}`
      })
    }
    ElMessage.success('草稿已保存')
  } else {
    requestList.value.push({
      id: ++idCounter,
      requestCode: `CGSQ-2024-${String(requestList.value.length + 1).padStart(4, '0')}`,
      title: requestForm.title,
      applicant: 'admin',
      amount: `¥${totalAmount.value}`,
      applyDate: new Date().toISOString().slice(0, 10),
      status: 'draft',
      statusLabel: '草稿',
      department: requestForm.department,
      items: [...requestForm.items],
      remark: requestForm.remark
    })
    ElMessage.success('草稿已保存')
  }
  formDialogVisible.value = false
}

function submitRequest() {
  if (!requestForm.title) {
    ElMessage.warning('请输入申请标题')
    return
  }
  if (requestForm.items.length === 0 || !requestForm.items[0].name) {
    ElMessage.warning('请添加采购明细')
    return
  }
  
  if (requestForm.id) {
    const index = requestList.value.findIndex(item => item.id === requestForm.id)
    if (index !== -1) {
      Object.assign(requestList.value[index], {
        title: requestForm.title,
        department: requestForm.department,
        items: [...requestForm.items],
        remark: requestForm.remark,
        amount: `¥${totalAmount.value}`,
        status: 'pending',
        statusLabel: '待审批'
      })
    }
  } else {
    requestList.value.push({
      id: ++idCounter,
      requestCode: `CGSQ-2024-${String(requestList.value.length + 1).padStart(4, '0')}`,
      title: requestForm.title,
      applicant: 'admin',
      amount: `¥${totalAmount.value}`,
      applyDate: new Date().toISOString().slice(0, 10),
      status: 'pending',
      statusLabel: '待审批',
      department: requestForm.department,
      items: [...requestForm.items],
      remark: requestForm.remark
    })
  }
  ElMessage.success('申请已提交')
  formDialogVisible.value = false
}

function approveRequest() {
  const index = requestList.value.findIndex(item => item.id === currentRequest.value.id)
  if (index !== -1) {
    requestList.value[index].status = 'approved'
    requestList.value[index].statusLabel = '已通过'
  }
  ElMessage.success('审批通过')
  approveDialogVisible.value = false
}

function rejectRequest() {
  const index = requestList.value.findIndex(item => item.id === currentRequest.value.id)
  if (index !== -1) {
    requestList.value[index].status = 'rejected'
    requestList.value[index].statusLabel = '已拒绝'
  }
  ElMessage.success('已拒绝申请')
  approveDialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.purchase-requests-container {
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
