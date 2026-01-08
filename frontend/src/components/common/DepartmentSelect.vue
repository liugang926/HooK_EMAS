<template>
  <el-tree-select
    v-model="selectedValue"
    :data="departmentTree"
    :props="treeProps"
    :placeholder="placeholder"
    :clearable="clearable"
    :disabled="disabled"
    :check-strictly="checkStrictly"
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
    type: [Number, String],
    default: null
  },
  placeholder: {
    type: String,
    default: '请选择部门'
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
const departmentTree = ref([])

const treeProps = {
  value: 'id',
  label: 'name',
  children: 'children'
}

// 监听外部值变化
watch(() => props.modelValue, (val) => {
  selectedValue.value = val
})

// 监听公司变化
watch(() => props.companyId, () => {
  loadDepartmentTree()
})

// 加载部门树
async function loadDepartmentTree() {
  try {
    const params = {}
    if (props.companyId) {
      params.company = props.companyId
    }
    const res = await request.get('/organizations/departments/tree/', { params })
    departmentTree.value = res || []
  } catch (error) {
    console.error('加载部门树失败:', error)
    departmentTree.value = []
  }
}

// 选择变化
function handleChange(val) {
  emit('update:modelValue', val)
  emit('change', val)
}

onMounted(() => {
  loadDepartmentTree()
})
</script>
