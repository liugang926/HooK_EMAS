<template>
  <div class="inventory-tasks-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>资产盘点任务</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建盘点
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20" class="stat-row">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">盘点任务总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card warning">
            <div class="stat-value">{{ stats.inProgress }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card success">
            <div class="stat-value">{{ stats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card danger">
            <div class="stat-value">{{ stats.abnormal }}</div>
            <div class="stat-label">异常资产</div>
          </div>
        </el-col>
      </el-row>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="任务状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="待执行" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredList" style="width: 100%">
        <el-table-column prop="taskCode" label="任务编号" width="150" />
        <el-table-column prop="name" label="任务名称" min-width="200" />
        <el-table-column prop="scope" label="盘点范围" width="150" />
        <el-table-column prop="executor" label="执行人" width="100" />
        <el-table-column prop="startDate" label="开始日期" width="120" />
        <el-table-column prop="endDate" label="结束日期" width="120" />
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.progress === 100 ? 'success' : ''" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 'in_progress'" type="success" link @click="handleContinue(row)">继续盘点</el-button>
            <el-button v-if="row.status === 'pending'" type="warning" link @click="handleStart(row)">开始盘点</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="盘点任务详情" width="900px">
      <el-descriptions :column="2" border v-if="currentTask">
        <el-descriptions-item label="任务编号">{{ currentTask.taskCode }}</el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <el-tag :type="getStatusType(currentTask.status)">{{ currentTask.statusLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="任务名称" :span="2">{{ currentTask.name }}</el-descriptions-item>
        <el-descriptions-item label="盘点范围">{{ currentTask.scope }}</el-descriptions-item>
        <el-descriptions-item label="执行人">{{ currentTask.executor }}</el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentTask.startDate }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{ currentTask.endDate }}</el-descriptions-item>
        <el-descriptions-item label="盘点进度" :span="2">
          <el-progress :percentage="currentTask.progress" :status="currentTask.progress === 100 ? 'success' : ''" style="width: 300px" />
        </el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px">
        <h4>盘点明细</h4>
        <el-table :data="currentTask?.details || []" border size="small" max-height="300">
          <el-table-column prop="assetCode" label="资产编号" width="120" />
          <el-table-column prop="assetName" label="资产名称" min-width="150" />
          <el-table-column prop="location" label="存放位置" width="120" />
          <el-table-column label="盘点状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getCheckStatusType(row.checkStatus)" size="small">{{ row.checkStatusLabel }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="checkTime" label="盘点时间" width="160" />
          <el-table-column prop="remark" label="备注" min-width="120" />
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button v-if="currentTask?.status === 'in_progress'" type="primary" @click="handleContinueFromView">继续盘点</el-button>
        <el-button v-if="currentTask?.status === 'completed'" type="success" @click="exportReport">导出报告</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建盘点弹窗 -->
    <el-dialog v-model="formDialogVisible" title="新建盘点任务" width="700px">
      <el-form :model="taskForm" label-width="100px" ref="formRef" :rules="formRules">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="盘点范围" prop="scope">
              <el-select v-model="taskForm.scope" placeholder="请选择" style="width: 100%">
                <el-option label="全公司" value="全公司" />
                <el-option label="研发部" value="研发部" />
                <el-option label="市场部" value="市场部" />
                <el-option label="财务部" value="财务部" />
                <el-option label="行政部" value="行政部" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="执行人" prop="executor">
              <el-select v-model="taskForm.executor" placeholder="请选择" style="width: 100%">
                <el-option label="张三" value="张三" />
                <el-option label="李四" value="李四" />
                <el-option label="王五" value="王五" />
                <el-option label="赵六" value="赵六" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="startDate">
              <el-date-picker v-model="taskForm.startDate" type="date" placeholder="请选择" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="endDate">
              <el-date-picker v-model="taskForm.endDate" type="date" placeholder="请选择" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="盘点说明">
          <el-input v-model="taskForm.remark" type="textarea" :rows="3" placeholder="请输入盘点说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTask">创建任务</el-button>
      </template>
    </el-dialog>
    
    <!-- 盘点执行弹窗 -->
    <el-dialog v-model="checkDialogVisible" title="执行盘点" width="900px">
      <el-descriptions :column="3" border v-if="currentTask" style="margin-bottom: 20px">
        <el-descriptions-item label="任务编号">{{ currentTask.taskCode }}</el-descriptions-item>
        <el-descriptions-item label="盘点范围">{{ currentTask.scope }}</el-descriptions-item>
        <el-descriptions-item label="当前进度">{{ currentTask.progress }}%</el-descriptions-item>
      </el-descriptions>
      
      <el-table :data="pendingAssets" border size="small" max-height="400">
        <el-table-column prop="assetCode" label="资产编号" width="120" />
        <el-table-column prop="assetName" label="资产名称" min-width="150" />
        <el-table-column prop="location" label="存放位置" width="120" />
        <el-table-column prop="currentUser" label="使用人" width="100" />
        <el-table-column label="盘点结果" width="180">
          <template #default="{ row }">
            <el-radio-group v-model="row.checkResult" size="small">
              <el-radio-button label="normal">正常</el-radio-button>
              <el-radio-button label="abnormal">异常</el-radio-button>
              <el-radio-button label="missing">盘亏</el-radio-button>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="备注" width="150">
          <template #default="{ row }">
            <el-input v-model="row.checkRemark" size="small" placeholder="备注" />
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="checkDialogVisible = false">取消</el-button>
        <el-button type="info" @click="saveDraft">暂存</el-button>
        <el-button type="primary" @click="submitCheck">提交盘点结果</el-button>
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

const stats = reactive({ total: 15, inProgress: 2, completed: 12, abnormal: 8 })

const taskList = ref([
  { 
    id: 1, 
    taskCode: 'PD-2024-0001', 
    name: '2024年1月全公司资产盘点', 
    scope: '全公司', 
    executor: '张三', 
    startDate: '2024-01-01', 
    endDate: '2024-01-15', 
    progress: 85, 
    status: 'in_progress', 
    statusLabel: '进行中',
    details: [
      { assetCode: 'ZC-2024-0001', assetName: 'ThinkPad X1 Carbon', location: '研发部', checkStatus: 'normal', checkStatusLabel: '正常', checkTime: '2024-01-05 10:30', remark: '' },
      { assetCode: 'ZC-2024-0002', assetName: 'Dell显示器', location: '研发部', checkStatus: 'normal', checkStatusLabel: '正常', checkTime: '2024-01-05 10:35', remark: '' },
      { assetCode: 'ZC-2024-0003', assetName: '办公桌椅', location: '市场部', checkStatus: 'abnormal', checkStatusLabel: '异常', checkTime: '2024-01-05 11:00', remark: '桌面有损坏' },
      { assetCode: 'ZC-2024-0004', assetName: '投影仪', location: '会议室', checkStatus: 'pending', checkStatusLabel: '待盘点', checkTime: '', remark: '' }
    ]
  },
  { 
    id: 2, 
    taskCode: 'PD-2023-0012', 
    name: '2023年12月研发部盘点', 
    scope: '研发部', 
    executor: '李四', 
    startDate: '2023-12-20', 
    endDate: '2023-12-25', 
    progress: 100, 
    status: 'completed', 
    statusLabel: '已完成',
    details: [
      { assetCode: 'ZC-2023-0001', assetName: '开发服务器', location: '机房', checkStatus: 'normal', checkStatusLabel: '正常', checkTime: '2023-12-22 09:00', remark: '' },
      { assetCode: 'ZC-2023-0002', assetName: '测试设备', location: '测试区', checkStatus: 'normal', checkStatusLabel: '正常', checkTime: '2023-12-22 09:30', remark: '' }
    ]
  },
  { 
    id: 3, 
    taskCode: 'PD-2024-0002', 
    name: '2024年2月财务部盘点', 
    scope: '财务部', 
    executor: '王五', 
    startDate: '2024-02-01', 
    endDate: '2024-02-10', 
    progress: 0, 
    status: 'pending', 
    statusLabel: '待执行',
    details: []
  }
])

const filteredList = computed(() => {
  if (!filterStatus.value) return taskList.value
  return taskList.value.filter(item => item.status === filterStatus.value)
})

// 待盘点资产
const pendingAssets = ref([
  { assetCode: 'ZC-2024-0004', assetName: '投影仪', location: '会议室', currentUser: '公用', checkResult: '', checkRemark: '' },
  { assetCode: 'ZC-2024-0005', assetName: '打印机', location: '行政部', currentUser: '公用', checkResult: '', checkRemark: '' },
  { assetCode: 'ZC-2024-0006', assetName: 'MacBook Pro', location: '研发部', currentUser: '张三', checkResult: '', checkRemark: '' },
  { assetCode: 'ZC-2024-0007', assetName: '会议室桌椅', location: '会议室', currentUser: '公用', checkResult: '', checkRemark: '' }
])

// 查看弹窗
const viewDialogVisible = ref(false)
const currentTask = ref(null)

// 新建弹窗
const formDialogVisible = ref(false)
const taskForm = reactive({
  name: '',
  scope: '',
  executor: '',
  startDate: '',
  endDate: '',
  remark: ''
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  scope: [{ required: true, message: '请选择盘点范围', trigger: 'change' }],
  executor: [{ required: true, message: '请选择执行人', trigger: 'change' }],
  startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  endDate: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

// 盘点执行弹窗
const checkDialogVisible = ref(false)

let idCounter = 100

function getStatusType(status) {
  const types = { pending: 'info', in_progress: 'warning', completed: 'success' }
  return types[status] || 'info'
}

function getCheckStatusType(status) {
  const types = { pending: 'info', normal: 'success', abnormal: 'warning', missing: 'danger' }
  return types[status] || 'info'
}

function handleFilter() {
  ElMessage.success('筛选完成')
}

function handleView(row) {
  currentTask.value = row
  viewDialogVisible.value = true
}

function handleAdd() {
  Object.assign(taskForm, {
    name: '',
    scope: '',
    executor: '',
    startDate: '',
    endDate: '',
    remark: ''
  })
  formDialogVisible.value = true
}

function handleStart(row) {
  row.status = 'in_progress'
  row.statusLabel = '进行中'
  stats.inProgress++
  currentTask.value = row
  checkDialogVisible.value = true
  ElMessage.success('盘点任务已开始')
}

function handleContinue(row) {
  currentTask.value = row
  checkDialogVisible.value = true
}

function handleContinueFromView() {
  viewDialogVisible.value = false
  checkDialogVisible.value = true
}

function submitTask() {
  formRef.value?.validate((valid) => {
    if (valid) {
      const newTask = {
        id: ++idCounter,
        taskCode: `PD-2024-${String(taskList.value.length + 1).padStart(4, '0')}`,
        name: taskForm.name,
        scope: taskForm.scope,
        executor: taskForm.executor,
        startDate: taskForm.startDate ? taskForm.startDate.toISOString().slice(0, 10) : '',
        endDate: taskForm.endDate ? taskForm.endDate.toISOString().slice(0, 10) : '',
        progress: 0,
        status: 'pending',
        statusLabel: '待执行',
        details: []
      }
      taskList.value.push(newTask)
      stats.total++
      ElMessage.success('盘点任务创建成功')
      formDialogVisible.value = false
    }
  })
}

function saveDraft() {
  const checkedCount = pendingAssets.value.filter(a => a.checkResult).length
  const totalCount = pendingAssets.value.length + (currentTask.value?.details?.filter(d => d.checkStatus !== 'pending').length || 0)
  const progress = Math.round((checkedCount + (currentTask.value?.details?.filter(d => d.checkStatus !== 'pending').length || 0)) / (totalCount + pendingAssets.value.length) * 100)
  
  if (currentTask.value) {
    currentTask.value.progress = Math.min(progress, 99) // 暂存不到100%
  }
  
  ElMessage.success('已暂存盘点进度')
  checkDialogVisible.value = false
}

function submitCheck() {
  const unchecked = pendingAssets.value.filter(a => !a.checkResult)
  if (unchecked.length > 0) {
    ElMessage.warning(`还有 ${unchecked.length} 项资产未盘点`)
    return
  }
  
  // 更新盘点明细
  const now = new Date().toLocaleString()
  pendingAssets.value.forEach(asset => {
    const statusMap = { normal: '正常', abnormal: '异常', missing: '盘亏' }
    currentTask.value.details.push({
      assetCode: asset.assetCode,
      assetName: asset.assetName,
      location: asset.location,
      checkStatus: asset.checkResult,
      checkStatusLabel: statusMap[asset.checkResult],
      checkTime: now,
      remark: asset.checkRemark
    })
    
    if (asset.checkResult !== 'normal') {
      stats.abnormal++
    }
  })
  
  // 计算新进度
  const totalDetails = currentTask.value.details.length
  const checkedDetails = currentTask.value.details.filter(d => d.checkStatus !== 'pending').length
  currentTask.value.progress = Math.round(checkedDetails / totalDetails * 100)
  
  if (currentTask.value.progress >= 100) {
    currentTask.value.status = 'completed'
    currentTask.value.statusLabel = '已完成'
    stats.inProgress--
    stats.completed++
  }
  
  ElMessage.success('盘点结果已提交')
  checkDialogVisible.value = false
  
  // 重置待盘点资产
  pendingAssets.value.forEach(a => {
    a.checkResult = ''
    a.checkRemark = ''
  })
}

function exportReport() {
  ElMessage.success('盘点报告导出成功')
}
</script>

<style lang="scss" scoped>
.inventory-tasks-container {
  .page-card { border-radius: 16px; }
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    h2 { margin: 0; font-size: 18px; color: #1f2937; } 
  }
  .stat-row { margin-bottom: 20px; }
  .stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px; padding: 20px; color: #fff;
    &.warning { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    &.success { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    &.danger { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .stat-value { font-size: 28px; font-weight: bold; }
    .stat-label { font-size: 14px; opacity: 0.9; margin-top: 4px; }
  }
  .filter-form { margin-bottom: 16px; }
}
</style>
