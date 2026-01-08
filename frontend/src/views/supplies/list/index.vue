<template>
  <div class="supplies-list-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>用品档案</h2>
          <div class="header-actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增用品
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="用品名称">
          <el-input v-model="filterForm.name" placeholder="请输入" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="分类">
          <el-cascader
            v-model="filterForm.category"
            :options="categoryOptions"
            :props="{ value: 'id', label: 'name', checkStrictly: true }"
            placeholder="请选择分类"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="suppliesList" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="用品编号" width="120" />
        <el-table-column prop="name" label="用品名称" min-width="150" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="model" label="规格型号" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price" label="单价" width="100">
          <template #default="{ row }">
            ¥ {{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="total_stock" label="库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.total_stock <= row.min_stock ? 'danger' : 'success'">
              {{ row.total_stock || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="min_stock" label="安全库存" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="formDialogVisible" :title="formDialogTitle" width="700px" destroy-on-close>
      <el-form :model="supplyForm" label-width="100px" ref="formRef" :rules="formRules">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用品名称" prop="name">
              <el-input v-model="supplyForm.name" placeholder="请输入用品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用品编号" prop="code">
              <el-input v-model="supplyForm.code" placeholder="留空自动生成">
                <template #append>
                  <el-button @click="generateCode">自动生成</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-cascader
                v-model="supplyForm.categoryPath"
                :options="categoryOptions"
                :props="{ value: 'id', label: 'name', checkStrictly: true, emitPath: true }"
                placeholder="请选择分类"
                style="width: 100%"
                @change="handleCategoryChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="supplyForm.unit" placeholder="请选择单位" style="width: 100%">
                <el-option label="个" value="个" />
                <el-option label="包" value="包" />
                <el-option label="支" value="支" />
                <el-option label="盒" value="盒" />
                <el-option label="箱" value="箱" />
                <el-option label="本" value="本" />
                <el-option label="瓶" value="瓶" />
                <el-option label="卷" value="卷" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="品牌" prop="brand">
              <el-input v-model="supplyForm.brand" placeholder="请输入品牌" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规格型号" prop="model">
              <el-input v-model="supplyForm.model" placeholder="请输入规格型号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">库存与价格</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单价" prop="price">
              <el-input-number v-model="supplyForm.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安全库存" prop="min_stock">
              <el-input-number v-model="supplyForm.min_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最高库存" prop="max_stock">
              <el-input-number v-model="supplyForm.max_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">其他信息</el-divider>
        <el-form-item label="描述">
          <el-input v-model="supplyForm.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="用品详情" width="600px">
      <el-descriptions :column="2" border v-if="currentSupply">
        <el-descriptions-item label="用品编号">{{ currentSupply.code }}</el-descriptions-item>
        <el-descriptions-item label="用品名称">{{ currentSupply.name }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentSupply.category_name }}</el-descriptions-item>
        <el-descriptions-item label="单位">{{ currentSupply.unit }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ currentSupply.brand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="规格型号">{{ currentSupply.model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="单价">¥ {{ currentSupply.price }}</el-descriptions-item>
        <el-descriptions-item label="当前库存">
          <el-tag :type="currentSupply.total_stock <= currentSupply.min_stock ? 'danger' : 'success'">
            {{ currentSupply.total_stock || 0 }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="安全库存">{{ currentSupply.min_stock }}</el-descriptions-item>
        <el-descriptions-item label="最高库存">{{ currentSupply.max_stock }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentSupply.description || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const loading = ref(false)
const submitting = ref(false)

const filterForm = reactive({ name: '', category: null })
const formRef = ref(null)

const suppliesList = ref([])
const categoryOptions = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

// Load supplies list from API
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      company: appStore.currentCompany?.id
    }
    if (filterForm.name) params.search = filterForm.name
    if (filterForm.category) params.category = filterForm.category[filterForm.category.length - 1]
    
    const res = await request.get('/consumables/list/', { params })
    suppliesList.value = res.results || res || []
    pagination.total = res.count || suppliesList.value.length
  } catch (error) {
    console.error('Load supplies failed:', error)
    // Use mock data if API not ready
    suppliesList.value = [
      { id: 1, code: 'BG-0001', name: 'A4打印纸', category_name: '纸张类', unit: '包', price: '25.00', total_stock: 50, min_stock: 20, brand: '得力', model: '500张/包' },
      { id: 2, code: 'BG-0002', name: '签字笔', category_name: '书写工具', unit: '支', price: '3.00', total_stock: 10, min_stock: 50, brand: '晨光', model: '0.5mm黑色' },
      { id: 3, code: 'BG-0003', name: '文件夹', category_name: '文件管理', unit: '个', price: '8.00', total_stock: 100, min_stock: 30, brand: '得力', model: 'A4双夹' }
    ]
  } finally {
    loading.value = false
  }
}

// Load category options
async function loadCategories() {
  try {
    const res = await request.get('/consumables/categories/tree/', { 
      params: { company: appStore.currentCompany?.id } 
    })
    categoryOptions.value = res || []
  } catch (error) {
    // Use default categories if API not ready
    categoryOptions.value = [
      { id: 1, name: '纸张类', children: [] },
      { id: 2, name: '书写工具', children: [] },
      { id: 3, name: '文件管理', children: [] },
      { id: 4, name: '办公设备耗材', children: [] },
      { id: 5, name: '清洁用品', children: [] }
    ]
  }
}

// Form dialog
const formDialogVisible = ref(false)
const formDialogTitle = ref('新增用品')
const supplyForm = reactive({
  id: null,
  code: '',
  name: '',
  category: null,
  categoryPath: [],
  unit: '个',
  brand: '',
  model: '',
  price: 0,
  min_stock: 0,
  max_stock: 0,
  description: ''
})

const formRules = {
  name: [{ required: true, message: '请输入用品名称', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择单位', trigger: 'change' }]
}

// View dialog
const viewDialogVisible = ref(false)
const currentSupply = ref(null)

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  filterForm.name = ''
  filterForm.category = null
  handleSearch()
}

function handleCategoryChange(path) {
  if (path && path.length > 0) {
    supplyForm.category = path[path.length - 1]
  } else {
    supplyForm.category = null
  }
}

// Generate code using API (following asset pattern)
async function generateCode() {
  const companyId = appStore.currentCompany?.id
  if (!companyId) {
    ElMessage.warning('请先选择公司')
    return
  }
  
  try {
    const res = await request.post('/system/code-rules/generate_code/', {
      company: companyId,
      code_type: 'supply_code'
    })
    if (res.code) {
      supplyForm.code = res.code
      ElMessage.success(`已生成编号: ${res.code}`)
    }
  } catch (error) {
    // Fallback to local generation
    const date = new Date()
    const dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
    const random = String(Math.floor(Math.random() * 10000)).padStart(4, '0')
    supplyForm.code = `BG${dateStr}${random}`
  }
}

function handleAdd() {
  formDialogTitle.value = '新增用品'
  Object.assign(supplyForm, {
    id: null,
    code: '',
    name: '',
    category: null,
    categoryPath: [],
    unit: '个',
    brand: '',
    model: '',
    price: 0,
    min_stock: 0,
    max_stock: 0,
    description: ''
  })
  formDialogVisible.value = true
}

function handleView(row) {
  currentSupply.value = row
  viewDialogVisible.value = true
}

function handleEdit(row) {
  formDialogTitle.value = '编辑用品'
  Object.assign(supplyForm, {
    id: row.id,
    code: row.code,
    name: row.name,
    category: row.category,
    categoryPath: row.category ? [row.category] : [],
    unit: row.unit,
    brand: row.brand || '',
    model: row.model || '',
    price: parseFloat(row.price) || 0,
    min_stock: row.min_stock || 0,
    max_stock: row.max_stock || 0,
    description: row.description || ''
  })
  formDialogVisible.value = true
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentSupply.value)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除用品 "${row.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await request.delete(`/consumables/list/${row.id}/`)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function submitForm() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  submitting.value = true
  try {
    const data = {
      company: appStore.currentCompany?.id,
      code: supplyForm.code,
      name: supplyForm.name,
      category: supplyForm.category,
      unit: supplyForm.unit,
      brand: supplyForm.brand,
      model: supplyForm.model,
      price: supplyForm.price,
      min_stock: supplyForm.min_stock,
      max_stock: supplyForm.max_stock,
      description: supplyForm.description
    }
    
    if (supplyForm.id) {
      await request.put(`/consumables/list/${supplyForm.id}/`, data)
      ElMessage.success('编辑成功')
    } else {
      await request.post('/consumables/list/', data)
      ElMessage.success('新增成功')
    }
    formDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
  loadCategories()
})
</script>

<style lang="scss" scoped>
.supplies-list-container {
  .page-card { 
    border-radius: 16px; 
  }
  
  .page-header { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    
    h2 { 
      margin: 0; 
      font-size: 18px; 
      color: #1f2937; 
    }
  }
  
  .filter-form { 
    margin-bottom: 16px; 
  }
  
  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
