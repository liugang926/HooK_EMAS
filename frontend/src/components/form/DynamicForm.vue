<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    :width="config?.dialogWidth || '900px'"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="validationRules"
      :label-width="config?.labelWidth || '100px'"
      class="dynamic-form"
      @submit.prevent
    >
      <!-- 按分组渲染字段 -->
      <template v-if="config?.groups?.length">
        <template v-for="group in config.groups" :key="group.key">
          <el-divider content-position="left">{{ group.name }}</el-divider>
          
          <el-row :gutter="20">
            <el-col
              v-for="field in group.fields"
              :key="field.key"
              :span="field.width || 8"
            >
              <el-form-item
                :label="field.label"
                :prop="field.key"
                :required="field.required"
              >
                <FieldRenderer
                  v-model="formData[field.key]"
                  :field="field"
                  :mode="mode"
                  :disabled="field.readonly"
                  @change="handleFieldChange"
                />
                <div v-if="field.helpText" class="field-help">
                  {{ field.helpText }}
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </template>
      </template>
      
      <!-- 未分组字段 -->
      <template v-if="config?.ungroupedFields?.length">
        <el-row :gutter="20">
          <el-col
            v-for="field in config.ungroupedFields"
            :key="field.key"
            :span="field.width || 8"
          >
            <el-form-item
              :label="field.label"
              :prop="field.key"
              :required="field.required"
            >
              <FieldRenderer
                v-model="formData[field.key]"
                :field="field"
                :mode="mode"
                :disabled="field.readonly"
                @change="handleFieldChange"
              />
              <div v-if="field.helpText" class="field-help">
                {{ field.helpText }}
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
      
      <!-- 无配置时的提示 -->
      <el-empty
        v-if="!loading && !config"
        description="暂无表单配置"
      />
      
      <!-- 加载中 -->
      <div v-if="loading" class="form-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载配置中...</span>
      </div>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        v-if="mode !== 'view'"
        type="primary"
        :loading="submitting"
        @click="handleSubmit"
      >
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import FieldRenderer from './FieldRenderer.vue'
import { useFormConfig } from '@/composables/useFormConfig'

const props = defineProps({
  // 显示控制
  modelValue: {
    type: Boolean,
    default: false
  },
  // 模块名称
  module: {
    type: String,
    required: true
  },
  // 表单模式: create, edit, view
  mode: {
    type: String,
    default: 'create',
    validator: (val) => ['create', 'edit', 'view'].includes(val)
  },
  // 编辑/查看时的数据
  data: {
    type: Object,
    default: null
  },
  // 记录ID（编辑模式）
  recordId: {
    type: [Number, String],
    default: null
  },
  // 自定义标题
  title: {
    type: String,
    default: ''
  },
  // 自定义配置（可选，不传则从API获取）
  customConfig: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success', 'cancel', 'change'])

// 表单配置服务
const {
  formConfig,
  loading,
  loadFormConfig,
  initFormData,
  buildValidationRules,
  submitForm,
  submitFormWithFiles
} = useFormConfig(props.module)

// 组件状态
const formRef = ref(null)
const submitting = ref(false)
const formData = reactive({})

// 显示控制
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 使用的配置（自定义配置优先）
const config = computed(() => props.customConfig || formConfig.value)

// 弹窗标题
const dialogTitle = computed(() => {
  if (props.title) return props.title
  
  const label = config.value?.moduleLabel || props.module
  const modeLabels = {
    create: '新增',
    edit: '编辑',
    view: '查看'
  }
  return `${modeLabels[props.mode]}${label}`
})

// 验证规则
const validationRules = computed(() => {
  return buildValidationRules()
})

// 获取所有文件类型字段
const fileFields = computed(() => {
  if (!config.value) return []
  
  const fields = []
  const allFields = [
    ...(config.value.groups?.flatMap(g => g.fields) || []),
    ...(config.value.ungroupedFields || [])
  ]
  
  allFields.forEach(field => {
    if (field.type === 'image' || field.type === 'file') {
      fields.push(field.key)
    }
  })
  
  return fields
})

// 初始化
async function initialize() {
  // 加载配置
  if (!props.customConfig) {
    await loadFormConfig(props.mode)
  }
  
  // 初始化表单数据
  const initialData = initFormData(props.data)
  Object.keys(formData).forEach(key => delete formData[key])
  Object.assign(formData, initialData)
}

// 监听显示状态
watch(visible, async (val) => {
  if (val) {
    await initialize()
  }
})

// 监听数据变化
watch(() => props.data, (val) => {
  if (visible.value && val) {
    const initialData = initFormData(val)
    Object.assign(formData, initialData)
  }
}, { deep: true })

// 字段变化处理
function handleFieldChange(value, field) {
  emit('change', { field: field.key, value, formData })
  
  // 处理自动填充（如选择用户后自动填充部门）
  if (field.referenceConfig?.autoFillFields) {
    const autoFill = field.referenceConfig.autoFillFields
    Object.entries(autoFill).forEach(([targetField, sourceField]) => {
      // 这里需要根据实际情况获取关联数据
      // 例如：formData[targetField] = value?.department
    })
  }
}

// 关闭弹窗
function handleClose() {
  visible.value = false
  formRef.value?.resetFields()
  emit('cancel')
}

// 提交表单
async function handleSubmit() {
  // 表单验证
  try {
    await formRef.value?.validate()
  } catch (error) {
    return
  }
  
  submitting.value = true
  
  try {
    let result
    
    // 判断是否有文件需要上传
    if (fileFields.value.length > 0) {
      result = await submitFormWithFiles(
        formData,
        props.mode,
        props.recordId,
        fileFields.value
      )
    } else {
      result = await submitForm(
        formData,
        props.mode,
        props.recordId
      )
    }
    
    ElMessage.success(props.mode === 'create' ? '新增成功' : '保存成功')
    emit('success', result)
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

// 暴露方法给父组件
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  getFormData: () => ({ ...formData }),
  setFieldValue: (key, value) => { formData[key] = value },
})
</script>

<style lang="scss" scoped>
.dynamic-form {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 10px;
  
  .el-divider {
    margin: 16px 0;
    
    :deep(.el-divider__text) {
      font-weight: 600;
      color: #303133;
    }
  }
  
  .field-help {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
  }
  
  .form-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
    color: #909399;
    
    .el-icon {
      margin-right: 8px;
      font-size: 20px;
    }
  }
}
</style>
