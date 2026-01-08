<template>
  <div class="image-upload-container">
    <el-upload
      ref="uploadRef"
      class="image-uploader"
      :class="{ 'has-image': imageUrl }"
      :action="uploadAction"
      :headers="uploadHeaders"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :disabled="disabled"
      accept="image/*"
    >
      <div v-if="imageUrl" class="image-preview">
        <el-image :src="imageUrl" fit="cover" />
        <div class="image-actions" v-if="!disabled">
          <el-icon class="action-icon" @click.stop="handlePreview"><ZoomIn /></el-icon>
          <el-icon class="action-icon" @click.stop="handleRemove"><Delete /></el-icon>
        </div>
      </div>
      <div v-else class="upload-placeholder">
        <el-icon class="upload-icon"><Plus /></el-icon>
        <span class="upload-text">{{ placeholder }}</span>
      </div>
    </el-upload>
    
    <!-- 图片预览 -->
    <el-dialog v-model="previewVisible" title="图片预览" width="600px">
      <img :src="imageUrl" style="width: 100%;" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, ZoomIn, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: [String, File],
    default: ''
  },
  placeholder: {
    type: String,
    default: '上传图片'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  maxSize: {
    type: Number,
    default: 5 // MB
  },
  uploadUrl: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const uploadRef = ref(null)
const previewVisible = ref(false)
const localFile = ref(null)
const localPreviewUrl = ref('')

// 上传地址
const uploadAction = computed(() => {
  return props.uploadUrl || '#'
})

// 上传请求头
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

// 图片URL
const imageUrl = computed(() => {
  // 优先显示本地预览
  if (localPreviewUrl.value) {
    return localPreviewUrl.value
  }
  // 显示传入的URL
  if (typeof props.modelValue === 'string' && props.modelValue) {
    // 处理相对路径
    if (props.modelValue.startsWith('http')) {
      return props.modelValue
    }
    return props.modelValue
  }
  return ''
})

// 监听外部值变化
watch(() => props.modelValue, (val) => {
  if (typeof val === 'string') {
    localFile.value = null
    localPreviewUrl.value = ''
  }
})

// 上传前校验
function beforeUpload(file) {
  // 检查文件类型
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  
  // 检查文件大小
  const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize
  if (!isLtMaxSize) {
    ElMessage.error(`图片大小不能超过 ${props.maxSize}MB!`)
    return false
  }
  
  // 如果没有上传URL，直接使用本地预览模式
  if (!props.uploadUrl || props.uploadUrl === '#') {
    // 创建本地预览
    localFile.value = file
    localPreviewUrl.value = URL.createObjectURL(file)
    emit('update:modelValue', file)
    emit('change', file)
    return false // 阻止自动上传
  }
  
  return true
}

// 上传成功
function handleSuccess(response) {
  if (response.url) {
    emit('update:modelValue', response.url)
    emit('change', response.url)
    ElMessage.success('图片上传成功')
  }
}

// 上传失败
function handleError(error) {
  console.error('图片上传失败:', error)
  ElMessage.error('图片上传失败')
}

// 预览图片
function handlePreview() {
  previewVisible.value = true
}

// 移除图片
function handleRemove() {
  localFile.value = null
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
  }
  localPreviewUrl.value = ''
  emit('update:modelValue', '')
  emit('change', '')
}
</script>

<style lang="scss" scoped>
.image-upload-container {
  .image-uploader {
    :deep(.el-upload) {
      width: 148px;
      height: 148px;
      border: 1px dashed #d9d9d9;
      border-radius: 8px;
      cursor: pointer;
      overflow: hidden;
      transition: all 0.3s;
      
      &:hover {
        border-color: var(--el-color-primary);
      }
    }
    
    &.has-image {
      :deep(.el-upload) {
        border: none;
      }
    }
    
    .image-preview {
      position: relative;
      width: 100%;
      height: 100%;
      
      :deep(.el-image) {
        width: 100%;
        height: 100%;
      }
      
      .image-actions {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        opacity: 0;
        transition: opacity 0.3s;
        
        .action-icon {
          font-size: 24px;
          color: #fff;
          cursor: pointer;
          
          &:hover {
            color: var(--el-color-primary);
          }
        }
      }
      
      &:hover .image-actions {
        opacity: 1;
      }
    }
    
    .upload-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      color: #909399;
      
      .upload-icon {
        font-size: 36px;
        margin-bottom: 8px;
      }
      
      .upload-text {
        font-size: 12px;
      }
    }
  }
}
</style>
