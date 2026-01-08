<template>
  <div class="suppliers-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>供应商管理</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增供应商
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="供应商名称">
          <el-input v-model="filterName" placeholder="请输入" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable style="width: 100px">
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredList" style="width: 100%">
        <el-table-column prop="code" label="供应商编号" width="120" />
        <el-table-column prop="name" label="供应商名称" min-width="150" />
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="inactive"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="供应商详情" width="600px">
      <el-descriptions :column="2" border v-if="currentSupplier">
        <el-descriptions-item label="供应商编号">{{ currentSupplier.code }}</el-descriptions-item>
        <el-descriptions-item label="供应商名称">{{ currentSupplier.name }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentSupplier.contact }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentSupplier.phone }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentSupplier.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentSupplier.status === 'active' ? 'success' : 'info'">
            {{ currentSupplier.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ currentSupplier.address }}</el-descriptions-item>
        <el-descriptions-item label="开户银行">{{ currentSupplier.bank || '-' }}</el-descriptions-item>
        <el-descriptions-item label="银行账号">{{ currentSupplier.bankAccount || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentSupplier.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="700px">
      <el-form :model="supplierForm" label-width="100px" ref="formRef" :rules="formRules">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商名称" prop="name">
              <el-input v-model="supplierForm.name" placeholder="请输入供应商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商编号">
              <el-input v-model="supplierForm.code" placeholder="自动生成" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact">
              <el-input v-model="supplierForm.contact" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="supplierForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="supplierForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="supplierForm.status">
                <el-radio label="active">启用</el-radio>
                <el-radio label="inactive">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址">
          <el-input v-model="supplierForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户银行">
              <el-input v-model="supplierForm.bank" placeholder="请输入开户银行" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账号">
              <el-input v-model="supplierForm.bankAccount" placeholder="请输入银行账号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="supplierForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const filterName = ref('')
const filterStatus = ref('')
const formRef = ref(null)

const supplierList = ref([
  { id: 1, code: 'GYS-001', name: '联想科技', contact: '张经理', phone: '13800138001', email: 'zhang@lenovo.com', address: '北京市海淀区中关村大街1号', status: 'active', bank: '中国银行北京分行', bankAccount: '6222****1234' },
  { id: 2, code: 'GYS-002', name: 'Dell中国', contact: '李经理', phone: '13800138002', email: 'li@dell.com', address: '上海市浦东新区张江高科园区', status: 'active', bank: '工商银行上海分行', bankAccount: '6222****5678' },
  { id: 3, code: 'GYS-003', name: 'HP中国', contact: '王经理', phone: '13800138003', email: 'wang@hp.com', address: '北京市朝阳区望京科技园', status: 'active' },
  { id: 4, code: 'GYS-004', name: '华为技术', contact: '赵经理', phone: '13800138004', email: 'zhao@huawei.com', address: '深圳市龙岗区华为基地', status: 'inactive' }
])

const filteredList = computed(() => {
  return supplierList.value.filter(item => {
    const nameMatch = !filterName.value || item.name.includes(filterName.value)
    const statusMatch = !filterStatus.value || item.status === filterStatus.value
    return nameMatch && statusMatch
  })
})

// 查看弹窗
const viewDialogVisible = ref(false)
const currentSupplier = ref(null)

// 表单弹窗
const formDialogVisible = ref(false)
const formDialogTitle = ref('新增供应商')
const supplierForm = reactive({
  id: null,
  code: '',
  name: '',
  contact: '',
  phone: '',
  email: '',
  address: '',
  status: 'active',
  bank: '',
  bankAccount: '',
  remark: ''
})

const formRules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

let idCounter = 100

function handleFilter() {
  ElMessage.success('搜索完成')
}

function handleReset() {
  filterName.value = ''
  filterStatus.value = ''
  ElMessage.success('已重置')
}

function handleView(row) {
  currentSupplier.value = row
  viewDialogVisible.value = true
}

function handleAdd() {
  formDialogTitle.value = '新增供应商'
  const newCode = `GYS-${String(supplierList.value.length + 1).padStart(3, '0')}`
  Object.assign(supplierForm, {
    id: null,
    code: newCode,
    name: '',
    contact: '',
    phone: '',
    email: '',
    address: '',
    status: 'active',
    bank: '',
    bankAccount: '',
    remark: ''
  })
  formDialogVisible.value = true
}

function handleEdit(row) {
  formDialogTitle.value = '编辑供应商'
  Object.assign(supplierForm, {
    id: row.id,
    code: row.code,
    name: row.name,
    contact: row.contact,
    phone: row.phone,
    email: row.email || '',
    address: row.address || '',
    status: row.status,
    bank: row.bank || '',
    bankAccount: row.bankAccount || '',
    remark: row.remark || ''
  })
  formDialogVisible.value = true
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentSupplier.value)
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除供应商 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = supplierList.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      supplierList.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleStatusChange(row) {
  ElMessage.success(`供应商 "${row.name}" 已${row.status === 'active' ? '启用' : '停用'}`)
}

function submitForm() {
  formRef.value?.validate((valid) => {
    if (valid) {
      if (supplierForm.id) {
        // 编辑
        const index = supplierList.value.findIndex(item => item.id === supplierForm.id)
        if (index !== -1) {
          Object.assign(supplierList.value[index], {
            name: supplierForm.name,
            contact: supplierForm.contact,
            phone: supplierForm.phone,
            email: supplierForm.email,
            address: supplierForm.address,
            status: supplierForm.status,
            bank: supplierForm.bank,
            bankAccount: supplierForm.bankAccount,
            remark: supplierForm.remark
          })
        }
        ElMessage.success('编辑成功')
      } else {
        // 新增
        supplierList.value.push({
          id: ++idCounter,
          code: supplierForm.code,
          name: supplierForm.name,
          contact: supplierForm.contact,
          phone: supplierForm.phone,
          email: supplierForm.email,
          address: supplierForm.address,
          status: supplierForm.status,
          bank: supplierForm.bank,
          bankAccount: supplierForm.bankAccount,
          remark: supplierForm.remark
        })
        ElMessage.success('新增成功')
      }
      formDialogVisible.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.suppliers-container {
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
