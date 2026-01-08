<template>
  <div class="supplies-settings-container">
    <el-card class="settings-card">
      <template #header>
        <h2>用品设置</h2>
      </template>
      
      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 用品分类 -->
        <el-tab-pane label="用品分类" name="categories">
          <div class="tab-header">
            <el-button type="primary" @click="handleAddCategory">
              <el-icon><Plus /></el-icon>
              新增分类
            </el-button>
          </div>
          
          <el-table :data="categoryList" row-key="id" default-expand-all v-loading="categoryLoading">
            <el-table-column prop="name" label="分类名称" min-width="200" />
            <el-table-column prop="code" label="分类代码" width="150" />
            <el-table-column prop="description" label="描述" min-width="200" />
            <el-table-column prop="sort_order" label="排序" width="80" />
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleEditCategory(row)">编辑</el-button>
                <el-button type="primary" link @click="handleAddSubCategory(row)">添加子分类</el-button>
                <el-button type="danger" link @click="handleDeleteCategory(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <!-- 编号规则 -->
        <el-tab-pane label="编号规则" name="codeRule">
          <div class="code-rule-section">
            <h3>用品编号规则</h3>
            <el-form :model="codeRuleForm" label-width="100px" class="code-rule-form">
              <el-form-item label="编号前缀">
                <el-input v-model="codeRuleForm.prefix" placeholder="如: BG" style="width: 300px" />
              </el-form-item>
              <el-form-item label="日期格式">
                <el-select v-model="codeRuleForm.date_format" style="width: 300px">
                  <el-option label="年 (YYYY)" value="YYYY" />
                  <el-option label="年月 (YYYYMM)" value="YYYYMM" />
                  <el-option label="年月日 (YYYYMMDD)" value="YYYYMMDD" />
                  <el-option label="无日期" value="" />
                </el-select>
              </el-form-item>
              <el-form-item label="流水号位数">
                <el-input-number v-model="codeRuleForm.serial_length" :min="3" :max="8" />
              </el-form-item>
              <el-form-item label="分隔符">
                <el-input v-model="codeRuleForm.separator" placeholder="如: -" style="width: 100px" />
              </el-form-item>
              <el-form-item label="流水号重置">
                <el-select v-model="codeRuleForm.reset_cycle" style="width: 300px">
                  <el-option label="每天重置" value="daily" />
                  <el-option label="每月重置" value="monthly" />
                  <el-option label="每年重置" value="yearly" />
                  <el-option label="不重置" value="never" />
                </el-select>
                <div class="form-tip">流水号在指定周期后从1开始重新计数</div>
              </el-form-item>
              <el-form-item label="示例">
                <el-tag type="warning" size="large">{{ codeRuleExample }}</el-tag>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveCodeRule" :loading="savingCodeRule">保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <!-- 自定义字段 -->
        <el-tab-pane label="自定义字段" name="customFields">
          <div class="custom-fields-section">
            <el-alert 
              title="自定义字段功能" 
              description="您可以为用品档案添加自定义字段，以满足不同业务场景的需求。" 
              type="info" 
              show-icon 
              :closable="false"
              style="margin-bottom: 20px"
            />
            
            <div class="tab-header">
              <el-button type="primary" @click="handleAddField">
                <el-icon><Plus /></el-icon>
                新增字段
              </el-button>
            </div>
            
            <el-table :data="customFieldsList" v-loading="fieldsLoading" :row-class-name="getFieldRowClass">
              <el-table-column prop="field_name" label="字段名称" width="150">
                <template #default="{ row }">
                  {{ row.field_name }}
                  <el-tag v-if="row.is_system" type="info" size="small" style="margin-left: 4px">系统</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="field_key" label="字段标识" width="150" />
              <el-table-column prop="field_type" label="字段类型" width="120">
                <template #default="{ row }">
                  {{ fieldTypeMap[row.field_type] || row.field_type }}
                </template>
              </el-table-column>
              <el-table-column prop="is_required" label="必填" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_required ? 'danger' : 'info'" size="small">
                    {{ row.is_required ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="sort_order" label="排序" width="80" align="center" />
              <el-table-column prop="is_active" label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-switch v-model="row.is_active" @change="toggleFieldStatus(row)" :disabled="row.is_system" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <template v-if="row.is_system">
                    <span class="text-gray-400">系统字段</span>
                  </template>
                  <template v-else>
                    <el-button type="primary" link @click="handleEditField(row)">编辑</el-button>
                    <el-button type="danger" link @click="handleDeleteField(row)">删除</el-button>
                  </template>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 分类编辑弹窗 -->
    <el-dialog v-model="categoryDialogVisible" :title="categoryDialogTitle" width="500px">
      <el-form :model="categoryForm" label-width="100px" ref="categoryFormRef" :rules="categoryRules">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类代码" prop="code">
          <el-input v-model="categoryForm.code" placeholder="请输入分类代码" />
        </el-form-item>
        <el-form-item label="上级分类" v-if="!categoryForm.parent_id">
          <el-cascader
            v-model="categoryForm.parentPath"
            :options="categoryList"
            :props="{ value: 'id', label: 'name', checkStrictly: true, emitPath: false }"
            placeholder="请选择上级分类（可选）"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="categoryForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="categoryForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCategory" :loading="savingCategory">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 自定义字段弹窗 -->
    <el-dialog v-model="fieldDialogVisible" :title="fieldDialogTitle" width="550px">
      <el-form :model="fieldForm" label-width="100px" ref="fieldFormRef" :rules="fieldRules">
        <el-form-item label="字段名称" prop="field_name">
          <el-input v-model="fieldForm.field_name" placeholder="如: 供应商" />
        </el-form-item>
        <el-form-item label="字段标识" prop="field_key">
          <el-input v-model="fieldForm.field_key" placeholder="如: supplier_name" :disabled="!!fieldForm.id" />
          <div class="form-tip">英文标识，创建后不可修改</div>
        </el-form-item>
        <el-form-item label="字段类型" prop="field_type">
          <el-select v-model="fieldForm.field_type" style="width: 100%">
            <el-option label="单行文本" value="text" />
            <el-option label="多行文本" value="textarea" />
            <el-option label="数字" value="number" />
            <el-option label="日期" value="date" />
            <el-option label="单选" value="select" />
            <el-option label="多选" value="multiselect" />
            <el-option label="开关" value="switch" />
          </el-select>
        </el-form-item>
        <el-form-item label="选项" v-if="['select', 'multiselect'].includes(fieldForm.field_type)">
          <el-input v-model="fieldForm.options_text" type="textarea" :rows="3" placeholder="每行一个选项" />
        </el-form-item>
        <el-form-item label="是否必填">
          <el-switch v-model="fieldForm.is_required" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="fieldForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitField" :loading="savingField">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const activeTab = ref('categories')

// Category management
const categoryLoading = ref(false)
const savingCategory = ref(false)
const categoryList = ref([])
const categoryDialogVisible = ref(false)
const categoryDialogTitle = ref('新增分类')
const categoryFormRef = ref(null)
const categoryForm = reactive({
  id: null,
  name: '',
  code: '',
  parent_id: null,
  parentPath: null,
  sort_order: 0,
  description: '',
  is_active: true
})

const categoryRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入分类代码', trigger: 'blur' }]
}

async function loadCategories() {
  categoryLoading.value = true
  try {
    const res = await request.get('/consumables/categories/tree/', {
      params: { company: appStore.currentCompany?.id }
    })
    categoryList.value = res || []
  } catch (error) {
    // Mock data
    categoryList.value = [
      { id: 1, name: '纸张类', code: 'ZZ', sort_order: 1, is_active: true, children: [] },
      { id: 2, name: '书写工具', code: 'SX', sort_order: 2, is_active: true, children: [] },
      { id: 3, name: '文件管理', code: 'WJ', sort_order: 3, is_active: true, children: [] },
      { id: 4, name: '办公设备耗材', code: 'SB', sort_order: 4, is_active: true, children: [] }
    ]
  } finally {
    categoryLoading.value = false
  }
}

function handleAddCategory() {
  categoryDialogTitle.value = '新增分类'
  Object.assign(categoryForm, {
    id: null,
    name: '',
    code: '',
    parent_id: null,
    parentPath: null,
    sort_order: 0,
    description: '',
    is_active: true
  })
  categoryDialogVisible.value = true
}

function handleAddSubCategory(parent) {
  categoryDialogTitle.value = '新增子分类'
  Object.assign(categoryForm, {
    id: null,
    name: '',
    code: '',
    parent_id: parent.id,
    parentPath: parent.id,
    sort_order: 0,
    description: '',
    is_active: true
  })
  categoryDialogVisible.value = true
}

function handleEditCategory(row) {
  categoryDialogTitle.value = '编辑分类'
  Object.assign(categoryForm, {
    id: row.id,
    name: row.name,
    code: row.code,
    parent_id: row.parent,
    parentPath: row.parent,
    sort_order: row.sort_order || 0,
    description: row.description || '',
    is_active: row.is_active
  })
  categoryDialogVisible.value = true
}

async function handleDeleteCategory(row) {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await request.delete(`/consumables/categories/${row.id}/`)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function submitCategory() {
  if (!categoryFormRef.value) return
  try {
    await categoryFormRef.value.validate()
  } catch { return }
  
  savingCategory.value = true
  try {
    const data = {
      company: appStore.currentCompany?.id,
      name: categoryForm.name,
      code: categoryForm.code,
      parent: categoryForm.parentPath || categoryForm.parent_id || null,
      sort_order: categoryForm.sort_order,
      description: categoryForm.description,
      is_active: categoryForm.is_active
    }
    
    if (categoryForm.id) {
      await request.put(`/consumables/categories/${categoryForm.id}/`, data)
      ElMessage.success('编辑成功')
    } else {
      await request.post('/consumables/categories/', data)
      ElMessage.success('新增成功')
    }
    categoryDialogVisible.value = false
    loadCategories()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingCategory.value = false
  }
}

// Code rule management
const savingCodeRule = ref(false)
const codeRuleForm = reactive({
  prefix: 'BG',
  date_format: 'YYYYMMDD',
  serial_length: 4,
  separator: '',
  reset_cycle: 'daily'
})

const codeRuleExample = computed(() => {
  const now = new Date()
  let dateStr = ''
  if (codeRuleForm.date_format === 'YYYY') {
    dateStr = String(now.getFullYear())
  } else if (codeRuleForm.date_format === 'YYYYMM') {
    dateStr = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}`
  } else if (codeRuleForm.date_format === 'YYYYMMDD') {
    dateStr = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`
  }
  
  const serial = '1'.padStart(codeRuleForm.serial_length, '0')
  const sep = codeRuleForm.separator || ''
  
  return `${codeRuleForm.prefix || ''}${sep}${dateStr}${sep}${serial}`
})

async function loadCodeRule() {
  try {
    const res = await request.get('/system/code-rules/asset_code/', {
      params: { company: appStore.currentCompany?.id, code: 'supply_code' }
    })
    if (res && res.prefix) {
      Object.assign(codeRuleForm, {
        prefix: res.prefix || 'BG',
        date_format: res.date_format || 'YYYYMMDD',
        serial_length: res.serial_length || 4,
        separator: res.separator || '',
        reset_cycle: res.reset_cycle || 'daily'
      })
    }
  } catch (error) {
    // Use defaults
  }
}

async function saveCodeRule() {
  savingCodeRule.value = true
  try {
    await request.post('/system/code-rules/asset_code/', {
      company: appStore.currentCompany?.id,
      code: 'supply_code',
      prefix: codeRuleForm.prefix,
      date_format: codeRuleForm.date_format,
      serial_length: codeRuleForm.serial_length,
      separator: codeRuleForm.separator,
      reset_cycle: codeRuleForm.reset_cycle
    })
    ElMessage.success('编号规则保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingCodeRule.value = false
  }
}

// Custom fields management
const fieldsLoading = ref(false)
const savingField = ref(false)
const customFieldsList = ref([])
const fieldDialogVisible = ref(false)
const fieldDialogTitle = ref('新增字段')
const fieldFormRef = ref(null)
const fieldForm = reactive({
  id: null,
  field_name: '',
  field_key: '',
  field_type: 'text',
  options_text: '',
  is_required: false,
  sort_order: 0
})

const fieldRules = {
  field_name: [{ required: true, message: '请输入字段名称', trigger: 'blur' }],
  field_key: [{ required: true, message: '请输入字段标识', trigger: 'blur' }],
  field_type: [{ required: true, message: '请选择字段类型', trigger: 'change' }]
}

const fieldTypeMap = {
  text: '单行文本',
  textarea: '多行文本',
  number: '数字',
  date: '日期',
  select: '单选',
  multiselect: '多选',
  switch: '开关'
}

// Default system fields for office supplies
const defaultFields = [
  { id: 'sys_1', field_name: '用品名称', field_key: 'name', field_type: 'text', is_required: true, is_system: true, is_active: true, sort_order: 1 },
  { id: 'sys_2', field_name: '用品编码', field_key: 'code', field_type: 'text', is_required: false, is_system: true, is_active: true, sort_order: 2 },
  { id: 'sys_3', field_name: '用品分类', field_key: 'category', field_type: 'select', is_required: false, is_system: true, is_active: true, sort_order: 3 },
  { id: 'sys_4', field_name: '品牌', field_key: 'brand', field_type: 'text', is_required: false, is_system: true, is_active: true, sort_order: 4 },
  { id: 'sys_5', field_name: '规格型号', field_key: 'model', field_type: 'text', is_required: false, is_system: true, is_active: true, sort_order: 5 },
  { id: 'sys_6', field_name: '计量单位', field_key: 'unit', field_type: 'select', is_required: true, is_system: true, is_active: true, sort_order: 6 },
  { id: 'sys_7', field_name: '单价', field_key: 'price', field_type: 'number', is_required: false, is_system: true, is_active: true, sort_order: 7 },
  { id: 'sys_8', field_name: '安全库存', field_key: 'min_stock', field_type: 'number', is_required: false, is_system: true, is_active: true, sort_order: 8 },
  { id: 'sys_9', field_name: '最高库存', field_key: 'max_stock', field_type: 'number', is_required: false, is_system: true, is_active: true, sort_order: 9 },
  { id: 'sys_10', field_name: '描述', field_key: 'description', field_type: 'textarea', is_required: false, is_system: true, is_active: true, sort_order: 10 }
]

async function loadCustomFields() {
  fieldsLoading.value = true
  try {
    const res = await request.get('/system/form/fields/', {
      params: { module: 'supply', company: appStore.currentCompany?.id }
    })
    const apiFields = res.results || res || []
    // Combine default system fields with custom fields from API
    customFieldsList.value = [...defaultFields, ...apiFields.filter(f => !f.is_system)]
  } catch (error) {
    // If API fails, show default fields
    customFieldsList.value = [...defaultFields]
  } finally {
    fieldsLoading.value = false
  }
}

function handleAddField() {
  fieldDialogTitle.value = '新增字段'
  Object.assign(fieldForm, {
    id: null,
    field_name: '',
    field_key: '',
    field_type: 'text',
    options_text: '',
    is_required: false,
    sort_order: customFieldsList.value.length + 1
  })
  fieldDialogVisible.value = true
}

function handleEditField(row) {
  fieldDialogTitle.value = '编辑字段'
  Object.assign(fieldForm, {
    id: row.id,
    field_name: row.field_name,
    field_key: row.field_key,
    field_type: row.field_type,
    options_text: row.options ? row.options.join('\n') : '',
    is_required: row.is_required,
    sort_order: row.sort_order
  })
  fieldDialogVisible.value = true
}

async function handleDeleteField(row) {
  try {
    await ElMessageBox.confirm(`确定要删除字段 "${row.field_name}" 吗？`, '确认删除', { type: 'warning' })
    await request.delete(`/system/form/fields/${row.id}/`)
    ElMessage.success('删除成功')
    loadCustomFields()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function toggleFieldStatus(row) {
  if (row.is_system) return // Don't allow toggling system fields
  try {
    await request.patch(`/system/form/fields/${row.id}/`, { is_active: row.is_active })
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.is_active = !row.is_active
    ElMessage.error('更新失败')
  }
}

function getFieldRowClass({ row }) {
  return row.is_system ? 'system-field-row' : ''
}

async function submitField() {
  if (!fieldFormRef.value) return
  try {
    await fieldFormRef.value.validate()
  } catch { return }
  
  savingField.value = true
  try {
    const data = {
      module: 'supply',
      field_name: fieldForm.field_name,
      field_key: fieldForm.field_key,
      field_type: fieldForm.field_type,
      options: fieldForm.options_text ? fieldForm.options_text.split('\n').filter(Boolean) : [],
      is_required: fieldForm.is_required,
      sort_order: fieldForm.sort_order,
      is_active: true
    }
    
    if (fieldForm.id) {
      await request.put(`/system/form/fields/${fieldForm.id}/`, data)
      ElMessage.success('编辑成功')
    } else {
      await request.post('/system/form/fields/', data)
      ElMessage.success('新增成功')
    }
    fieldDialogVisible.value = false
    loadCustomFields()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingField.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadCodeRule()
  loadCustomFields()
})
</script>

<style lang="scss" scoped>
.supplies-settings-container {
  .settings-card {
    border-radius: 16px;
    
    h2 {
      margin: 0;
      font-size: 18px;
      color: #1f2937;
    }
  }
  
  .tab-header {
    margin-bottom: 16px;
  }
  
  .code-rule-section {
    max-width: 600px;
    
    h3 {
      margin: 0 0 20px;
      font-size: 16px;
      color: #374151;
    }
  }
  
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
  
  .custom-fields-section {
    .tab-header {
      margin-bottom: 16px;
    }
  }
  
  .text-gray-400 {
    color: #9ca3af;
    font-size: 12px;
  }
}

// Global style for system field row (needs to be unscoped for table row styling)
:deep(.system-field-row) {
  background-color: #f9fafb !important;
  
  td {
    color: #6b7280;
  }
}
</style>
