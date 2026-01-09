<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    :label-width="config.labelWidth || '100px'"
    :disabled="loading"
    v-loading="loading"
  >
    <!-- 无布局配置时：按字段分组渲染 -->
    <template v-if="!hasCustomLayout">
      <!-- 分组字段 -->
      <template v-for="group in config.groups" :key="group.key">
        <el-collapse v-if="group.collapsible" v-model="activeGroups">
          <el-collapse-item :title="group.name" :name="group.key">
            <el-row :gutter="16">
              <el-col
                v-for="field in group.fields"
                :key="field.key"
                :span="field.width || 8"
              >
                <DynamicField
                  :field="field"
                  v-model="formData[field.key]"
                  :form-data="formData"
                  @change="handleFieldChange"
                />
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>
        
        <div v-else class="form-group">
          <div class="group-title">{{ group.name }}</div>
          <el-row :gutter="16">
            <el-col
              v-for="field in group.fields"
              :key="field.key"
              :span="field.width || 8"
            >
              <DynamicField
                :field="field"
                v-model="formData[field.key]"
                :form-data="formData"
                @change="handleFieldChange"
              />
            </el-col>
          </el-row>
        </div>
      </template>
      
      <!-- 未分组字段 -->
      <el-row v-if="config.ungroupedFields?.length" :gutter="16">
        <el-col
          v-for="field in config.ungroupedFields"
          :key="field.key"
          :span="field.width || 8"
        >
          <DynamicField
            :field="field"
            v-model="formData[field.key]"
            :form-data="formData"
            @change="handleFieldChange"
          />
        </el-col>
      </el-row>
    </template>

    <!-- 有自定义布局配置时：按布局渲染 -->
    <template v-else>
      <!-- 分组布局 -->
      <template v-for="group in layout.groups" :key="group.id">
        <div class="form-group">
          <div class="group-title">{{ group.title }}</div>
          <template v-for="row in group.rows" :key="row.id">
            <el-row :gutter="16">
              <el-col
                v-for="col in row.cols"
                :key="col.field"
                :span="col.span || 12"
              >
                <DynamicField
                  v-if="getFieldConfig(col.field)"
                  :field="getFieldConfig(col.field)"
                  v-model="formData[col.field]"
                  :form-data="formData"
                  @change="handleFieldChange"
                />
              </el-col>
            </el-row>
          </template>
        </div>
      </template>
      
      <!-- 行布局 -->
      <template v-for="row in layout.rows" :key="row.id">
        <el-row :gutter="16">
          <el-col
            v-for="col in row.cols"
            :key="col.field"
            :span="col.span || 12"
          >
            <DynamicField
              v-if="getFieldConfig(col.field)"
              :field="getFieldConfig(col.field)"
              v-model="formData[col.field]"
              :form-data="formData"
              @change="handleFieldChange"
            />
          </el-col>
        </el-row>
      </template>
    </template>

    <!-- 表单操作按钮 (可选) -->
    <div v-if="showActions" class="form-actions">
      <slot name="actions">
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ submitText }}
        </el-button>
      </slot>
    </div>
  </el-form>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import DynamicField from './DynamicField.vue'

const props = defineProps({
  // 模块配置 (来自 API)
  config: {
    type: Object,
    required: true,
    default: () => ({
      groups: [],
      ungroupedFields: []
    })
  },
  // 自定义布局配置
  layout: {
    type: Object,
    default: () => ({
      rows: [],
      groups: []
    })
  },
  // 初始数据
  initialData: {
    type: Object,
    default: () => ({})
  },
  // 模式: create | edit | view
  mode: {
    type: String,
    default: 'create'
  },
  // 是否显示操作按钮
  showActions: {
    type: Boolean,
    default: false
  },
  // 提交按钮文本
  submitText: {
    type: String,
    default: '保存'
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 提交状态
  submitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'change', 'reset', 'field-change'])

const formRef = ref()
const formData = reactive({})
const activeGroups = ref([])

// 是否有自定义布局
const hasCustomLayout = computed(() => {
  return (props.layout.rows?.length > 0) || (props.layout.groups?.length > 0)
})

// 所有字段配置映射
const fieldConfigMap = computed(() => {
  const map = {}
  
  // 从分组中收集
  for (const group of (props.config.groups || [])) {
    for (const field of (group.fields || [])) {
      map[field.key] = field
    }
  }
  
  // 从未分组字段收集
  for (const field of (props.config.ungroupedFields || [])) {
    map[field.key] = field
  }
  
  return map
})

// 表单验证规则
const formRules = computed(() => {
  const rules = {}
  
  for (const [key, field] of Object.entries(fieldConfigMap.value)) {
    if (field.rules?.length) {
      rules[key] = field.rules
    }
  }
  
  return rules
})

// 获取字段配置
function getFieldConfig(fieldKey) {
  return fieldConfigMap.value[fieldKey]
}

// 监听初始数据
watch(
  () => props.initialData,
  (newData) => {
    Object.assign(formData, newData)
  },
  { immediate: true, deep: true }
)

// 处理字段变化
function handleFieldChange({ field, value }) {
  emit('field-change', { field, value, formData })
  emit('change', formData)
  
  // 触发公式字段重新计算
  recalculateFormulas()
}

// 重新计算公式字段
function recalculateFormulas() {
  for (const [key, field] of Object.entries(fieldConfigMap.value)) {
    if (field.type === 'formula' && field.formulaConfig?.expression) {
      try {
        // 在实际实现中，这会调用后端 API 或使用前端公式引擎
        // 这里简单模拟基本数学运算
        const result = evaluateSimpleExpression(
          field.formulaConfig.expression,
          formData
        )
        formData[key] = result
      } catch (e) {
        console.warn(`公式计算失败 [${key}]:`, e.message)
      }
    }
  }
}

// 简易表达式求值 (仅支持基本数学运算)
function evaluateSimpleExpression(expression, context) {
  // 替换变量
  let expr = expression
  for (const [key, value] of Object.entries(context)) {
    const val = value ?? 0
    expr = expr.replace(new RegExp(`\\b${key}\\b`, 'g'), val)
  }
  
  // 安全求值 (仅允许数字和基本运算符)
  if (!/^[\d\s+\-*/().]+$/.test(expr)) {
    throw new Error('表达式包含不允许的字符')
  }
  
  // eslint-disable-next-line no-eval
  return eval(expr)
}

// 表单验证
async function validate() {
  return formRef.value?.validate()
}

// 获取表单数据
function getFormData() {
  return { ...formData }
}

// 重置表单
function handleReset() {
  formRef.value?.resetFields()
  Object.assign(formData, props.initialData)
  emit('reset')
}

// 提交表单
async function handleSubmit() {
  try {
    await validate()
    emit('submit', getFormData())
  } catch (error) {
    ElMessage.warning('请检查表单填写是否完整')
  }
}

// 暴露方法
defineExpose({
  validate,
  getFormData,
  resetFields: handleReset,
  formRef
})

// 初始化
onMounted(() => {
  // 展开默认分组
  activeGroups.value = props.config.groups
    ?.filter(g => !g.collapsed)
    .map(g => g.key) || []
  
  // 初始计算公式
  recalculateFormulas()
})
</script>

<style lang="scss" scoped>
.form-group {
  margin-bottom: 24px;
  
  .group-title {
    font-size: 16px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ebeef5;
    
    &::before {
      content: '';
      display: inline-block;
      width: 4px;
      height: 16px;
      background: #409eff;
      margin-right: 8px;
      vertical-align: middle;
      border-radius: 2px;
    }
  }
}

.form-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  text-align: right;
}
</style>
