<template>
  <el-dialog
    v-model="visible"
    title="批量导入资产"
    width="650px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <!-- Step indicator -->
    <el-steps :active="currentStep" simple class="import-steps">
      <el-step title="上传文件" />
      <el-step title="导入结果" />
    </el-steps>

    <!-- Step 1: Upload file -->
    <div v-show="currentStep === 0" class="step-content">
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          class="upload-area"
          drag
          :auto-upload="false"
          :limit="1"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
        >
          <div class="upload-content">
            <el-icon class="upload-icon" :size="48">
              <UploadFilled />
            </el-icon>
            <div class="upload-text">
              <span class="primary">点击或拖拽文件到此处上传</span>
              <span class="secondary">仅支持 .xlsx、.xls 格式的Excel文件</span>
            </div>
          </div>
        </el-upload>
        
        <div v-if="selectedFile" class="selected-file">
          <el-icon><Document /></el-icon>
          <span class="file-name">{{ selectedFile.name }}</span>
          <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
          <el-button type="danger" link @click="removeFile">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>

      <div class="template-section">
        <div class="template-info">
          <el-icon class="info-icon"><InfoFilled /></el-icon>
          <div class="info-content">
            <p>请先下载导入模板，按照模板格式填写资产数据后再上传</p>
            <p class="hint">模板中包含必填字段说明和示例数据</p>
          </div>
        </div>
        <el-button type="primary" link @click="downloadTemplate" :loading="downloadingTemplate">
          <el-icon><Download /></el-icon>
          下载导入模板
        </el-button>
      </div>

      <el-divider />

      <div class="import-notes">
        <h4>导入说明</h4>
        <ul>
          <li><strong>资产名称</strong> 和 <strong>原值</strong> 为必填字段</li>
          <li>资产编号如不填写，系统将自动生成</li>
          <li>日期格式请使用 YYYY-MM-DD（如：2024-01-15）</li>
          <li>使用部门、使用人等字段请填写系统中已存在的名称</li>
          <li>每次最多可导入 1000 条数据</li>
        </ul>
      </div>
    </div>

    <!-- Step 2: Import result -->
    <div v-show="currentStep === 1" class="step-content">
      <div v-if="importing" class="importing-state">
        <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
        <p>正在导入数据，请稍候...</p>
      </div>

      <div v-else-if="importResult" class="import-result">
        <div :class="['result-summary', importResult.success ? 'success' : 'error']">
          <el-icon :size="64">
            <CircleCheck v-if="importResult.success_count > 0" />
            <CircleClose v-else />
          </el-icon>
          <div class="summary-text">
            <h3 v-if="importResult.success_count > 0">
              成功导入 {{ importResult.success_count }} 条资产
            </h3>
            <h3 v-else>导入失败</h3>
            <p v-if="importResult.error_count > 0" class="error-count">
              {{ importResult.error_count }} 条数据导入失败
            </p>
          </div>
        </div>

        <!-- Error details -->
        <div v-if="importResult.errors && importResult.errors.length > 0" class="error-details">
          <h4>
            <el-icon><WarningFilled /></el-icon>
            错误详情
          </h4>
          <el-table :data="importResult.errors" max-height="250" size="small" border>
            <el-table-column prop="row" label="行号" width="80" align="center" />
            <el-table-column prop="error" label="错误信息" />
          </el-table>
        </div>

        <!-- Successfully imported assets -->
        <div v-if="importResult.created_assets && importResult.created_assets.length > 0" class="success-details">
          <h4>
            <el-icon><SuccessFilled /></el-icon>
            导入成功的资产
          </h4>
          <el-table :data="importResult.created_assets" max-height="200" size="small" border>
            <el-table-column prop="asset_code" label="资产编号" width="150" />
            <el-table-column prop="name" label="资产名称" />
          </el-table>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ currentStep === 1 ? '关闭' : '取消' }}</el-button>
        <el-button
          v-if="currentStep === 0"
          type="primary"
          :disabled="!selectedFile"
          :loading="importing"
          @click="handleImport"
        >
          开始导入
        </el-button>
        <el-button
          v-if="currentStep === 1 && importResult?.error_count > 0"
          type="primary"
          @click="resetToUpload"
        >
          重新上传
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Document,
  Close,
  Download,
  InfoFilled,
  Loading,
  CircleCheck,
  CircleClose,
  WarningFilled,
  SuccessFilled
} from '@element-plus/icons-vue'
import { downloadImportTemplate, importAssets } from '@/api/assets'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// State
const currentStep = ref(0)
const uploadRef = ref()
const selectedFile = ref(null)
const downloading = ref(false)
const downloadingTemplate = ref(false)
const importing = ref(false)
const importResult = ref(null)

// Methods
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function handleFileChange(file) {
  selectedFile.value = file.raw
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件，请先移除已选文件')
}

function removeFile() {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

async function downloadTemplate() {
  downloadingTemplate.value = true
  try {
    const response = await downloadImportTemplate()
    
    // Create download link
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'asset_import_template.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  } finally {
    downloadingTemplate.value = false
  }
}

async function handleImport() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }

  importing.value = true
  currentStep.value = 1

  try {
    const result = await importAssets(selectedFile.value)
    importResult.value = result
    
    if (result.success_count > 0) {
      ElMessage.success(`成功导入 ${result.success_count} 条资产`)
      emit('success')
    } else if (result.error_count > 0) {
      ElMessage.warning('导入完成，但存在错误')
    }
  } catch (error) {
    console.error('导入失败:', error)
    importResult.value = {
      success: false,
      success_count: 0,
      error_count: 1,
      errors: [{ row: '-', error: error.response?.data?.message || error.message || '导入失败' }]
    }
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

function resetToUpload() {
  currentStep.value = 0
  selectedFile.value = null
  importResult.value = null
  uploadRef.value?.clearFiles()
}

function handleClose() {
  visible.value = false
}

function handleClosed() {
  // Reset state when dialog is closed
  currentStep.value = 0
  selectedFile.value = null
  importResult.value = null
  importing.value = false
  uploadRef.value?.clearFiles()
}

// Watch for dialog open to reset state
watch(visible, (val) => {
  if (val) {
    handleClosed()
  }
})
</script>

<style lang="scss" scoped>
.import-steps {
  margin-bottom: 24px;
  
  :deep(.el-step__title) {
    font-size: 14px;
  }
}

.step-content {
  min-height: 300px;
}

.upload-section {
  .upload-area {
    :deep(.el-upload-dragger) {
      padding: 40px 20px;
      border-radius: 12px;
      transition: all 0.3s;
      
      &:hover {
        border-color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-9);
      }
    }
  }
  
  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    
    .upload-icon {
      color: var(--el-color-primary);
    }
    
    .upload-text {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      
      .primary {
        font-size: 16px;
        color: #1f2937;
      }
      
      .secondary {
        font-size: 13px;
        color: #9ca3af;
      }
    }
  }
  
  .selected-file {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    margin-top: 16px;
    background: #f0f9ff;
    border-radius: 8px;
    border: 1px solid #bae6fd;
    
    .el-icon {
      color: var(--el-color-primary);
    }
    
    .file-name {
      font-weight: 500;
      color: #1f2937;
    }
    
    .file-size {
      color: #6b7280;
      font-size: 13px;
    }
  }
}

.template-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin-top: 16px;
  background: #fffbeb;
  border-radius: 8px;
  border: 1px solid #fde68a;
  
  .template-info {
    display: flex;
    gap: 12px;
    
    .info-icon {
      color: #f59e0b;
      font-size: 20px;
      flex-shrink: 0;
      margin-top: 2px;
    }
    
    .info-content {
      p {
        margin: 0;
        font-size: 14px;
        color: #1f2937;
        
        &.hint {
          font-size: 12px;
          color: #6b7280;
          margin-top: 4px;
        }
      }
    }
  }
}

.import-notes {
  h4 {
    margin: 0 0 12px;
    font-size: 14px;
    color: #374151;
  }
  
  ul {
    margin: 0;
    padding-left: 20px;
    
    li {
      margin-bottom: 8px;
      font-size: 13px;
      color: #6b7280;
      line-height: 1.5;
      
      strong {
        color: #1f2937;
      }
    }
  }
}

.importing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  
  .loading-icon {
    color: var(--el-color-primary);
    animation: spin 1s linear infinite;
  }
  
  p {
    margin-top: 16px;
    font-size: 14px;
    color: #6b7280;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.import-result {
  .result-summary {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    
    &.success {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      
      .el-icon {
        color: #22c55e;
      }
    }
    
    &.error {
      background: #fef2f2;
      border: 1px solid #fecaca;
      
      .el-icon {
        color: #ef4444;
      }
    }
    
    .summary-text {
      h3 {
        margin: 0;
        font-size: 18px;
        color: #1f2937;
      }
      
      .error-count {
        margin: 4px 0 0;
        font-size: 14px;
        color: #ef4444;
      }
    }
  }
  
  .error-details,
  .success-details {
    margin-top: 16px;
    
    h4 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 12px;
      font-size: 14px;
      color: #374151;
    }
  }
  
  .error-details {
    h4 .el-icon {
      color: #f59e0b;
    }
  }
  
  .success-details {
    h4 .el-icon {
      color: #22c55e;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
