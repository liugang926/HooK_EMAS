<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="700px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <!-- Selected assets summary -->
    <div class="selected-assets-summary">
      <div class="summary-header">
        <el-icon><Box /></el-icon>
        <span>已选择 <strong>{{ selectedAssets.length }}</strong> 项资产</span>
      </div>
      <el-table :data="selectedAssets" max-height="200" size="small" border>
        <el-table-column prop="asset_code" label="资产编号" width="140" />
        <el-table-column prop="name" label="资产名称" min-width="150" />
        <el-table-column label="当前状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="using_user_name" label="当前使用人" width="100" />
        <el-table-column prop="using_department_name" label="当前部门" width="120" />
      </el-table>
    </div>

    <el-divider />

    <!-- Batch Receive Form -->
    <el-form
      v-if="operationType === 'receive'"
      ref="formRef"
      :model="receiveForm"
      :rules="receiveRules"
      label-width="100px"
    >
      <el-form-item label="领用人" prop="receive_user">
        <el-select
          v-model="receiveForm.receive_user"
          filterable
          placeholder="请选择领用人"
          style="width: 100%"
        >
          <el-option
            v-for="user in userOptions"
            :key="user.id"
            :label="user.display_name || user.username"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="领用部门" prop="receive_department">
        <el-tree-select
          v-model="receiveForm.receive_department"
          :data="departmentOptions"
          :props="{ value: 'id', label: 'displayName', children: 'children' }"
          placeholder="请选择领用部门"
          check-strictly
          filterable
          clearable
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="存放位置">
        <el-tree-select
          v-model="receiveForm.receive_location"
          :data="locationOptions"
          :props="{ value: 'id', label: 'displayName', children: 'children' }"
          placeholder="请选择存放位置（可选）"
          check-strictly
          filterable
          clearable
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="领用日期" prop="receive_date">
        <el-date-picker
          v-model="receiveForm.receive_date"
          type="date"
          placeholder="请选择领用日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="领用原因">
        <el-input
          v-model="receiveForm.reason"
          type="textarea"
          :rows="3"
          placeholder="请输入领用原因（可选）"
        />
      </el-form-item>
    </el-form>

    <!-- Batch Return Form -->
    <el-form
      v-else-if="operationType === 'return'"
      ref="formRef"
      :model="returnForm"
      :rules="returnRules"
      label-width="100px"
    >
      <el-form-item label="退还日期" prop="return_date">
        <el-date-picker
          v-model="returnForm.return_date"
          type="date"
          placeholder="请选择退还日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="退还原因">
        <el-input
          v-model="returnForm.reason"
          type="textarea"
          :rows="3"
          placeholder="请输入退还原因（可选）"
        />
      </el-form-item>
      <div class="return-info">
        <el-alert
          title="退还后资产将变为闲置状态，使用人和部门信息将被清空"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
    </el-form>

    <!-- Batch Transfer Form -->
    <el-form
      v-else-if="operationType === 'transfer'"
      ref="formRef"
      :model="transferForm"
      :rules="transferRules"
      label-width="100px"
    >
      <el-alert
        title="请至少选择一个调拨目标（新部门、新使用人或新存放位置）"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      
      <el-form-item label="新使用人">
        <el-select
          v-model="transferForm.to_user"
          filterable
          clearable
          placeholder="选择新使用人（可选）"
          style="width: 100%"
        >
          <el-option
            v-for="user in userOptions"
            :key="user.id"
            :label="user.display_name || user.username"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="新部门">
        <el-tree-select
          v-model="transferForm.to_department"
          :data="departmentOptions"
          :props="{ value: 'id', label: 'displayName', children: 'children' }"
          placeholder="选择新部门（可选）"
          check-strictly
          filterable
          clearable
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="新存放位置">
        <el-tree-select
          v-model="transferForm.to_location"
          :data="locationOptions"
          :props="{ value: 'id', label: 'displayName', children: 'children' }"
          placeholder="选择新存放位置（可选）"
          check-strictly
          filterable
          clearable
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="调拨日期" prop="transfer_date">
        <el-date-picker
          v-model="transferForm.transfer_date"
          type="date"
          placeholder="请选择调拨日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="调拨原因">
        <el-input
          v-model="transferForm.reason"
          type="textarea"
          :rows="3"
          placeholder="请输入调拨原因（可选）"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ submitButtonText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box } from '@element-plus/icons-vue'
import {
  batchReceiveAssets,
  batchReturnAssets,
  batchTransferAssets
} from '@/api/assets'
import request from '@/utils/request'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  operationType: {
    type: String, // 'receive', 'return', 'transfer'
    default: 'receive'
  },
  selectedAssets: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialogTitle = computed(() => {
  const titles = {
    receive: '批量领用',
    return: '批量退还',
    transfer: '批量调拨'
  }
  return titles[props.operationType] || '批量操作'
})

const submitButtonText = computed(() => {
  const texts = {
    receive: '确认领用',
    return: '确认退还',
    transfer: '确认调拨'
  }
  return texts[props.operationType] || '确认'
})

// Status mapping
const statusMap = {
  idle: { label: '闲置', type: 'warning' },
  in_use: { label: '使用中', type: 'success' },
  borrowed: { label: '借用中', type: 'primary' },
  maintenance: { label: '维修中', type: 'danger' },
  disposed: { label: '已处置', type: 'info' }
}

function getStatusType(status) {
  return statusMap[status]?.type || 'info'
}

function getStatusLabel(status) {
  return statusMap[status]?.label || status
}

// State
const formRef = ref()
const submitting = ref(false)
const userOptions = ref([])
const departmentOptions = ref([])
const locationOptions = ref([])

// Form data
const receiveForm = reactive({
  receive_user: null,
  receive_department: null,
  receive_location: null,
  receive_date: new Date().toISOString().split('T')[0],
  reason: ''
})

const returnForm = reactive({
  return_date: new Date().toISOString().split('T')[0],
  reason: ''
})

const transferForm = reactive({
  to_user: null,
  to_department: null,
  to_location: null,
  transfer_date: new Date().toISOString().split('T')[0],
  reason: ''
})

// Validation rules
const receiveRules = {
  receive_user: [{ required: true, message: '请选择领用人', trigger: 'change' }],
  receive_date: [{ required: true, message: '请选择领用日期', trigger: 'change' }]
}

const returnRules = {
  return_date: [{ required: true, message: '请选择退还日期', trigger: 'change' }]
}

const transferRules = {
  transfer_date: [{ required: true, message: '请选择调拨日期', trigger: 'change' }]
}

// Load options
async function loadUsers() {
  try {
    const res = await request.get('/auth/users/', { params: { page_size: 1000 } })
    userOptions.value = res?.results || res || []
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

async function loadDepartments() {
  try {
    const res = await request.get('/organizations/departments/tree/')
    const data = res || []
    departmentOptions.value = addPathToTree(data, '')
  } catch (error) {
    console.error('加载部门失败:', error)
  }
}

async function loadLocations() {
  try {
    const res = await request.get('/organizations/locations/tree/')
    const data = res || []
    locationOptions.value = addPathToTree(data, '')
  } catch (error) {
    console.error('加载位置失败:', error)
  }
}

function addPathToTree(nodes, parentPath) {
  return nodes.map(node => {
    const currentPath = parentPath ? `${parentPath} > ${node.name}` : node.name
    const result = {
      ...node,
      displayName: parentPath ? `${node.name} (${parentPath})` : node.name,
      fullPath: currentPath
    }
    if (node.children && node.children.length > 0) {
      result.children = addPathToTree(node.children, currentPath)
    }
    return result
  })
}

// Submit handlers
async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch (error) {
    return
  }

  // Get asset IDs
  const assetIds = props.selectedAssets.map(a => a.id)
  
  if (assetIds.length === 0) {
    ElMessage.warning('请选择要操作的资产')
    return
  }

  // Confirm action
  const actionText = {
    receive: '领用',
    return: '退还',
    transfer: '调拨'
  }[props.operationType]

  try {
    await ElMessageBox.confirm(
      `确定要${actionText} ${assetIds.length} 项资产吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  submitting.value = true

  try {
    let result
    
    if (props.operationType === 'receive') {
      result = await batchReceiveAssets({
        asset_ids: assetIds,
        receive_user: receiveForm.receive_user,
        receive_department: receiveForm.receive_department,
        receive_location: receiveForm.receive_location,
        receive_date: receiveForm.receive_date,
        reason: receiveForm.reason
      })
    } else if (props.operationType === 'return') {
      result = await batchReturnAssets({
        asset_ids: assetIds,
        return_date: returnForm.return_date,
        reason: returnForm.reason
      })
    } else if (props.operationType === 'transfer') {
      // Validate at least one target is selected
      if (!transferForm.to_user && !transferForm.to_department && !transferForm.to_location) {
        ElMessage.warning('请至少选择一个调拨目标')
        submitting.value = false
        return
      }
      
      result = await batchTransferAssets({
        asset_ids: assetIds,
        to_user: transferForm.to_user,
        to_department: transferForm.to_department,
        to_location: transferForm.to_location,
        transfer_date: transferForm.transfer_date,
        reason: transferForm.reason
      })
    }

    if (result?.success) {
      ElMessage.success(result.message || `${actionText}成功`)
      emit('success')
      handleClose()
    } else {
      ElMessage.error(result?.message || `${actionText}失败`)
      
      // Show invalid assets if any
      if (result?.invalid_assets?.length > 0) {
        ElMessageBox.alert(
          `<div style="max-height: 300px; overflow: auto;">
            <ul style="margin: 0; padding-left: 20px;">
              ${result.invalid_assets.map(a => `<li>${a}</li>`).join('')}
            </ul>
          </div>`,
          '以下资产无法操作',
          {
            dangerouslyUseHTMLString: true,
            confirmButtonText: '知道了'
          }
        )
      }
    }
  } catch (error) {
    console.error(`${actionText}失败:`, error)
    ElMessage.error(error.response?.data?.message || `${actionText}失败`)
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  visible.value = false
}

function handleClosed() {
  // Reset forms
  Object.assign(receiveForm, {
    receive_user: null,
    receive_department: null,
    receive_location: null,
    receive_date: new Date().toISOString().split('T')[0],
    reason: ''
  })
  Object.assign(returnForm, {
    return_date: new Date().toISOString().split('T')[0],
    reason: ''
  })
  Object.assign(transferForm, {
    to_user: null,
    to_department: null,
    to_location: null,
    transfer_date: new Date().toISOString().split('T')[0],
    reason: ''
  })
  formRef.value?.resetFields()
}

// Load data when dialog opens
watch(visible, (val) => {
  if (val) {
    loadUsers()
    loadDepartments()
    // Load locations for both receive and transfer operations
    if (props.operationType === 'receive' || props.operationType === 'transfer') {
      loadLocations()
    }
  }
})

onMounted(() => {
  // Pre-load options
  loadUsers()
  loadDepartments()
  loadLocations()
})
</script>

<style lang="scss" scoped>
.selected-assets-summary {
  .summary-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #374151;
    
    .el-icon {
      color: var(--el-color-primary);
    }
    
    strong {
      color: var(--el-color-primary);
      font-size: 16px;
    }
  }
}

.return-info {
  margin-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
