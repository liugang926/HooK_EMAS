<template>
  <div class="organization-container">
    <el-row :gutter="16">
      <!-- 左侧：组织架构树 -->
      <el-col :span="7">
        <el-card class="tree-card">
          <template #header>
            <div class="card-header">
              <span>组织架构</span>
              <el-button type="primary" link @click="handleAddDept">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
          </template>
          <el-input 
            v-model="searchKey" 
            placeholder="搜索部门或员工" 
            clearable 
            style="margin-bottom: 16px"
            @input="handleSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <!-- 搜索结果：员工列表 -->
          <div v-if="searchKey && searchedEmployees.length > 0" class="search-results">
            <div class="search-section-title">
              <el-icon><User /></el-icon>
              <span>员工搜索结果 ({{ searchedEmployees.length }}人)</span>
            </div>
            <div class="search-employee-list">
              <div 
                v-for="emp in searchedEmployees" 
                :key="emp.id" 
                class="search-employee-item"
                @click="handleSearchEmployeeClick(emp)"
              >
                <el-avatar :size="28" class="emp-avatar">{{ emp.name?.charAt(0) }}</el-avatar>
                <div class="emp-info">
                  <span class="emp-name">{{ emp.name }}</span>
                  <span class="emp-dept">{{ emp.department || '未分配部门' }}</span>
                </div>
              </div>
            </div>
            <el-divider />
            <div class="search-section-title" v-if="filteredDeptTree.length > 0">
              <el-icon><OfficeBuilding /></el-icon>
              <span>部门搜索结果</span>
            </div>
          </div>
          <div class="tree-wrapper">
            <el-tree
              ref="treeRef"
              :data="filteredDeptTree"
              :props="{ label: 'name', children: 'children' }"
              default-expand-all
              highlight-current
              node-key="id"
              @node-click="handleNodeClick"
            >
              <template #default="{ node, data }">
                <div class="tree-node">
                  <div class="node-content">
                    <span class="node-name">{{ node.label }}</span>
                    <span class="node-count">({{ data.employeeCount }}人)</span>
                  </div>
                  <div class="node-actions" @click.stop>
                    <el-dropdown trigger="click" size="small">
                      <el-icon class="more-icon"><More /></el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click="handleEditDept(data)">
                            <el-icon><Edit /></el-icon> 编辑部门
                          </el-dropdown-item>
                          <el-dropdown-item @click="handleSetManager(data)">
                            <el-icon><User /></el-icon> 设置负责人
                          </el-dropdown-item>
                          <el-dropdown-item @click="handleAddSubDept(data)">
                            <el-icon><Plus /></el-icon> 添加子部门
                          </el-dropdown-item>
                          <el-dropdown-item divided @click="handleDeleteDept(data)" style="color: #f56c6c;">
                            <el-icon><Delete /></el-icon> 删除部门
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：部门信息和员工列表 -->
      <el-col :span="17">
        <!-- 部门信息卡片 -->
        <el-card v-if="currentDept" class="dept-info-card">
          <div class="dept-info">
            <div class="dept-header">
              <div class="dept-title">
                <h3>{{ currentDept.name }}</h3>
                <el-tag size="small" type="info">{{ currentDept.employeeCount }}人</el-tag>
              </div>
              <el-button type="primary" link @click="handleEditDept(currentDept)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>
            <div class="dept-detail">
              <div class="detail-item">
                <span class="label">部门编码：</span>
                <span class="value">{{ currentDept.code || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">排序：</span>
                <span class="value">{{ currentDept.sortOrder || 0 }}</span>
              </div>
              <div class="detail-item manager-item">
                <span class="label">部门负责人：</span>
                <div class="manager-info" v-if="currentDept.managerName">
                  <el-avatar :size="28" class="manager-avatar">
                    {{ currentDept.managerName?.charAt(0) }}
                  </el-avatar>
                  <span class="manager-name">{{ currentDept.managerName }}</span>
                  <el-button type="primary" link size="small" @click="handleSetManager(currentDept)">
                    更换
                  </el-button>
                </div>
                <div v-else class="no-manager">
                  <span>暂无负责人</span>
                  <el-button type="primary" link size="small" @click="handleSetManager(currentDept)">
                    <el-icon><Plus /></el-icon> 设置
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 员工列表 -->
        <el-card class="employee-card">
          <template #header>
            <div class="card-header">
              <span>{{ currentDept?.name || '全部' }}员工列表</span>
              <div class="header-actions">
                <el-button @click="handleSync">
                  <el-icon><Refresh /></el-icon>
                  同步组织
                </el-button>
                <el-button type="primary" @click="handleAddEmployee">
                  <el-icon><Plus /></el-icon>
                  添加员工
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="employeeList" 
            style="width: 100%" 
            v-loading="tableLoading"
            table-layout="auto"
          >
            <el-table-column label="姓名" min-width="90">
              <template #default="{ row }">
                <div class="employee-name">
                  <el-avatar :size="22" class="emp-avatar">
                    {{ row.name?.charAt(0) }}
                  </el-avatar>
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="employeeNo" label="工号" width="70" show-overflow-tooltip />
            <el-table-column label="所属部门" min-width="90" show-overflow-tooltip>
              <template #default="{ row }">
                <div class="dept-tags">
                  <el-tag 
                    v-if="row.department" 
                    :type="row.departmentMemberships?.length > 1 ? 'primary' : 'info'"
                    size="small"
                  >
                    {{ row.department }}
                  </el-tag>
                  <el-tooltip 
                    v-if="row.departmentMemberships?.length > 1"
                    placement="top"
                    :content="getOtherDepartmentsTooltip(row)"
                  >
                    <el-tag type="info" size="small" class="more-dept-tag">
                      +{{ row.departmentMemberships.length - 1 }}
                    </el-tag>
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="资产归属" min-width="90" show-overflow-tooltip>
              <template #default="{ row }">
                <el-tag 
                  v-if="row.assetDepartmentName" 
                  type="success" 
                  size="small"
                  effect="plain"
                >
                  {{ row.assetDepartmentName }}
                </el-tag>
                <span v-else class="no-asset-dept">
                  {{ row.department || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="position" label="职位" min-width="90" show-overflow-tooltip />
            <el-table-column prop="phone" label="手机号" width="110" />
            <el-table-column label="操作" width="90" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditEmployee(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteEmployee(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加/编辑部门弹窗 -->
    <el-dialog v-model="deptDialogVisible" :title="deptDialogTitle" width="500px">
      <el-form :model="deptForm" label-width="100px" :rules="deptRules" ref="deptFormRef">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="deptForm.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码">
          <el-input v-model="deptForm.code" placeholder="请输入部门编码" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select
            v-model="deptForm.parentId"
            :data="deptTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择上级部门（留空为顶级部门）"
            check-strictly
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="部门负责人">
          <el-select 
            v-model="deptForm.managerId" 
            placeholder="请选择负责人" 
            clearable 
            filterable
            style="width: 100%"
          >
            <el-option 
              v-for="emp in allEmployees" 
              :key="emp.id" 
              :label="`${emp.name} - ${emp.position || '无职位'}`" 
              :value="emp.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="deptForm.sortOrder" :min="0" :max="9999" />
          <span class="form-tip">数字越小越靠前</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deptDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDept" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 设置部门负责人弹窗 -->
    <el-dialog v-model="managerDialogVisible" title="设置部门负责人" width="500px">
      <div class="manager-dialog-content">
        <div class="current-dept">
          <span class="label">当前部门：</span>
          <span class="value">{{ managerForm.deptName }}</span>
        </div>
        <div class="current-manager" v-if="managerForm.currentManagerName">
          <span class="label">当前负责人：</span>
          <el-tag>{{ managerForm.currentManagerName }}</el-tag>
        </div>
        <el-form label-width="100px" style="margin-top: 20px;">
          <el-form-item label="选择负责人">
            <el-select 
              v-model="managerForm.newManagerId" 
              placeholder="请选择新的负责人" 
              clearable 
              filterable
              style="width: 100%"
            >
              <el-option 
                v-for="emp in deptEmployees" 
                :key="emp.id" 
                :label="`${emp.name} - ${emp.position || '无职位'}`" 
                :value="emp.id"
              >
                <div class="emp-option">
                  <el-avatar :size="24">{{ emp.name?.charAt(0) }}</el-avatar>
                  <span class="emp-name">{{ emp.name }}</span>
                  <span class="emp-position">{{ emp.position || '无职位' }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="managerForm.fromAllEmployees">从全部员工中选择</el-checkbox>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="managerDialogVisible = false">取消</el-button>
        <el-button type="danger" plain @click="removeManager" v-if="managerForm.currentManagerId">
          移除负责人
        </el-button>
        <el-button type="primary" @click="saveManager" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加/编辑员工弹窗 -->
    <el-dialog v-model="employeeDialogVisible" :title="employeeDialogTitle" width="650px">
      <el-form :model="employeeForm" label-width="100px" :rules="employeeRules" ref="employeeFormRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="employeeForm.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" prop="employeeNo">
              <el-input v-model="employeeForm.employeeNo" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="主部门" prop="departmentId">
              <el-tree-select
                v-model="employeeForm.departmentId"
                :data="deptTree"
                :props="{ label: 'name', value: 'id', children: 'children' }"
                placeholder="请选择主部门"
                check-strictly
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位" prop="position">
              <el-input v-model="employeeForm.position" placeholder="请输入职位" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 多部门信息显示 -->
        <el-form-item label="所属部门" v-if="employeeForm.departmentMemberships && employeeForm.departmentMemberships.length > 0">
          <div class="dept-membership-list">
            <el-tag 
              v-for="membership in employeeForm.departmentMemberships" 
              :key="membership.department_id"
              :type="membership.is_primary ? 'primary' : 'info'"
              size="default"
              class="dept-membership-tag"
            >
              {{ membership.department_name }}
              <span v-if="membership.is_primary" class="primary-label">(主)</span>
              <span v-if="membership.is_leader" class="leader-label">[负责人]</span>
            </el-tag>
          </div>
          <div class="form-tip">上述部门从第三方平台同步，无法在此修改</div>
        </el-form-item>
        
        <!-- 资产归属部门 -->
        <el-form-item label="资产归属部门">
          <el-select
            v-model="employeeForm.assetDepartmentId"
            placeholder="请选择资产归属部门"
            clearable
            style="width: 100%"
          >
            <!-- 如果有多部门，显示所有部门供选择 -->
            <el-option 
              v-if="employeeForm.departmentMemberships && employeeForm.departmentMemberships.length > 0"
              v-for="membership in employeeForm.departmentMemberships" 
              :key="membership.department_id" 
              :label="membership.department_name + (membership.is_primary ? ' (主)' : '')"
              :value="membership.department_id"
            />
            <!-- 如果没有多部门信息，至少显示主部门 -->
            <el-option 
              v-else-if="employeeForm.departmentId"
              :label="getDeptNameById(employeeForm.departmentId)"
              :value="employeeForm.departmentId"
            />
          </el-select>
          <div class="form-tip">
            指定该用户资产归属的部门。当用户属于多部门时，默认为主部门，可手动修改。
          </div>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="employeeForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="employeeForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-radio-group v-model="employeeForm.status">
            <el-radio label="active">在职</el-radio>
            <el-radio label="inactive">离职</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="employeeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEmployee" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, Search, Refresh, Edit, Delete, User, More, OfficeBuilding } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import request from '@/utils/request'

const searchKey = ref('')
const currentDept = ref(null)
const treeRef = ref()
const deptFormRef = ref()
const employeeFormRef = ref()
const loading = ref(false)
const tableLoading = ref(false)
const saving = ref(false)

const deptTree = ref([])
const employeeList = ref([])
const allEmployees = ref([])
const searchedEmployees = ref([])  // 搜索到的员工列表
let searchDebounceTimer = null  // 搜索防抖计时器

// 加载部门树
async function loadDepartments() {
  try {
    const res = await request.get('/organizations/departments/tree/')
    deptTree.value = transformDeptTree(res || [])
  } catch (error) {
    console.error('加载部门失败:', error)
    deptTree.value = []
  }
}

// 转换部门树数据格式
function transformDeptTree(departments) {
  return departments.map(dept => ({
    id: dept.id,
    name: dept.name,
    code: dept.code,
    parent: dept.parent,
    sortOrder: dept.sort_order,
    employeeCount: dept.total_employee_count || dept.employee_count || 0,
    directEmployeeCount: dept.employee_count || 0,
    manager: dept.manager,
    managerName: dept.manager_name,
    children: dept.children ? transformDeptTree(dept.children) : []
  }))
}

// 加载员工列表（支持多部门信息）
async function loadEmployees(deptId = null) {
  tableLoading.value = true
  try {
    let url = '/auth/users/'
    if (deptId) {
      url += `?department=${deptId}`
    }
    const res = await request.get(url)
    const users = res.results || res || []
    employeeList.value = users.map(user => ({
      id: user.id,
      name: user.nickname || user.display_name || user.first_name || user.username,
      employeeNo: user.employee_no || '-',
      department: user.department_name || user.department?.name || '-',
      departmentId: user.department?.id || user.department,
      position: user.position || '-',
      phone: user.phone || '-',
      email: user.email || '-',
      status: user.is_active ? 'active' : 'inactive',
      isManager: currentDept.value?.manager === user.id,
      // 多部门支持
      departmentMemberships: user.department_memberships || [],
      allDepartments: user.all_departments || [],
      assetDepartment: user.asset_department,
      assetDepartmentName: user.asset_department_name
    }))
  } catch (error) {
    console.error('加载员工失败:', error)
    employeeList.value = []
  } finally {
    tableLoading.value = false
  }
}

// 获取其他部门的tooltip内容
function getOtherDepartmentsTooltip(row) {
  if (!row.departmentMemberships || row.departmentMemberships.length <= 1) {
    return ''
  }
  const otherDepts = row.departmentMemberships
    .filter(m => !m.is_primary)
    .map(m => m.department_name)
  return `其他部门: ${otherDepts.join(', ')}`
}

// 加载全部员工（用于选择负责人）
async function loadAllEmployees() {
  try {
    const res = await request.get('/auth/users/?page_size=1000')
    const users = res.results || res || []
    allEmployees.value = users.map(user => ({
      id: user.id,
      name: user.nickname || user.display_name || user.first_name || user.username,
      position: user.position || '',
      departmentId: user.department?.id || user.department
    }))
  } catch (error) {
    console.error('加载全部员工失败:', error)
  }
}

// 页面加载时获取数据
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([loadDepartments(), loadAllEmployees()])
    // 默认加载所有员工
    await loadEmployees()
  } finally {
    loading.value = false
  }
})

const filteredDeptTree = computed(() => {
  if (!searchKey.value) return deptTree.value
  const filterNodes = (nodes) => {
    return nodes.filter(node => {
      if (node.name.includes(searchKey.value)) return true
      if (node.children) {
        const filteredChildren = filterNodes(node.children)
        if (filteredChildren.length) {
          node.children = filteredChildren
          return true
        }
      }
      return false
    })
  }
  return filterNodes(JSON.parse(JSON.stringify(deptTree.value)))
})

// 搜索处理（包含员工搜索）
function handleSearch() {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  
  if (!searchKey.value) {
    searchedEmployees.value = []
    return
  }
  
  // 防抖处理
  searchDebounceTimer = setTimeout(async () => {
    await searchEmployees(searchKey.value)
  }, 300)
}

// 搜索员工
async function searchEmployees(keyword) {
  if (!keyword) {
    searchedEmployees.value = []
    return
  }
  
  try {
    const res = await request.get('/auth/users/', {
      params: { search: keyword, page_size: 20 }
    })
    const users = res.results || res || []
    searchedEmployees.value = users.map(user => ({
      id: user.id,
      name: user.nickname || user.display_name || user.first_name || user.username,
      employeeNo: user.employee_no || '-',
      department: user.department_name || '-',
      departmentId: user.department?.id || user.department,
      position: user.position || '-',
      phone: user.phone || '-',
      email: user.email || '-',
      // 多部门信息
      departmentMemberships: user.department_memberships || [],
      allDepartments: user.all_departments || [],
      assetDepartment: user.asset_department,
      assetDepartmentName: user.asset_department_name
    }))
  } catch (error) {
    console.error('搜索员工失败:', error)
    searchedEmployees.value = []
  }
}

// 点击搜索到的员工
function handleSearchEmployeeClick(emp) {
  // 如果员工有部门，选中该部门
  if (emp.departmentId) {
    // 查找部门
    const findDept = (nodes, id) => {
      for (const node of nodes) {
        if (node.id === id) return node
        if (node.children) {
          const found = findDept(node.children, id)
          if (found) return found
        }
      }
      return null
    }
    const dept = findDept(deptTree.value, emp.departmentId)
    if (dept) {
      currentDept.value = dept
      loadEmployees(dept.id)
    }
  }
  
  // 打开编辑弹窗
  handleEditEmployee(emp)
  
  // 清空搜索
  searchKey.value = ''
  searchedEmployees.value = []
}

// 部门下的员工（用于设置负责人）
const deptEmployees = computed(() => {
  if (managerForm.fromAllEmployees) {
    return allEmployees.value
  }
  return employeeList.value
})

// 部门弹窗
const deptDialogVisible = ref(false)
const deptDialogTitle = ref('添加部门')
const deptForm = reactive({
  id: null,
  name: '',
  code: '',
  parentId: null,
  managerId: null,
  sortOrder: 0
})

const deptRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

// 设置负责人弹窗
const managerDialogVisible = ref(false)
const managerForm = reactive({
  deptId: null,
  deptName: '',
  currentManagerId: null,
  currentManagerName: '',
  newManagerId: null,
  fromAllEmployees: false
})

// 员工弹窗
const employeeDialogVisible = ref(false)
const employeeDialogTitle = ref('添加员工')
const employeeForm = reactive({
  id: null,
  name: '',
  employeeNo: '',
  departmentId: null,
  position: '',
  phone: '',
  email: '',
  status: 'active',
  // 多部门支持
  departmentMemberships: [],
  allDepartments: [],
  assetDepartmentId: null
})

const employeeRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  departmentId: [{ required: true, message: '请选择部门', trigger: 'change' }]
}

function handleNodeClick(data) {
  currentDept.value = data
  loadEmployees(data.id)
}

function handleAddDept() {
  deptDialogTitle.value = '添加部门'
  Object.assign(deptForm, { 
    id: null, 
    name: '', 
    code: '',
    parentId: currentDept.value?.id || null, 
    managerId: null, 
    sortOrder: 0 
  })
  deptDialogVisible.value = true
}

function handleEditDept(data) {
  deptDialogTitle.value = '编辑部门'
  Object.assign(deptForm, {
    id: data.id,
    name: data.name,
    code: data.code,
    parentId: data.parent,
    managerId: data.manager,
    sortOrder: data.sortOrder || 0
  })
  deptDialogVisible.value = true
}

function handleAddSubDept(data) {
  deptDialogTitle.value = '添加子部门'
  Object.assign(deptForm, { 
    id: null, 
    name: '', 
    code: '',
    parentId: data.id, 
    managerId: null, 
    sortOrder: 0 
  })
  deptDialogVisible.value = true
}

function handleDeleteDept(data) {
  if (data.children && data.children.length > 0) {
    ElMessage.warning('该部门下有子部门，请先删除子部门')
    return
  }
  if (data.directEmployeeCount > 0) {
    ElMessage.warning('该部门下有员工，请先移除员工')
    return
  }
  
  ElMessageBox.confirm(`确定要删除部门 "${data.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/organizations/departments/${data.id}/`)
      ElMessage.success('删除成功')
      await loadDepartments()
      currentDept.value = null
    } catch (error) {
      ElMessage.error('删除失败: ' + (error.response?.data?.error || error.message))
    }
  }).catch(() => {})
}

function handleSetManager(data) {
  managerForm.deptId = data.id
  managerForm.deptName = data.name
  managerForm.currentManagerId = data.manager
  managerForm.currentManagerName = data.managerName
  managerForm.newManagerId = data.manager
  managerForm.fromAllEmployees = false
  
  // 如果当前部门没有员工列表，先加载
  if (!employeeList.value.length || currentDept.value?.id !== data.id) {
    loadEmployees(data.id)
  }
  
  managerDialogVisible.value = true
}

async function saveDept() {
  const valid = await deptFormRef.value?.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    const data = {
      name: deptForm.name,
      code: deptForm.code,
      parent: deptForm.parentId,
      manager: deptForm.managerId,
      sort_order: deptForm.sortOrder,
      company: 1 // 默认公司
    }
    
    if (deptForm.id) {
      await request.patch(`/organizations/departments/${deptForm.id}/`, data)
      ElMessage.success('部门编辑成功')
    } else {
      await request.post('/organizations/departments/', data)
      ElMessage.success('部门添加成功')
    }
    
    deptDialogVisible.value = false
    await loadDepartments()
    
    // 更新当前选中的部门信息
    if (currentDept.value && deptForm.id === currentDept.value.id) {
      const findDept = (nodes, id) => {
        for (const node of nodes) {
          if (node.id === id) return node
          if (node.children) {
            const found = findDept(node.children, id)
            if (found) return found
          }
        }
        return null
      }
      currentDept.value = findDept(deptTree.value, deptForm.id)
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

async function saveManager() {
  saving.value = true
  try {
    await request.patch(`/organizations/departments/${managerForm.deptId}/`, {
      manager: managerForm.newManagerId
    })
    ElMessage.success('负责人设置成功')
    managerDialogVisible.value = false
    await loadDepartments()
    
    // 更新当前部门信息
    if (currentDept.value && currentDept.value.id === managerForm.deptId) {
      const findDept = (nodes, id) => {
        for (const node of nodes) {
          if (node.id === id) return node
          if (node.children) {
            const found = findDept(node.children, id)
            if (found) return found
          }
        }
        return null
      }
      currentDept.value = findDept(deptTree.value, managerForm.deptId)
      // 重新加载员工列表以更新负责人标记
      loadEmployees(managerForm.deptId)
    }
  } catch (error) {
    ElMessage.error('设置失败: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

async function removeManager() {
  ElMessageBox.confirm('确定要移除该部门的负责人吗？', '移除确认', {
    confirmButtonText: '确定移除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    saving.value = true
    try {
      await request.patch(`/organizations/departments/${managerForm.deptId}/`, {
        manager: null
      })
      ElMessage.success('负责人已移除')
      managerDialogVisible.value = false
      await loadDepartments()
      
      if (currentDept.value && currentDept.value.id === managerForm.deptId) {
        currentDept.value.manager = null
        currentDept.value.managerName = null
        loadEmployees(managerForm.deptId)
      }
    } catch (error) {
      ElMessage.error('移除失败: ' + (error.response?.data?.error || error.message))
    } finally {
      saving.value = false
    }
  }).catch(() => {})
}

function handleAddEmployee() {
  employeeDialogTitle.value = '添加员工'
  Object.assign(employeeForm, {
    id: null,
    name: '',
    employeeNo: '',
    departmentId: currentDept.value?.id || null,
    position: '',
    phone: '',
    email: '',
    status: 'active',
    // 多部门支持
    departmentMemberships: [],
    allDepartments: [],
    assetDepartmentId: currentDept.value?.id || null
  })
  employeeDialogVisible.value = true
}

function handleEditEmployee(row) {
  employeeDialogTitle.value = '编辑员工'
  Object.assign(employeeForm, {
    id: row.id,
    name: row.name,
    employeeNo: row.employeeNo === '-' ? '' : row.employeeNo,
    departmentId: row.departmentId,
    position: row.position === '-' ? '' : row.position,
    phone: row.phone === '-' ? '' : row.phone,
    email: row.email === '-' ? '' : row.email,
    status: row.status,
    // 多部门支持
    departmentMemberships: row.departmentMemberships || [],
    allDepartments: row.allDepartments || [],
    // 资产归属部门：如果已设置则使用，否则默认为主部门
    assetDepartmentId: row.assetDepartment || row.departmentId
  })
  employeeDialogVisible.value = true
}

// 根据部门ID获取部门名称
function getDeptNameById(deptId) {
  if (!deptId) return ''
  const findDept = (nodes, id) => {
    for (const node of nodes) {
      if (node.id === id) return node.name
      if (node.children) {
        const found = findDept(node.children, id)
        if (found) return found
      }
    }
    return ''
  }
  return findDept(deptTree.value, deptId) || `部门#${deptId}`
}

function handleDeleteEmployee(row) {
  ElMessageBox.confirm(`确定要删除员工 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/auth/users/${row.id}/`)
      ElMessage.success('删除成功')
      await loadEmployees(currentDept.value?.id)
      await loadDepartments() // 更新人数
    } catch (error) {
      ElMessage.error('删除失败: ' + (error.response?.data?.error || error.message))
    }
  }).catch(() => {})
}

async function saveEmployee() {
  const valid = await employeeFormRef.value?.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    const data = {
      nickname: employeeForm.name,
      display_name: employeeForm.name,
      employee_no: employeeForm.employeeNo,
      department: employeeForm.departmentId,
      asset_department: employeeForm.assetDepartmentId,
      position: employeeForm.position,
      phone: employeeForm.phone,
      email: employeeForm.email,
      is_active: employeeForm.status === 'active'
    }
    
    if (employeeForm.id) {
      await request.patch(`/auth/users/${employeeForm.id}/`, data)
      ElMessage.success('员工编辑成功')
    } else {
      data.username = `user_${Date.now()}`
      data.password = 'default123'
      await request.post('/auth/users/', data)
      ElMessage.success('员工添加成功')
    }
    
    employeeDialogVisible.value = false
    await loadEmployees(currentDept.value?.id)
    await loadDepartments() // 更新人数
    await loadAllEmployees() // 更新全部员工列表
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

async function handleSync() {
  ElMessageBox.confirm('确定要从SSO同步组织架构吗？同步后会更新部门和人员信息。', '同步确认', {
    confirmButtonText: '确定同步',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    const loadingInstance = ElLoading.service({
      lock: true,
      text: '正在同步组织架构...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    try {
      const res = await request.post('/sso/sync-organization/', {
        provider: 'wework',
        sync_type: 'incremental',
        sync_departments: true,
        sync_users: true,
        sync_managers: true
      })
      ElMessage.success(`同步完成！部门：${res.departments || 0}个，用户：${res.users || 0}人，负责人：${res.managers || 0}人`)
      // 重新加载数据
      await Promise.all([loadDepartments(), loadAllEmployees()])
      if (currentDept.value) {
        loadEmployees(currentDept.value.id)
      } else {
        loadEmployees()
      }
    } catch (error) {
      console.error('同步失败:', error)
      ElMessage.error('同步失败: ' + (error.response?.data?.error || error.message))
    } finally {
      loadingInstance.close()
    }
  }).catch(() => {})
}
</script>

<style lang="scss" scoped>
.organization-container {
  width: 100%;
  min-width: 0;
  overflow: hidden;
  
  :deep(.el-row) {
    flex-wrap: nowrap;
  }
  
  :deep(.el-col) {
    min-width: 0;
  }
  
  .tree-card {
    border-radius: 16px;
    height: calc(100vh - 180px);
  }
  
  .dept-info-card {
    border-radius: 16px;
    margin-bottom: 16px;
  }
  
  .employee-card {
    border-radius: 16px;
    height: calc(100vh - 320px);
    overflow: hidden;
    
    :deep(.el-card__body) {
      padding-top: 0;
      height: 100%;
      overflow: hidden;
    }
    
    :deep(.el-table) {
      height: 100%;
    }
    
    :deep(.el-table__header-wrapper),
    :deep(.el-table__body-wrapper) {
      overflow-x: auto;
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .tree-wrapper {
    height: calc(100vh - 330px);
    overflow-y: auto;
  }
  
  .tree-node {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding-right: 8px;
    
    .node-content {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    
    .node-name {
      font-size: 14px;
    }
    
    .node-count {
      font-size: 12px;
      color: #9ca3af;
    }
    
    .node-actions {
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    &:hover .node-actions {
      opacity: 1;
    }
    
    .more-icon {
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      
      &:hover {
        background: #f0f0f0;
      }
    }
  }
  
  .dept-info {
    .dept-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      .dept-title {
        display: flex;
        align-items: center;
        gap: 12px;
        
        h3 {
          margin: 0;
          font-size: 18px;
        }
      }
    }
    
    .dept-detail {
      display: flex;
      flex-wrap: wrap;
      gap: 24px;
      
      .detail-item {
        display: flex;
        align-items: center;
        
        .label {
          color: #666;
          margin-right: 8px;
        }
        
        .value {
          color: #333;
        }
      }
      
      .manager-item {
        flex: 1;
        min-width: 200px;
        
        .manager-info {
          display: flex;
          align-items: center;
          gap: 8px;
          
          .manager-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
          }
          
          .manager-name {
            font-weight: 500;
          }
        }
        
        .no-manager {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #999;
        }
      }
    }
  }
  
  .employee-name {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .emp-avatar {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: #fff;
      font-size: 12px;
    }
  }
  
  .header-actions {
    display: flex;
    gap: 12px;
  }
  
  .form-tip {
    margin-left: 12px;
    font-size: 12px;
    color: #999;
  }
  
  // 搜索结果样式
  .search-results {
    margin-bottom: 12px;
    
    .search-section-title {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #666;
      margin-bottom: 8px;
      
      .el-icon {
        font-size: 14px;
      }
    }
    
    .search-employee-list {
      max-height: 200px;
      overflow-y: auto;
    }
    
    .search-employee-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.2s;
      
      &:hover {
        background-color: #f5f7fa;
      }
      
      .emp-avatar {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: #fff;
        font-size: 12px;
      }
      
      .emp-info {
        display: flex;
        flex-direction: column;
        
        .emp-name {
          font-size: 14px;
          font-weight: 500;
        }
        
        .emp-dept {
          font-size: 12px;
          color: #999;
        }
      }
    }
  }
  
  // 部门标签样式
  .dept-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    
    .primary-tag {
      font-size: 10px;
      margin-left: 2px;
    }
    
    .more-dept-tag {
      cursor: pointer;
    }
  }
  
  .no-asset-dept {
    color: #999;
    font-size: 12px;
  }
  
  // 部门成员标签
  .dept-membership-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .dept-membership-tag {
      .primary-label {
        margin-left: 4px;
        font-weight: bold;
      }
      
      .leader-label {
        margin-left: 4px;
        color: #e6a23c;
      }
    }
  }
}

.manager-dialog-content {
  .current-dept, .current-manager {
    margin-bottom: 12px;
    
    .label {
      color: #666;
      margin-right: 8px;
    }
    
    .value {
      font-weight: 500;
    }
  }
}

.emp-option {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .emp-name {
    font-weight: 500;
  }
  
  .emp-position {
    color: #999;
    font-size: 12px;
  }
}
</style>
