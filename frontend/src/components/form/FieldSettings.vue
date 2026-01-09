<template>
  <div class="field-settings-container">
    <div class="section-header">
      <h3>{{ title || '自定义字段' }}</h3>
      <el-button type="primary" @click="handleAddField">
        <el-icon><Plus /></el-icon>
        添加字段
      </el-button>
    </div>
    
    <el-table :data="fieldList" v-loading="loading" style="width: 100%">
      <el-table-column prop="field_name" label="字段名称" min-width="150" />
      <el-table-column prop="field_type" label="字段类型" width="120">
        <template #default="{ row }">
          {{ getFieldTypeLabel(row.field_type) }}
        </template>
      </el-table-column>
      <el-table-column label="是否必填" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_required ? 'danger' : 'info'" size="small">
            {{ row.is_required ? '必填' : '选填' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="系统字段" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_system ? 'warning' : ''" size="small">
            {{ row.is_system ? '系统' : '自定义' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="列表显示" width="100" align="center">
        <template #default="{ row }">
          <el-switch 
            v-model="row.show_in_list" 
            :disabled="row.is_system"
            @change="handleToggleListShow(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button 
            type="primary" 
            link 
            size="small" 
            @click="handleEditField(row)" 
            :disabled="row.is_system"
          >
            编辑
          </el-button>
          <el-button 
            type="danger" 
            link 
            size="small" 
            @click="handleDeleteField(row)" 
            :disabled="row.is_system"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- Field Edit Dialog -->
    <el-dialog v-model="fieldDialogVisible" :title="fieldDialogTitle" width="600px">
      <el-form :model="fieldForm" :rules="fieldRules" ref="fieldFormRef" label-width="120px">
        <el-form-item label="字段标识" prop="field_key">
          <el-input 
            v-model="fieldForm.field_key" 
            placeholder="如：custom_field_1"
            :disabled="!!fieldForm.id"
          />
          <div class="form-tip">字段标识创建后不可修改，建议使用英文和下划线</div>
        </el-form-item>
        <el-form-item label="字段名称" prop="field_name">
          <el-input v-model="fieldForm.field_name" placeholder="请输入字段显示名称" />
        </el-form-item>
        <el-form-item label="字段类型" prop="field_type">
          <el-select v-model="fieldForm.field_type" style="width: 100%" @change="handleFieldTypeChange">
            <el-option-group label="基础类型">
              <el-option label="单行文本" value="text" />
              <el-option label="多行文本" value="textarea" />
              <el-option label="数字" value="number" />
              <el-option label="小数" value="decimal" />
              <el-option label="日期" value="date" />
              <el-option label="日期时间" value="datetime" />
              <el-option label="开关" value="switch" />
            </el-option-group>
            <el-option-group label="选择类型">
              <el-option label="下拉选择" value="select" />
              <el-option label="多选" value="multi_select" />
              <el-option label="单选框" value="radio" />
            </el-option-group>
            <el-option-group label="引用类型">
              <el-option label="用户选择" value="reference" />
              <el-option label="树形选择" value="tree_select" />
            </el-option-group>
            <el-option-group label="其他类型">
              <el-option label="图片上传" value="image" />
              <el-option label="文件上传" value="file" />
            </el-option-group>
          </el-select>
        </el-form-item>
        
        <!-- Options Configuration for select types -->
        <el-form-item v-if="['select', 'multi_select', 'radio'].includes(fieldForm.field_type)" label="选项配置">
          <div class="options-editor">
            <div v-for="(opt, idx) in fieldForm.options" :key="idx" class="option-item">
              <el-input v-model="opt.label" placeholder="显示名称" style="width: 45%" />
              <el-input v-model="opt.value" placeholder="选项值" style="width: 45%" />
              <el-button type="danger" link @click="removeOption(idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" link @click="addOption">
              <el-icon><Plus /></el-icon> 添加选项
            </el-button>
          </div>
        </el-form-item>
        
        <!-- Number Configuration -->
        <el-form-item v-if="['number', 'decimal'].includes(fieldForm.field_type)" label="数值范围">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-input-number v-model="fieldForm.number_config.min" placeholder="最小值" style="width: 100%" />
            </el-col>
            <el-col :span="12">
              <el-input-number v-model="fieldForm.number_config.max" placeholder="最大值" style="width: 100%" />
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item v-if="fieldForm.field_type === 'decimal'" label="小数位数">
          <el-input-number v-model="fieldForm.number_config.precision" :min="0" :max="6" />
        </el-form-item>
        
        <el-divider content-position="left">权限设置</el-divider>
        
        <el-form-item label="是否必填">
          <el-switch v-model="fieldForm.is_required" />
        </el-form-item>
        <el-form-item label="始终只读">
          <el-switch v-model="fieldForm.is_readonly" />
        </el-form-item>
        <el-form-item label="新增时隐藏">
          <el-switch v-model="fieldForm.is_hidden_on_create" />
        </el-form-item>
        <el-form-item label="编辑时隐藏">
          <el-switch v-model="fieldForm.is_hidden_on_edit" />
        </el-form-item>
        
        <el-divider content-position="left">显示设置</el-divider>
        
        <el-form-item label="排序">
          <el-input-number v-model="fieldForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="栅格宽度">
          <el-slider v-model="fieldForm.width" :min="4" :max="24" :step="4" show-stops />
          <span class="form-tip">一行最多24格，8表示一行3列</span>
        </el-form-item>
        <el-form-item label="占位提示">
          <el-input v-model="fieldForm.placeholder" placeholder="请输入占位提示文字" />
        </el-form-item>
        <el-form-item label="列表显示">
          <el-switch v-model="fieldForm.show_in_list" />
          <span class="form-tip">是否在列表中显示此字段</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fieldDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitField">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const props = defineProps({
  // Module name (e.g., 'asset', 'supply', 'user')
  module: {
    type: String,
    required: true
  },
  // Section title
  title: {
    type: String,
    default: '自定义字段'
  },
  // Include system fields in the list
  showSystemFields: {
    type: Boolean,
    default: true
  },
  // Default system fields (for frontend display before API returns)
  defaultFields: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['field-saved', 'field-deleted'])

// Field type labels
const fieldTypeMap = {
  text: '单行文本',
  textarea: '多行文本',
  number: '数字',
  decimal: '小数',
  date: '日期',
  datetime: '日期时间',
  select: '下拉选择',
  multi_select: '多选',
  radio: '单选框',
  switch: '开关',
  reference: '用户选择',
  tree_select: '树形选择',
  image: '图片上传',
  file: '文件上传',
  code: '自动编号',
}

function getFieldTypeLabel(type) {
  return fieldTypeMap[type] || type
}

// State
const loading = ref(false)
const submitting = ref(false)
const fieldList = ref([])
const fieldDialogVisible = ref(false)
const fieldDialogTitle = ref('添加字段')
const fieldFormRef = ref(null)

// Default field form
const defaultFieldForm = {
  id: null,
  module: props.module,
  field_key: '',
  field_name: '',
  field_type: 'text',
  sort_order: 0,
  is_required: false,
  is_readonly: false,
  is_hidden_on_create: false,
  is_hidden_on_edit: false,
  options: [],
  number_config: { min: 0, max: 999999, precision: 2 },
  placeholder: '',
  width: 8,
  show_in_list: false,
  is_system: false,
}

const fieldForm = reactive({ ...defaultFieldForm })

const fieldRules = {
  field_key: [
    { required: true, message: '请输入字段标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  field_name: [{ required: true, message: '请输入字段名称', trigger: 'blur' }],
  field_type: [{ required: true, message: '请选择字段类型', trigger: 'change' }],
}

// Load fields
async function loadFields() {
  loading.value = true
  try {
    const res = await request.get('/system/form/fields/', {
      params: { module: props.module }
    })
    const apiFields = res.results || res || []
    
    if (props.showSystemFields && props.defaultFields.length > 0) {
      // Combine default system fields with custom fields from API
      const customFields = apiFields.filter(f => !f.is_system)
      fieldList.value = [...props.defaultFields, ...customFields]
    } else {
      fieldList.value = apiFields
    }
  } catch (error) {
    console.error('Failed to load fields:', error)
    // Fallback to default fields
    if (props.defaultFields.length > 0) {
      fieldList.value = [...props.defaultFields]
    }
  } finally {
    loading.value = false
  }
}

// Handle add field
function handleAddField() {
  fieldDialogTitle.value = '添加字段'
  Object.assign(fieldForm, { 
    ...defaultFieldForm,
    module: props.module,
    options: [],
    number_config: { min: 0, max: 999999, precision: 2 }
  })
  fieldDialogVisible.value = true
}

// Handle edit field
function handleEditField(row) {
  if (row.is_system) {
    ElMessage.warning('系统字段不能编辑')
    return
  }
  fieldDialogTitle.value = '编辑字段'
  Object.assign(fieldForm, {
    ...defaultFieldForm,
    ...row,
    options: row.options || [],
    number_config: row.number_config || { min: 0, max: 999999, precision: 2 }
  })
  fieldDialogVisible.value = true
}

// Handle delete field
async function handleDeleteField(row) {
  if (row.is_system) {
    ElMessage.warning('系统字段不能删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除字段 "${row.field_name}" 吗？`, '删除确认', { type: 'warning' })
    await request.delete(`/system/form/fields/${row.id}/`)
    ElMessage.success('删除成功')
    emit('field-deleted', row)
    loadFields()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// Toggle list show
async function handleToggleListShow(row) {
  if (row.is_system) return
  try {
    await request.patch(`/system/form/fields/${row.id}/`, { show_in_list: row.show_in_list })
  } catch (error) {
    row.show_in_list = !row.show_in_list
    ElMessage.error('更新失败')
  }
}

// Handle field type change
function handleFieldTypeChange(type) {
  if (['select', 'multi_select', 'radio'].includes(type)) {
    if (!fieldForm.options.length) {
      fieldForm.options = [{ label: '', value: '' }]
    }
  } else {
    fieldForm.options = []
  }
}

// Add option
function addOption() {
  fieldForm.options.push({ label: '', value: '' })
}

// Remove option
function removeOption(index) {
  fieldForm.options.splice(index, 1)
}

// Submit field
async function submitField() {
  try {
    await fieldFormRef.value?.validate()
  } catch (error) {
    return
  }
  
  submitting.value = true
  try {
    const data = {
      module: props.module,
      field_key: fieldForm.field_key,
      field_name: fieldForm.field_name,
      field_type: fieldForm.field_type,
      sort_order: fieldForm.sort_order,
      is_required: fieldForm.is_required,
      is_readonly: fieldForm.is_readonly,
      is_hidden_on_create: fieldForm.is_hidden_on_create,
      is_hidden_on_edit: fieldForm.is_hidden_on_edit,
      options: fieldForm.options.filter(o => o.label && o.value),
      number_config: fieldForm.number_config,
      placeholder: fieldForm.placeholder,
      width: fieldForm.width,
      show_in_list: fieldForm.show_in_list,
    }
    
    let result
    if (fieldForm.id) {
      result = await request.put(`/system/form/fields/${fieldForm.id}/`, data)
      ElMessage.success('编辑成功')
    } else {
      result = await request.post('/system/form/fields/', data)
      ElMessage.success('添加成功')
    }
    
    fieldDialogVisible.value = false
    emit('field-saved', result)
    loadFields()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

// Watch for module changes
watch(() => props.module, () => {
  loadFields()
})

// Initialize
onMounted(() => {
  loadFields()
})

// Expose methods
defineExpose({
  loadFields
})
</script>

<style lang="scss" scoped>
.field-settings-container {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      color: #374151;
    }
  }
  
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-left: 8px;
  }
  
  .options-editor {
    width: 100%;
    
    .option-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }
  }
}
</style>
