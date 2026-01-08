<template>
  <component
    :is="fieldComponent"
    v-model="modelValue"
    v-bind="fieldProps"
    @change="handleChange"
  />
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue'

// 基础组件
import {
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElDatePicker,
  ElSwitch,
  ElRadioGroup,
  ElRadio,
  ElCheckboxGroup,
  ElCheckbox,
  ElCascader,
  ElTreeSelect,
} from 'element-plus'

// 异步加载自定义组件
const UserSelect = defineAsyncComponent(() => import('@/components/common/UserSelect.vue'))
const DepartmentSelect = defineAsyncComponent(() => import('@/components/common/DepartmentSelect.vue'))
const LocationSelect = defineAsyncComponent(() => import('@/components/common/LocationSelect.vue'))
const CategorySelect = defineAsyncComponent(() => import('@/components/common/CategorySelect.vue'))
const ImageUpload = defineAsyncComponent(() => import('@/components/common/ImageUpload.vue'))

const props = defineProps({
  // 字段配置
  field: {
    type: Object,
    required: true
  },
  // 双向绑定值
  modelValue: {
    type: [String, Number, Boolean, Array, Object, null],
    default: null
  },
  // 表单模式
  mode: {
    type: String,
    default: 'create',
    validator: (val) => ['create', 'edit', 'view'].includes(val)
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// 双向绑定
const modelValue = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 计算字段是否只读
const isReadonly = computed(() => {
  if (props.disabled) return true
  if (props.field.readonly) return true
  if (props.mode === 'view') return true
  return false
})

// 根据字段类型获取组件
const fieldComponent = computed(() => {
  const type = props.field.type
  const refConfig = props.field.referenceConfig
  
  // 引用类型字段 - 根据配置选择组件
  if (type === 'reference' && refConfig) {
    const api = refConfig.api || ''
    if (api.includes('users') || api.includes('auth')) {
      return UserSelect
    }
    if (api.includes('department')) {
      return DepartmentSelect
    }
    if (api.includes('location')) {
      return LocationSelect
    }
    if (api.includes('categor')) {
      return CategorySelect
    }
    // 默认使用 ElSelect
    return ElSelect
  }
  
  // 树形选择
  if (type === 'tree_select') {
    if (refConfig?.api?.includes('department')) {
      return DepartmentSelect
    }
    if (refConfig?.api?.includes('location')) {
      return LocationSelect
    }
    return ElTreeSelect
  }
  
  // 级联选择
  if (type === 'cascader') {
    if (refConfig?.api?.includes('categor')) {
      return CategorySelect
    }
    return ElCascader
  }
  
  // 基础类型映射
  const componentMap = {
    text: ElInput,
    textarea: ElInput,
    number: ElInputNumber,
    decimal: ElInputNumber,
    date: ElDatePicker,
    datetime: ElDatePicker,
    select: ElSelect,
    multi_select: ElSelect,
    radio: ElRadioGroup,
    checkbox: ElCheckboxGroup,
    switch: ElSwitch,
    image: ImageUpload,
    file: ImageUpload,
    code: ElInput,
    rich_text: ElInput,
  }
  
  return componentMap[type] || ElInput
})

// 计算字段属性
const fieldProps = computed(() => {
  const type = props.field.type
  const baseProps = {
    placeholder: props.field.placeholder || `请输入${props.field.label}`,
    disabled: isReadonly.value,
    style: { width: '100%' }
  }
  
  // 文本框
  if (type === 'text' || type === 'code') {
    return {
      ...baseProps,
      clearable: true,
    }
  }
  
  // 多行文本
  if (type === 'textarea') {
    return {
      ...baseProps,
      type: 'textarea',
      rows: 3,
    }
  }
  
  // 数字
  if (type === 'number' || type === 'decimal') {
    const numConfig = props.field.numberConfig || {}
    return {
      ...baseProps,
      min: numConfig.min ?? 0,
      max: numConfig.max ?? Number.MAX_SAFE_INTEGER,
      precision: type === 'decimal' ? (numConfig.precision ?? 2) : 0,
      step: numConfig.step ?? 1,
      controlsPosition: 'right',
    }
  }
  
  // 日期
  if (type === 'date') {
    return {
      ...baseProps,
      type: 'date',
      valueFormat: 'YYYY-MM-DD',
      placeholder: props.field.placeholder || '请选择日期',
    }
  }
  
  // 日期时间
  if (type === 'datetime') {
    return {
      ...baseProps,
      type: 'datetime',
      valueFormat: 'YYYY-MM-DD HH:mm:ss',
      placeholder: props.field.placeholder || '请选择日期时间',
    }
  }
  
  // 下拉选择
  if (type === 'select') {
    return {
      ...baseProps,
      clearable: true,
      filterable: true,
      placeholder: props.field.placeholder || '请选择',
    }
  }
  
  // 多选
  if (type === 'multi_select') {
    return {
      ...baseProps,
      multiple: true,
      clearable: true,
      filterable: true,
      collapseTags: true,
      placeholder: props.field.placeholder || '请选择',
    }
  }
  
  // 开关
  if (type === 'switch') {
    return {
      disabled: isReadonly.value,
    }
  }
  
  // 引用类型
  if (type === 'reference' || type === 'tree_select') {
    return {
      ...baseProps,
      placeholder: props.field.placeholder || '请选择',
    }
  }
  
  // 图片上传
  if (type === 'image') {
    return {
      disabled: isReadonly.value,
      placeholder: props.field.placeholder || '上传图片',
    }
  }
  
  return baseProps
})

// 处理值变化
function handleChange(val) {
  emit('change', val, props.field)
}
</script>
