<template>
  <div class="membership-container">
    <div class="page-header">
      <h2>用户公司关系管理</h2>
      <p class="description">管理用户与公司的关联关系，包括角色分配、数据权限等</p>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <el-row :gutter="16" justify="space-between">
        <el-col :span="16">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名、昵称或公司名..."
            clearable
            style="width: 300px"
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="filterCompany"
            placeholder="筛选公司"
            clearable
            style="width: 200px; margin-left: 12px"
            @change="loadMemberships"
          >
            <el-option
              v-for="company in companies"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-col>
        <el-col :span="8" style="text-align: right">
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            添加用户公司关系
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- Data Table -->
    <el-table
      v-loading="loading"
      :data="memberships"
      stripe
      border
      style="width: 100%"
    >
      <el-table-column prop="user_name" label="用户" min-width="120">
        <template #default="{ row }">
          <div class="user-info">
            <el-avatar :size="32" :src="row.user_avatar">
              {{ row.user_name?.charAt(0) }}
            </el-avatar>
            <span class="name">{{ row.user_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="company_name" label="公司" min-width="150" />
      <el-table-column prop="is_primary" label="主公司" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_primary ? 'success' : 'info'" size="small">
            {{ row.is_primary ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="roles_detail" label="角色" min-width="180">
        <template #default="{ row }">
          <el-tag
            v-for="role in row.roles_detail"
            :key="role.id"
            size="small"
            style="margin-right: 4px"
          >
            {{ role.name }}
          </el-tag>
          <span v-if="!row.roles_detail?.length" class="no-data">未分配</span>
        </template>
      </el-table-column>
      <el-table-column prop="data_scope" label="数据范围" width="100">
        <template #default="{ row }">
          {{ getDataScopeLabel(row.data_scope) }}
        </template>
      </el-table-column>
      <el-table-column prop="is_admin" label="管理员" width="80" align="center">
        <template #default="{ row }">
          <el-icon v-if="row.is_admin" color="#67c23a"><Check /></el-icon>
          <el-icon v-else color="#909399"><Close /></el-icon>
        </template>
      </el-table-column>
      <el-table-column prop="is_finance_auditor" label="财务审计" width="90" align="center">
        <template #default="{ row }">
          <el-icon v-if="row.is_finance_auditor" color="#67c23a"><Check /></el-icon>
          <el-icon v-else color="#909399"><Close /></el-icon>
        </template>
      </el-table-column>
      <el-table-column prop="effective_date" label="有效期" width="200">
        <template #default="{ row }">
          <span v-if="row.effective_date || row.expiry_date">
            {{ row.effective_date || '不限' }} ~ {{ row.expiry_date || '不限' }}
          </span>
          <span v-else class="no-data">永久有效</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="openEditDialog(row)">
            编辑
          </el-button>
          <el-popconfirm
            title="确定要删除此用户公司关系吗？"
            @confirm="deleteMembership(row.id)"
          >
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadMemberships"
        @current-change="loadMemberships"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户公司关系' : '添加用户公司关系'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户" prop="user" v-if="!isEdit">
          <el-select
            v-model="formData.user"
            filterable
            remote
            :remote-method="searchUsers"
            placeholder="搜索并选择用户"
            style="width: 100%"
            :loading="userSearchLoading"
          >
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.display_name || user.username"
              :value="user.id"
            >
              <div class="user-option">
                <el-avatar :size="24" :src="user.avatar">
                  {{ (user.display_name || user.username)?.charAt(0) }}
                </el-avatar>
                <span>{{ user.display_name || user.username }}</span>
                <span class="dept-info" v-if="user.department_name">
                  {{ user.department_name }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="用户" v-else>
          <el-input :value="editingMembership?.user_name" disabled />
        </el-form-item>
        
        <el-form-item label="公司" prop="company" v-if="!isEdit">
          <el-select
            v-model="formData.company"
            placeholder="选择公司"
            style="width: 100%"
          >
            <el-option
              v-for="company in companies"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="公司" v-else>
          <el-input :value="editingMembership?.company_name" disabled />
        </el-form-item>

        <el-form-item label="是否主公司" prop="is_primary">
          <el-switch v-model="formData.is_primary" />
          <span class="form-tip">设为主公司后，用户默认登录进入该公司</span>
        </el-form-item>

        <el-form-item label="角色" prop="roles">
          <el-select
            v-model="formData.roles"
            multiple
            placeholder="选择角色"
            style="width: 100%"
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="数据范围" prop="data_scope">
          <el-radio-group v-model="formData.data_scope">
            <el-radio value="all">所有数据</el-radio>
            <el-radio value="department">部门数据</el-radio>
            <el-radio value="self">个人数据</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="公司管理员" prop="is_admin">
          <el-switch v-model="formData.is_admin" />
          <span class="form-tip">可管理该公司的所有设置</span>
        </el-form-item>

        <el-form-item label="财务审计员" prop="is_finance_auditor">
          <el-switch v-model="formData.is_finance_auditor" />
          <span class="form-tip">可查看财务相关报表和审计记录</span>
        </el-form-item>

        <el-form-item label="有效期">
          <el-col :span="11">
            <el-date-picker
              v-model="formData.effective_date"
              type="date"
              placeholder="生效日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-col>
          <el-col :span="2" style="text-align: center">~</el-col>
          <el-col :span="11">
            <el-date-picker
              v-model="formData.expiry_date"
              type="date"
              placeholder="失效日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-col>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Check, Close } from '@element-plus/icons-vue'
import request from '@/api/request'

// State
const loading = ref(false)
const memberships = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const filterCompany = ref(null)
const companies = ref([])
const roleOptions = ref([])
const userOptions = ref([])
const userSearchLoading = ref(false)

// Dialog state
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingMembership = ref(null)
const formRef = ref(null)
const submitting = ref(false)

const formData = reactive({
  user: null,
  company: null,
  is_primary: false,
  roles: [],
  data_scope: 'department',
  is_admin: false,
  is_finance_auditor: false,
  effective_date: null,
  expiry_date: null
})

const formRules = {
  user: [{ required: true, message: '请选择用户', trigger: 'change' }],
  company: [{ required: true, message: '请选择公司', trigger: 'change' }]
}

// Methods
const loadMemberships = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      company: filterCompany.value || undefined
    }
    const res = await request.get('/auth/user-company-memberships/', { params })
    memberships.value = res.results || res || []
    total.value = res.count || memberships.value.length
  } catch (error) {
    console.error('Failed to load memberships:', error)
    ElMessage.error('加载用户公司关系失败')
  } finally {
    loading.value = false
  }
}

const loadCompanies = async () => {
  try {
    const res = await request.get('/organizations/companies/')
    companies.value = res.results || res || []
  } catch (error) {
    console.error('Failed to load companies:', error)
  }
}

const loadRoles = async (companyId) => {
  try {
    const params = companyId ? { company: companyId } : {}
    const res = await request.get('/auth/roles/', { params })
    roleOptions.value = res.results || res || []
  } catch (error) {
    console.error('Failed to load roles:', error)
  }
}

const searchUsers = async (query) => {
  if (!query) {
    userOptions.value = []
    return
  }
  userSearchLoading.value = true
  try {
    const res = await request.get('/auth/users/', { params: { search: query } })
    userOptions.value = res.results || res || []
  } catch (error) {
    console.error('Failed to search users:', error)
  } finally {
    userSearchLoading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadMemberships()
}

const getDataScopeLabel = (scope) => {
  const labels = {
    all: '所有数据',
    department: '部门数据',
    self: '个人数据'
  }
  return labels[scope] || scope
}

const openCreateDialog = () => {
  isEdit.value = false
  editingMembership.value = null
  Object.assign(formData, {
    user: null,
    company: null,
    is_primary: false,
    roles: [],
    data_scope: 'department',
    is_admin: false,
    is_finance_auditor: false,
    effective_date: null,
    expiry_date: null
  })
  loadRoles()
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  editingMembership.value = row
  Object.assign(formData, {
    user: row.user,
    company: row.company,
    is_primary: row.is_primary,
    roles: row.roles_detail?.map(r => r.id) || [],
    data_scope: row.data_scope,
    is_admin: row.is_admin,
    is_finance_auditor: row.is_finance_auditor,
    effective_date: row.effective_date,
    expiry_date: row.expiry_date
  })
  loadRoles(row.company)
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true

    const data = {
      ...formData,
      roles: formData.roles
    }

    if (isEdit.value) {
      await request.patch(`/auth/user-company-memberships/${editingMembership.value.id}/`, data)
      ElMessage.success('更新成功')
    } else {
      await request.post('/auth/user-company-memberships/', data)
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    loadMemberships()
  } catch (error) {
    if (error !== false) {
      console.error('Submit failed:', error)
      ElMessage.error(error.response?.data?.msg || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

const deleteMembership = async (id) => {
  try {
    await request.delete(`/auth/user-company-memberships/${id}/`)
    ElMessage.success('删除成功')
    loadMemberships()
  } catch (error) {
    console.error('Delete failed:', error)
    ElMessage.error('删除失败')
  }
}

// Lifecycle
onMounted(() => {
  loadCompanies()
  loadMemberships()
})
</script>

<style scoped>
.membership-container {
  padding: 20px;
  background: var(--el-bg-color);
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.page-header .description {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.toolbar {
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info .name {
  font-weight: 500;
}

.no-data {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.user-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-option .dept-info {
  margin-left: auto;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.form-tip {
  margin-left: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
