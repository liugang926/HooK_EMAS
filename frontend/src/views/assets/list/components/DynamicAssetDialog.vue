<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    :width="width"
    :destroy-on-close="true"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <DynamicForm
      ref="formRef"
      :config="formConfig"
      :layout="formLayout"
      :initial-data="initialData"
      :mode="mode"
      :loading="loading"
      @change="handleFormChange"
    />

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ mode === 'create' ? '创建' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import DynamicForm from '@/components/dynamic-form/DynamicForm.vue'
import request from '@/utils/request'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  // 模式: create | edit
  mode: {
    type: String,
    default: 'create'
  },
  // 编辑时传入的资产数据
  assetData: {
    type: Object,
    default: null
  },
  // 弹窗宽度
  width: {
    type: String,
    default: '900px'
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

// 状态
const formRef = ref()
const loading = ref(false)
const submitting = ref(false)
const formConfig = ref({ groups: [], ungroupedFields: [] })
const formLayout = ref({ rows: [], groups: [] })

// 可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 对话框标题
const dialogTitle = computed(() => {
  return props.mode === 'create' ? '新增资产' : '编辑资产'
})

// 初始数据
const initialData = computed(() => {
  if (props.mode === 'edit' && props.assetData) {
    return { ...props.assetData }
  }
  return {
    status: 'idle' // 默认状态
  }
})

// 加载表单配置
async function loadFormConfig() {
  loading.value = true
  try {
    // 从 Module Registry 获取字段配置
    const fieldsRes = await request.get('/api/system/registry/asset/fields/', {
      params: { mode: props.mode }
    })
    
    // 转换为 formConfig 格式
    const fields = fieldsRes || []
    formConfig.value = {
      groups: [],
      ungroupedFields: fields.map(field => ({
        key: field.key,
        label: field.label,
        type: field.type,
        required: field.required,
        readonly: field.readonly,
        placeholder: field.placeholder,
        helpText: field.helpText,
        width: field.width || 12,
        options: field.options,
        referenceConfig: field.referenceConfig,
        numberConfig: field.numberConfig,
        formulaConfig: field.formulaConfig,
        rules: field.rules || []
      }))
    }
    
    // 尝试加载自定义布局
    try {
      const layoutRes = await request.get('/api/system/form/layouts/for_module/', {
        params: { module: 'asset', type: 'form' }
      })
      if (layoutRes?.layout && (layoutRes.layout.rows?.length || layoutRes.layout.groups?.length)) {
        formLayout.value = layoutRes.layout
      }
    } catch (layoutError) {
      // 没有自定义布局，使用默认
      console.log('使用默认布局')
    }
    
  } catch (error) {
    console.error('加载表单配置失败:', error)
    ElMessage.error('加载表单配置失败')
  } finally {
    loading.value = false
  }
}

// 处理表单变化
function handleFormChange(formData) {
  // 可用于实时验证或公式计算
}

// 关闭对话框
function handleClose() {
  visible.value = false
}

// 提交表单
async function handleSubmit() {
  try {
    // 验证表单
    await formRef.value?.validate()
    
    const formData = formRef.value?.getFormData()
    if (!formData) return
    
    submitting.value = true
    
    if (props.mode === 'create') {
      // 创建资产
      await request.post('/api/assets/list/', formData)
      ElMessage.success('资产创建成功')
    } else {
      // 更新资产
      await request.put(`/api/assets/list/${props.assetData.id}/`, formData)
      ElMessage.success('资产更新成功')
    }
    
    emit('success')
    handleClose()
    
  } catch (error) {
    if (error !== false) { // 非验证错误
      console.error('提交失败:', error)
      ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  } finally {
    submitting.value = false
  }
}

// 监听弹窗打开
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      loadFormConfig()
    }
  },
  { immediate: true }
)
</script>

<style lang="scss" scoped>
:deep(.el-dialog__body) {
  padding: 20px 24px;
  max-height: 70vh;
  overflow-y: auto;
}
</style>
