<template>
  <div class="permissions-container">
    <!-- 顶部操作栏 -->
    <el-card class="action-card" style="margin-bottom: 16px;">
      <div class="action-bar">
        <div class="action-info">
          <el-icon><InfoFilled /></el-icon>
          <span>角色权限说明：超级管理员拥有所有权限；部门管理员可管理本部门资产；普通员工可查看和申请资产。同步后会自动分配角色。</span>
        </div>
        <div class="action-buttons">
          <el-button type="primary" @click="handleSyncRoles" :loading="syncingRoles">
            <el-icon><Refresh /></el-icon>
            同步角色
          </el-button>
        </div>
      </div>
    </el-card>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="role-card">
          <template #header>
            <div class="card-header">
              <span>角色列表</span>
              <el-button type="primary" link @click="handleAddRole">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="role-list" v-loading="loadingRoles">
            <div
              v-for="role in roleList"
              :key="role.id"
              :class="['role-item', { active: currentRole?.id === role.id }]"
              @click="selectRole(role)"
            >
              <div class="role-info">
                <div class="role-name">
                  {{ role.name }}
                  <el-tag v-if="role.is_system" size="small" type="info" style="margin-left: 8px;">系统</el-tag>
                </div>
                <div class="role-desc">{{ role.description }}</div>
              </div>
              <el-tag size="small">{{ role.user_count || 0 }}人</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card class="permission-card">
          <template #header>
            <div class="card-header">
              <span>{{ currentRole?.name || '选择角色' }} - 权限配置</span>
              <div>
                <el-button @click="handleEditRole" :disabled="!currentRole || currentRole.is_system">编辑角色</el-button>
                <el-button type="primary" @click="handleSave" :disabled="!currentRole">保存权限</el-button>
              </div>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="功能权限" name="function">
              <el-tree
                ref="permissionTreeRef"
                :data="permissionTree"
                :props="{ label: 'name', children: 'children' }"
                show-checkbox
                default-expand-all
                node-key="id"
                v-model:checked="checkedPermissions"
              />
            </el-tab-pane>
            <el-tab-pane label="数据权限" name="data">
              <el-form label-width="120px">
                <el-form-item label="数据范围">
                  <el-radio-group v-model="dataScope">
                    <el-radio label="all">全部数据</el-radio>
                    <el-radio label="dept">本部门数据</el-radio>
                    <el-radio label="dept_below">本部门及以下</el-radio>
                    <el-radio label="self">仅本人数据</el-radio>
                    <el-radio label="custom">自定义</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item v-if="dataScope === 'custom'" label="自定义部门">
                  <el-tree-select
                    v-model="customDepts"
                    :data="deptTree"
                    :props="{ label: 'name', value: 'id', children: 'children' }"
                    multiple
                    check-strictly
                    placeholder="请选择可访问的部门"
                    style="width: 400px"
                  />
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="角色成员" name="members">
              <div style="margin-bottom: 16px">
                <el-button type="primary" size="small" @click="handleAddMember">添加成员</el-button>
              </div>
              <el-table :data="roleMembers" v-loading="loadingMembers">
                <el-table-column prop="name" label="姓名" width="100" />
                <el-table-column prop="department" label="部门" />
                <el-table-column prop="position" label="职位" />
                <el-table-column prop="phone" label="手机号" width="130" />
                <el-table-column label="操作" width="80">
                  <template #default="{ row }">
                    <el-button type="danger" link size="small" @click="handleRemoveMember(row)">移除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加/编辑角色弹窗 -->
    <el-dialog v-model="roleDialogVisible" :title="roleDialogTitle" width="500px">
      <el-form :model="roleForm" label-width="80px" :rules="roleRules" ref="roleFormRef">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input v-model="roleForm.code" placeholder="请输入角色代码（英文）" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input v-model="roleForm.description" type="textarea" :rows="3" placeholder="请输入角色描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRole" :loading="savingRole">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加成员弹窗 -->
    <el-dialog v-model="memberDialogVisible" title="添加角色成员" width="700px">
      <el-transfer
        v-model="selectedMembers"
        :data="availableMembers"
        :titles="['可选员工', '已选员工']"
        :props="{ key: 'id', label: 'label' }"
        filterable
        filter-placeholder="搜索员工"
      />
      <template #footer>
        <el-button @click="memberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddMembers" :loading="addingMembers">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { Plus, Refresh, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import request from '@/utils/request'
import { extractListData } from '@/utils/api-helpers'

const activeTab = ref('function')
const currentRole = ref(null)
const dataScope = ref('all')
const customDepts = ref([])
const permissionTreeRef = ref()
const roleFormRef = ref()

const loadingRoles = ref(false)
const loadingMembers = ref(false)
const savingRole = ref(false)
const addingMembers = ref(false)
const syncingRoles = ref(false)

const checkedPermissions = ref([])
const roleList = ref([])
const roleMembers = ref([])
const deptTree = ref([])

const permissionTree = ref([
  { id: 1, name: '资产管理', children: [
    { id: 11, name: '资产查看' },
    { id: 12, name: '资产新增' },
    { id: 13, name: '资产编辑' },
    { id: 14, name: '资产删除' },
    { id: 15, name: '资产导出' },
    { id: 16, name: '资产领用' },
    { id: 17, name: '资产退还' },
    { id: 18, name: '资产借用' },
    { id: 19, name: '资产调拨' }
  ]},
  { id: 2, name: '耗材管理', children: [
    { id: 21, name: '耗材查看' },
    { id: 22, name: '耗材入库' },
    { id: 23, name: '耗材出库' },
    { id: 24, name: '耗材删除' }
  ]},
  { id: 3, name: '采购管理', children: [
    { id: 31, name: '采购申请' },
    { id: 32, name: '采购审批' },
    { id: 33, name: '供应商管理' }
  ]},
  { id: 4, name: '盘点管理', children: [
    { id: 41, name: '盘点任务查看' },
    { id: 42, name: '盘点任务创建' },
    { id: 43, name: '盘点执行' }
  ]},
  { id: 5, name: '报表管理', children: [
    { id: 51, name: '报表查看' },
    { id: 52, name: '报表导出' }
  ]},
  { id: 6, name: '财务管理', children: [
    { id: 61, name: '折旧方案管理' },
    { id: 62, name: '财务台账查看' },
    { id: 63, name: '财务台账导出' }
  ]},
  { id: 7, name: '系统设置', children: [
    { id: 71, name: '组织管理' },
    { id: 72, name: '权限管理' },
    { id: 73, name: '系统配置' },
    { id: 74, name: 'SSO配置' },
    { id: 75, name: '审批流配置' }
  ]}
])

// 角色弹窗
const roleDialogVisible = ref(false)
const roleDialogTitle = ref('添加角色')
const roleForm = reactive({
  id: null,
  name: '',
  code: '',
  description: ''
})

const roleRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色代码', trigger: 'blur' }]
}

// 成员弹窗
const memberDialogVisible = ref(false)
const selectedMembers = ref([])
const availableMembers = ref([])

// 加载角色列表
async function loadRoles() {
  loadingRoles.value = true
  try {
    const res = await request.get('/auth/roles/')
    roleList.value = extractListData(res)
    
    // 如果没有角色，创建默认角色
    if (roleList.value.length === 0) {
      await createDefaultRoles()
    }
  } catch (error) {
    console.error('加载角色失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    loadingRoles.value = false
  }
}

// 创建默认角色
async function createDefaultRoles() {
  const defaultRoles = [
    { name: '超级管理员', code: 'super_admin', description: '拥有所有权限', is_system: true },
    { name: '资产管理员', code: 'asset_admin', description: '管理资产相关功能' },
    { name: '部门管理员', code: 'dept_admin', description: '管理本部门资产' },
    { name: '普通员工', code: 'employee', description: '基础查看和申请权限' }
  ]
  
  for (const role of defaultRoles) {
    try {
      await request.post('/auth/roles/', role)
    } catch (e) {
      // 忽略重复创建错误
    }
  }
  
  // 重新加载
  const res = await request.get('/auth/roles/')
  roleList.value = extractListData(res)
}

// 加载部门树
async function loadDeptTree() {
  try {
    const res = await request.get('/organizations/departments/tree/')
    deptTree.value = res || []
  } catch (error) {
    console.error('加载部门树失败:', error)
  }
}

// 加载角色成员
async function loadRoleMembers(roleId) {
  loadingMembers.value = true
  try {
    const res = await request.get(`/auth/roles/${roleId}/members/`)
    roleMembers.value = res || []
  } catch (error) {
    console.error('加载角色成员失败:', error)
    roleMembers.value = []
  } finally {
    loadingMembers.value = false
  }
}

// 加载可选员工
async function loadAvailableMembers() {
  try {
    // 获取所有用户，不分页（设置较大的page_size）
    const res = await request.get('/auth/users/', {
      params: { page_size: 9999 }
    })
    const users = extractListData(res)
    
    // 排除已经是该角色成员的用户
    const existingIds = new Set(roleMembers.value.map(m => m.id))
    
    availableMembers.value = users
      .filter(u => !existingIds.has(u.id))
      .map(u => ({
        id: u.id,
        label: `${u.display_name || u.username} - ${u.department_name || u.department?.name || '未分配部门'}`
      }))
  } catch (error) {
    console.error('加载可选员工失败:', error)
    availableMembers.value = []
  }
}

// 选择角色
function selectRole(role) {
  currentRole.value = role
  
  // 加载角色权限
  if (role.permissions) {
    checkedPermissions.value = role.permissions.function_permissions || []
    dataScope.value = role.permissions.data_scope || 'all'
    customDepts.value = role.permissions.custom_depts || []
  } else {
    // 默认权限
    if (role.code === 'super_admin') {
      checkedPermissions.value = getAllPermissionIds()
      dataScope.value = 'all'
    } else if (role.code === 'asset_admin') {
      checkedPermissions.value = [11, 12, 13, 14, 15, 16, 17, 18, 19, 41, 42, 43, 51, 52]
      dataScope.value = 'all'
    } else if (role.code === 'dept_admin') {
      checkedPermissions.value = [11, 12, 13, 16, 17, 18, 21, 22, 23, 41, 43, 51]
      dataScope.value = 'dept_below'
    } else {
      checkedPermissions.value = [11, 21, 51]
      dataScope.value = 'self'
    }
    customDepts.value = []
  }
  
  // 设置选中的权限节点
  setTimeout(() => {
    permissionTreeRef.value?.setCheckedKeys(checkedPermissions.value)
  }, 0)
  
  // 加载成员
  loadRoleMembers(role.id)
}

// 获取所有权限ID
function getAllPermissionIds() {
  const ids = []
  permissionTree.value.forEach(parent => {
    if (parent.children) {
      parent.children.forEach(child => ids.push(child.id))
    }
  })
  return ids
}

function handleAddRole() {
  roleDialogTitle.value = '添加角色'
  Object.assign(roleForm, { id: null, name: '', code: '', description: '' })
  roleDialogVisible.value = true
}

function handleEditRole() {
  if (!currentRole.value || currentRole.value.is_system) return
  roleDialogTitle.value = '编辑角色'
  Object.assign(roleForm, {
    id: currentRole.value.id,
    name: currentRole.value.name,
    code: currentRole.value.code,
    description: currentRole.value.description
  })
  roleDialogVisible.value = true
}

async function saveRole() {
  const valid = await roleFormRef.value?.validate()
  if (!valid) return
  
  savingRole.value = true
  try {
    if (roleForm.id) {
      await request.put(`/auth/roles/${roleForm.id}/`, {
        name: roleForm.name,
        code: roleForm.code,
        description: roleForm.description
      })
      ElMessage.success('角色编辑成功')
    } else {
      await request.post('/auth/roles/', {
        name: roleForm.name,
        code: roleForm.code,
        description: roleForm.description
      })
      ElMessage.success('角色添加成功')
    }
    roleDialogVisible.value = false
    await loadRoles()
  } catch (error) {
    ElMessage.error('保存角色失败: ' + (error.response?.data?.error || error.message))
  } finally {
    savingRole.value = false
  }
}

async function handleSave() {
  if (!currentRole.value) return
  
  const checkedKeys = permissionTreeRef.value?.getCheckedKeys() || []
  
  const permissions = {
    function_permissions: checkedKeys,
    data_scope: dataScope.value,
    custom_depts: dataScope.value === 'custom' ? customDepts.value : []
  }
  
  try {
    await request.patch(`/auth/roles/${currentRole.value.id}/`, {
      permissions: permissions
    })
    ElMessage.success('权限保存成功')
    
    // 更新本地缓存
    currentRole.value.permissions = permissions
    const index = roleList.value.findIndex(r => r.id === currentRole.value.id)
    if (index !== -1) {
      roleList.value[index].permissions = permissions
    }
  } catch (error) {
    ElMessage.error('保存权限失败: ' + (error.response?.data?.error || error.message))
  }
}

async function handleAddMember() {
  if (!currentRole.value) return
  await loadAvailableMembers()
  selectedMembers.value = []
  memberDialogVisible.value = true
}

async function confirmAddMembers() {
  if (selectedMembers.value.length === 0) {
    ElMessage.warning('请选择要添加的成员')
    return
  }
  
  addingMembers.value = true
  try {
    const res = await request.post(`/auth/roles/${currentRole.value.id}/add_members/`, {
      user_ids: selectedMembers.value
    })
    ElMessage.success(res.message || '成员添加成功')
    memberDialogVisible.value = false
    
    // 重新加载成员和角色列表
    await loadRoleMembers(currentRole.value.id)
    await loadRoles()
  } catch (error) {
    ElMessage.error('添加成员失败: ' + (error.response?.data?.error || error.message))
  } finally {
    addingMembers.value = false
  }
}

async function handleRemoveMember(row) {
  try {
    await ElMessageBox.confirm(`确定要移除成员 "${row.name}" 吗？`, '移除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.post(`/auth/roles/${currentRole.value.id}/remove_member/`, {
      user_id: row.id
    })
    
    ElMessage.success('成员已移除')
    
    // 重新加载成员和角色列表
    await loadRoleMembers(currentRole.value.id)
    await loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除成员失败: ' + (error.response?.data?.error || error.message))
    }
  }
}

// 同步角色
async function handleSyncRoles() {
  try {
    await ElMessageBox.confirm(
      '同步角色将根据以下规则自动分配角色：\n' +
      '• 所有活跃用户分配"普通员工"角色\n' +
      '• 部门负责人分配"部门管理员"角色\n' +
      '• 超级管理员用户分配"超级管理员"角色\n\n' +
      '确定要同步吗？',
      '同步角色确认',
      {
        confirmButtonText: '确定同步',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    syncingRoles.value = true
    const loading = ElLoading.service({
      lock: true,
      text: '正在同步角色...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    try {
      const res = await request.post('/auth/roles/sync_roles/')
      
      const stats = res.stats || {}
      ElMessage.success(
        `同步完成！共处理 ${stats.total_users || 0} 名用户，` +
        `新分配普通员工 ${stats.employee_assigned || 0} 人，` +
        `部门管理员 ${stats.dept_admin_assigned || 0} 人，` +
        `超级管理员 ${stats.super_admin_assigned || 0} 人`
      )
      
      // 重新加载角色列表
      await loadRoles()
      
      // 如果有选中的角色，重新加载成员
      if (currentRole.value) {
        await loadRoleMembers(currentRole.value.id)
      }
    } finally {
      loading.close()
      syncingRoles.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('同步失败: ' + (error.response?.data?.error || error.message))
    }
  }
}

onMounted(async () => {
  await Promise.all([loadRoles(), loadDeptTree()])
  
  // 默认选中第一个角色
  if (roleList.value.length > 0) {
    selectRole(roleList.value[0])
  }
})
</script>

<style lang="scss" scoped>
.permissions-container {
  .action-card {
    border-radius: 12px;
    
    .action-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .action-info {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #666;
        
        .el-icon {
          color: #409eff;
          font-size: 18px;
        }
      }
      
      .action-buttons {
        display: flex;
        gap: 12px;
      }
    }
  }
  
  .role-card, .permission-card { border-radius: 16px; min-height: calc(100vh - 260px); }
  .card-header { display: flex; justify-content: space-between; align-items: center; }
  .role-list {
    .role-item {
      display: flex; justify-content: space-between; align-items: center;
      padding: 12px 16px; border-radius: 8px; cursor: pointer; margin-bottom: 8px;
      background: #f9fafb; transition: all 0.2s;
      &:hover, &.active { background: #eff6ff; border-left: 3px solid #3b82f6; }
      .role-info { 
        .role-name { font-weight: 500; display: flex; align-items: center; } 
        .role-desc { font-size: 12px; color: #9ca3af; margin-top: 4px; } 
      }
    }
  }
  
  :deep(.el-transfer) {
    .el-transfer-panel {
      width: 280px;
      height: 400px;
      
      .el-transfer-panel__body {
        height: calc(100% - 40px);
      }
      
      .el-transfer-panel__list {
        height: calc(100% - 40px);
        overflow: auto;
      }
    }
  }
}
</style>
