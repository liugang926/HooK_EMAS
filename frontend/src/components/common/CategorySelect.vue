<template>
  <el-cascader
    v-model="selectedValue"
    :options="categoryTree"
    :props="cascaderProps"
    :placeholder="placeholder"
    :clearable="clearable"
    :disabled="disabled"
    filterable
    @change="handleChange"
    style="width: 100%"
  />
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import request from '@/utils/request'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: '请选择分类'
  },
  clearable: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  checkStrictly: {
    type: Boolean,
    default: true
  },
  companyId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedValue = ref(props.modelValue)
const categoryTree = ref([])

const cascaderProps = {
  value: 'id',
  label: 'name',
  children: 'children',
  checkStrictly: props.checkStrictly,
  emitPath: true
}

// 监听外部值变化
watch(() => props.modelValue, (val) => {
  selectedValue.value = val
})

// 监听公司变化
watch(() => props.companyId, () => {
  loadCategoryTree()
})

// 加载分类树
async function loadCategoryTree() {
  try {
    const params = {}
    if (props.companyId) {
      params.company = props.companyId
    }
    const res = await request.get('/assets/categories/tree/', { params })
    categoryTree.value = transformTree(res || [])
  } catch (error) {
    console.error('加载分类树失败:', error)
    categoryTree.value = []
  }
}

// 转换树结构以适配 cascader
function transformTree(tree) {
  return tree.map(item => ({
    id: item.id,
    name: item.name,
    children: item.children && item.children.length > 0 
      ? transformTree(item.children) 
      : undefined
  }))
}

// 选择变化
function handleChange(val) {
  emit('update:modelValue', val)
  const lastId = val && val.length > 0 ? val[val.length - 1] : null
  emit('change', val, lastId)
}

onMounted(() => {
  loadCategoryTree()
})
</script>
