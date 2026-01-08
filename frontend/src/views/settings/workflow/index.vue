<template>
  <div class="workflow-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>审批流设置</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建审批流
          </el-button>
        </div>
      </template>
      
      <el-table :data="workflowList" style="width: 100%">
        <el-table-column prop="name" label="审批流名称" min-width="150" />
        <el-table-column prop="type" label="业务类型" width="120" />
        <el-table-column label="审批节点" width="200">
          <template #default="{ row }">
            <div class="steps-preview">
              <el-tag v-for="(step, index) in row.stepsList" :key="index" size="small" style="margin-right: 4px">
                {{ step }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleStatusChange(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="updateTime" label="更新时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="审批流详情" width="700px">
      <el-descriptions :column="2" border v-if="currentWorkflow">
        <el-descriptions-item label="审批流名称">{{ currentWorkflow.name }}</el-descriptions-item>
        <el-descriptions-item label="业务类型">{{ currentWorkflow.type }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentWorkflow.enabled ? 'success' : 'info'">
            {{ currentWorkflow.enabled ? '启用' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ currentWorkflow.updateTime }}</el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px">
        <h4>审批流程</h4>
        <el-steps :active="currentWorkflow?.stepsList?.length" align-center>
          <el-step v-for="(step, index) in currentWorkflow?.stepsList" :key="index" :title="step" />
        </el-steps>
      </div>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="700px">
      <el-form :model="workflowForm" label-width="100px" :rules="formRules" ref="formRef">
        <el-form-item label="审批流名称" prop="name">
          <el-input v-model="workflowForm.name" placeholder="请输入审批流名称" />
        </el-form-item>
        <el-form-item label="业务类型" prop="type">
          <el-select v-model="workflowForm.type" placeholder="请选择业务类型" style="width: 100%">
            <el-option label="资产领用" value="资产领用" />
            <el-option label="资产归还" value="资产归还" />
            <el-option label="资产调拨" value="资产调拨" />
            <el-option label="资产处置" value="资产处置" />
            <el-option label="采购申请" value="采购申请" />
            <el-option label="耗材领用" value="耗材领用" />
          </el-select>
        </el-form-item>
        <el-form-item label="审批节点">
          <div class="step-editor">
            <div v-for="(step, index) in workflowForm.steps" :key="index" class="step-item">
              <el-tag closable @close="removeStep(index)">
                节点{{ index + 1 }}: {{ step.name }} ({{ step.approver }})
              </el-tag>
            </div>
            <el-button type="primary" link @click="addStep">
              <el-icon><Plus /></el-icon>
              添加节点
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="workflowForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWorkflow">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加节点弹窗 -->
    <el-dialog v-model="stepDialogVisible" title="添加审批节点" width="500px">
      <el-form :model="stepForm" label-width="80px">
        <el-form-item label="节点名称">
          <el-input v-model="stepForm.name" placeholder="如：部门主管审批" />
        </el-form-item>
        <el-form-item label="审批人">
          <el-select v-model="stepForm.approverType" placeholder="请选择审批人类型" style="width: 100%">
            <el-option label="指定人员" value="user" />
            <el-option label="部门主管" value="dept_leader" />
            <el-option label="上级主管" value="superior" />
            <el-option label="指定角色" value="role" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="stepForm.approverType === 'user'" label="选择人员">
          <el-select v-model="stepForm.approverId" placeholder="请选择审批人" style="width: 100%">
            <el-option label="张三" value="1" />
            <el-option label="李四" value="2" />
            <el-option label="王五" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="stepForm.approverType === 'role'" label="选择角色">
          <el-select v-model="stepForm.approverId" placeholder="请选择角色" style="width: 100%">
            <el-option label="资产管理员" value="asset_admin" />
            <el-option label="部门经理" value="dept_manager" />
            <el-option label="财务主管" value="finance_manager" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stepDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddStep">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const formRef = ref()

const workflowList = ref([
  { id: 1, name: '资产领用审批', type: '资产领用', steps: 2, stepsList: ['部门主管', '资产管理员'], enabled: true, updateTime: '2024-01-10 10:30' },
  { id: 2, name: '资产采购审批', type: '采购申请', steps: 3, stepsList: ['部门主管', '财务主管', '总经理'], enabled: true, updateTime: '2024-01-08 14:20' },
  { id: 3, name: '资产处置审批', type: '资产处置', steps: 2, stepsList: ['资产管理员', '财务主管'], enabled: true, updateTime: '2024-01-05 09:15' }
])

// 查看弹窗
const viewDialogVisible = ref(false)
const currentWorkflow = ref(null)

// 表单弹窗
const formDialogVisible = ref(false)
const formDialogTitle = ref('新建审批流')
const workflowForm = reactive({
  id: null,
  name: '',
  type: '',
  steps: [],
  enabled: true
})

const formRules = {
  name: [{ required: true, message: '请输入审批流名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择业务类型', trigger: 'change' }]
}

// 节点弹窗
const stepDialogVisible = ref(false)
const stepForm = reactive({
  name: '',
  approverType: '',
  approverId: ''
})

let idCounter = 100

function handleView(row) {
  currentWorkflow.value = row
  viewDialogVisible.value = true
}

function handleAdd() {
  formDialogTitle.value = '新建审批流'
  Object.assign(workflowForm, { id: null, name: '', type: '', steps: [], enabled: true })
  formDialogVisible.value = true
}

function handleEdit(row) {
  formDialogTitle.value = '编辑审批流'
  Object.assign(workflowForm, {
    id: row.id,
    name: row.name,
    type: row.type,
    steps: row.stepsList.map((name, i) => ({ name, approver: name })),
    enabled: row.enabled
  })
  formDialogVisible.value = true
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentWorkflow.value)
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除审批流 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = workflowList.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      workflowList.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleStatusChange(row) {
  ElMessage.success(`审批流 "${row.name}" 已${row.enabled ? '启用' : '停用'}`)
}

function addStep() {
  Object.assign(stepForm, { name: '', approverType: '', approverId: '' })
  stepDialogVisible.value = true
}

function confirmAddStep() {
  if (!stepForm.name || !stepForm.approverType) {
    ElMessage.warning('请填写完整节点信息')
    return
  }
  const approverMap = {
    user: stepForm.approverId === '1' ? '张三' : stepForm.approverId === '2' ? '李四' : '王五',
    dept_leader: '部门主管',
    superior: '上级主管',
    role: stepForm.approverId === 'asset_admin' ? '资产管理员' : stepForm.approverId === 'dept_manager' ? '部门经理' : '财务主管'
  }
  workflowForm.steps.push({
    name: stepForm.name,
    approver: approverMap[stepForm.approverType]
  })
  stepDialogVisible.value = false
}

function removeStep(index) {
  workflowForm.steps.splice(index, 1)
}

function saveWorkflow() {
  formRef.value?.validate((valid) => {
    if (valid) {
      if (workflowForm.steps.length === 0) {
        ElMessage.warning('请至少添加一个审批节点')
        return
      }
      
      const now = new Date().toLocaleString().slice(0, 16)
      if (workflowForm.id) {
        const index = workflowList.value.findIndex(item => item.id === workflowForm.id)
        if (index !== -1) {
          workflowList.value[index] = {
            ...workflowList.value[index],
            name: workflowForm.name,
            type: workflowForm.type,
            steps: workflowForm.steps.length,
            stepsList: workflowForm.steps.map(s => s.approver),
            enabled: workflowForm.enabled,
            updateTime: now
          }
        }
        ElMessage.success('审批流编辑成功')
      } else {
        workflowList.value.push({
          id: ++idCounter,
          name: workflowForm.name,
          type: workflowForm.type,
          steps: workflowForm.steps.length,
          stepsList: workflowForm.steps.map(s => s.approver),
          enabled: workflowForm.enabled,
          updateTime: now
        })
        ElMessage.success('审批流创建成功')
      }
      formDialogVisible.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.workflow-container {
  .page-card { border-radius: 16px; }
  .page-header { display: flex; justify-content: space-between; align-items: center; h2 { margin: 0; font-size: 18px; color: #1f2937; } }
  .steps-preview { display: flex; flex-wrap: wrap; gap: 4px; }
  .step-editor {
    .step-item { margin-bottom: 8px; }
  }
}
</style>
