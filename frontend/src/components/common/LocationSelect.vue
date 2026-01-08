<template>
  <el-tree-select
    v-model="selectedValue"
    :data="locationTree"
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
    default: '请选择存放位置'
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
const locationTree = ref([])

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
  loadLocationTree()
})

// 加载位置树
async function loadLocationTree() {
  try {
    const params = {}
    if (props.companyId) {
      params.company = props.companyId
    }
    const res = await request.get('/organizations/locations/tree/', { params })
    locationTree.value = res || []
  } catch (error) {
    console.error('加载位置树失败:', error)
    locationTree.value = []
  }
}

// 选择变化
function handleChange(val) {
  emit('update:modelValue', val)
  emit('change', val)
}

onMounted(() => {
  loadLocationTree()
})
</script>
