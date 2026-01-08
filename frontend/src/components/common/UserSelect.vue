<template>
  <el-select
    v-model="selectedValue"
    :placeholder="placeholder"
    :clearable="clearable"
    :disabled="disabled"
    filterable
    remote
    :remote-method="handleSearch"
    :loading="loading"
    @change="handleChange"
    style="width: 100%"
  >
    <el-option
      v-for="user in userList"
      :key="user.id"
      :label="user.display_name || user.username"
      :value="user.id"
    >
      <div class="user-option">
        <el-avatar :size="24" :src="user.avatar">
          {{ (user.display_name || user.username || '').charAt(0) }}
        </el-avatar>
        <div class="user-info">
          <span class="user-name">{{ user.display_name || user.username }}</span>
          <span class="user-dept" v-if="user.department_name">{{ user.department_name }}</span>
        </div>
      </div>
    </el-option>
  </el-select>
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
    default: '请选择用户'
  },
  clearable: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  departmentId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedValue = ref(props.modelValue)
const userList = ref([])
const loading = ref(false)

// 监听外部值变化
watch(() => props.modelValue, (val) => {
  selectedValue.value = val
  if (val && !userList.value.find(u => u.id === val)) {
    loadUserById(val)
  }
})

// 搜索用户
async function handleSearch(query) {
  if (!query && userList.value.length > 0) return
  
  loading.value = true
  try {
    const params = {
      search: query,
      page_size: 50,
      is_active: true
    }
    if (props.departmentId) {
      params.department = props.departmentId
    }
    const res = await request.get('/auth/users/', { params })
    userList.value = res.results || res
  } catch (error) {
    console.error('搜索用户失败:', error)
  } finally {
    loading.value = false
  }
}

// 根据ID加载用户
async function loadUserById(id) {
  try {
    const res = await request.get(`/auth/users/${id}/`)
    if (res && !userList.value.find(u => u.id === res.id)) {
      userList.value.unshift(res)
    }
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

// 选择变化
function handleChange(val) {
  emit('update:modelValue', val)
  const user = userList.value.find(u => u.id === val)
  emit('change', val, user)
}

// 初始化
onMounted(() => {
  handleSearch('')
  if (props.modelValue) {
    loadUserById(props.modelValue)
  }
})
</script>

<style lang="scss" scoped>
.user-option {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .user-info {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
    
    .user-name {
      font-size: 14px;
      color: #303133;
    }
    
    .user-dept {
      font-size: 12px;
      color: #909399;
    }
  }
}
</style>
