<template>
  <el-form-item
    :label="field.label"
    :prop="field.key"
    :rules="field.rules"
    :class="{ 'formula-field': isFormulaField }"
  >
    <!-- 文本输入 -->
    <el-input
      v-if="field.type === 'text'"
      v-model="localValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.readonly"
      :maxlength="field.maxLength"
      show-word-limit
      clearable
      @input="handleInput"
    />

    <!-- 多行文本 -->
    <el-input
      v-else-if="field.type === 'textarea'"
      v-model="localValue"
      type="textarea"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.readonly"
      :rows="field.rows || 3"
      :maxlength="field.maxLength"
      show-word-limit
      @input="handleInput"
    />

    <!-- 数字输入 -->
    <el-input-number
      v-else-if="field.type === 'number'"
      v-model="localValue"
      :placeholder="field.placeholder"
      :disabled="field.readonly"
      :min="field.numberConfig?.min"
      :max="field.numberConfig?.max"
      :step="field.numberConfig?.step || 1"
      :precision="0"
      controls-position="right"
      style="width: 100%"
      @change="handleInput"
    />

    <!-- 小数输入 -->
    <el-input-number
      v-else-if="field.type === 'decimal'"
      v-model="localValue"
      :placeholder="field.placeholder"
      :disabled="field.readonly"
      :min="field.numberConfig?.min"
      :max="field.numberConfig?.max"
      :step="field.numberConfig?.step || 0.01"
      :precision="field.numberConfig?.precision || 2"
      controls-position="right"
      style="width: 100%"
      @change="handleInput"
    />

    <!-- 日期选择 -->
    <el-date-picker
      v-else-if="field.type === 'date'"
      v-model="localValue"
      type="date"
      :placeholder="field.placeholder || '选择日期'"
      :disabled="field.readonly"
      value-format="YYYY-MM-DD"
      style="width: 100%"
      @change="handleInput"
    />

    <!-- 日期时间选择 -->
    <el-date-picker
      v-else-if="field.type === 'datetime'"
      v-model="localValue"
      type="datetime"
      :placeholder="field.placeholder || '选择时间'"
      :disabled="field.readonly"
      value-format="YYYY-MM-DD HH:mm:ss"
      style="width: 100%"
      @change="handleInput"
    />

    <!-- 下拉选择 -->
    <el-select
      v-else-if="field.type === 'select'"
      v-model="localValue"
      :placeholder="field.placeholder || '请选择'"
      :disabled="field.readonly"
      filterable
      clearable
      style="width: 100%"
      @change="handleInput"
    >
      <el-option
        v-for="opt in field.options"
        :key="opt.value"
        :label="opt.label"
        :value="opt.value"
      />
    </el-select>

    <!-- 多选 -->
    <el-select
      v-else-if="field.type === 'multi_select'"
      v-model="localValue"
      multiple
      :placeholder="field.placeholder || '请选择'"
      :disabled="field.readonly"
      filterable
      clearable
      collapse-tags
      collapse-tags-tooltip
      style="width: 100%"
      @change="handleInput"
    >
      <el-option
        v-for="opt in field.options"
        :key="opt.value"
        :label="opt.label"
        :value="opt.value"
      />
    </el-select>

    <!-- 单选框组 -->
    <el-radio-group
      v-else-if="field.type === 'radio'"
      v-model="localValue"
      :disabled="field.readonly"
      @change="handleInput"
    >
      <el-radio
        v-for="opt in field.options"
        :key="opt.value"
        :value="opt.value"
      >
        {{ opt.label }}
      </el-radio>
    </el-radio-group>

    <!-- 开关 -->
    <el-switch
      v-else-if="field.type === 'switch'"
      v-model="localValue"
      :disabled="field.readonly"
      @change="handleInput"
    />

    <!-- 引用选择 (远程搜索) -->
    <el-select
      v-else-if="field.type === 'reference'"
      v-model="localValue"
      :placeholder="field.placeholder || '请选择'"
      :disabled="field.readonly"
      filterable
      remote
      :remote-method="handleRemoteSearch"
      :loading="referenceLoading"
      clearable
      style="width: 100%"
      @change="handleInput"
    >
      <el-option
        v-for="opt in referenceOptions"
        :key="opt.value"
        :label="opt.label"
        :value="opt.value"
      />
    </el-select>

    <!-- 树形选择 -->
    <el-tree-select
      v-else-if="field.type === 'tree_select'"
      v-model="localValue"
      :data="treeOptions"
      :props="{ label: 'label', value: 'value', children: 'children' }"
      :placeholder="field.placeholder || '请选择'"
      :disabled="field.readonly"
      check-strictly
      filterable
      clearable
      style="width: 100%"
      @change="handleInput"
    />

    <!-- 公式字段 (只读显示) -->
    <div v-else-if="field.type === 'formula'" class="formula-display">
      <span class="formula-value">{{ formatFormulaValue(localValue) }}</span>
      <el-tooltip v-if="field.formulaConfig?.expression" placement="top">
        <template #content>
          公式: {{ field.formulaConfig.expression }}
        </template>
        <el-icon class="formula-icon"><InfoFilled /></el-icon>
      </el-tooltip>
    </div>

    <!-- 编号字段 (只读) -->
    <el-input
      v-else-if="field.type === 'code'"
      v-model="localValue"
      :placeholder="field.placeholder || '自动生成'"
      disabled
    >
      <template #prefix>
        <el-icon><Document /></el-icon>
      </template>
    </el-input>

    <!-- 图片上传 -->
    <div v-else-if="field.type === 'image'" class="image-upload-field">
      <el-upload
        :action="uploadAction"
        :headers="uploadHeaders"
        :show-file-list="false"
        :on-success="handleImageSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeImageUpload"
        :disabled="field.readonly"
        accept="image/*"
      >
        <div v-if="localValue" class="image-preview">
          <el-image
            :src="getImageUrl(localValue)"
            fit="cover"
            :preview-src-list="[getImageUrl(localValue)]"
          />
          <div class="image-actions" v-if="!field.readonly">
            <el-button type="primary" size="small" circle :icon="Upload" />
            <el-button type="danger" size="small" circle :icon="Delete" @click.stop="handleRemoveImage" />
          </div>
        </div>
        <div v-else class="image-placeholder">
          <el-icon :size="32"><Picture /></el-icon>
          <span>点击上传图片</span>
        </div>
      </el-upload>
    </div>

    <!-- 文件上传 -->
    <div v-else-if="field.type === 'file'" class="file-upload-field">
      <el-upload
        :action="uploadAction"
        :headers="uploadHeaders"
        :file-list="fileList"
        :on-success="handleFileSuccess"
        :on-remove="handleFileRemove"
        :on-error="handleUploadError"
        :disabled="field.readonly"
        :limit="field.fileConfig?.limit || 5"
        :accept="field.fileConfig?.accept"
      >
        <el-button :disabled="field.readonly">
          <el-icon><Upload /></el-icon>
          上传文件
        </el-button>
        <template #tip>
          <div class="upload-tip">
            {{ field.fileConfig?.tip || '支持常用文件格式' }}
          </div>
        </template>
      </el-upload>
    </div>

    <!-- 富文本编辑器 -->
    <div v-else-if="field.type === 'rich_text'" class="rich-text-field">
      <div
        class="rich-text-editor"
        contenteditable
        :innerHTML="localValue || ''"
        @input="handleRichTextInput"
        @blur="handleRichTextBlur"
        :class="{ readonly: field.readonly }"
      />
      <div class="rich-text-toolbar" v-if="!field.readonly">
        <el-button-group size="small">
          <el-button @click="execCommand('bold')"><strong>B</strong></el-button>
          <el-button @click="execCommand('italic')"><em>I</em></el-button>
          <el-button @click="execCommand('underline')"><u>U</u></el-button>
          <el-button @click="execCommand('insertUnorderedList')">• 列表</el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 颜色选择器 -->
    <el-color-picker
      v-else-if="field.type === 'color'"
      v-model="localValue"
      :disabled="field.readonly"
      show-alpha
      :predefine="predefineColors"
      @change="handleInput"
    />

    <!-- 默认文本输入 -->
    <el-input
      v-else
      v-model="localValue"
      :placeholder="field.placeholder"
      :disabled="field.readonly"
      @input="handleInput"
    />

    <!-- 帮助文本 -->
    <div v-if="field.helpText" class="field-help">
      {{ field.helpText }}
    </div>
  </el-form-item>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Document, Upload, Delete, Picture } from '@element-plus/icons-vue'
import request from '@/utils/request'

const props = defineProps({
  field: {
    type: Object,
    required: true
  },
  modelValue: {
    type: [String, Number, Boolean, Array, Object],
    default: null
  },
  formData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// 本地值
const localValue = ref(props.modelValue)

// 引用选择器状态
const referenceLoading = ref(false)
const referenceOptions = ref([])
const treeOptions = ref([])

// 文件上传状态
const fileList = ref([])

// 上传配置
const uploadAction = computed(() => '/api/common/upload/')
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

// 预定义颜色
const predefineColors = [
  '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399',
  '#ffffff', '#000000', '#ff4500', '#ff8c00', '#ffd700',
  '#90ee90', '#00ced1', '#1e90ff', '#c71585', '#9370db'
]

// 是否是公式字段
const isFormulaField = computed(() => {
  return ['formula', 'expression'].includes(props.field.type)
})

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  localValue.value = newVal
})

// 处理输入
function handleInput(val) {
  const value = val !== undefined ? val : localValue.value
  emit('update:modelValue', value)
  emit('change', { field: props.field.key, value })
}

// 远程搜索
async function handleRemoteSearch(query) {
  if (!props.field.referenceConfig?.api) return
  
  referenceLoading.value = true
  try {
    const params = { page_size: 50 }
    if (query) {
      params.search = query
    }
    
    const res = await request.get(props.field.referenceConfig.api, { params })
    const data = res?.results || res || []
    
    const labelField = props.field.referenceConfig.labelField || 'name'
    const valueField = props.field.referenceConfig.valueField || 'id'
    
    referenceOptions.value = data.map(item => ({
      label: item[labelField],
      value: item[valueField]
    }))
  } catch (error) {
    console.error('远程搜索失败:', error)
  } finally {
    referenceLoading.value = false
  }
}

// 加载树形数据
async function loadTreeOptions() {
  if (!props.field.referenceConfig?.api) return
  
  try {
    const res = await request.get(props.field.referenceConfig.api)
    const data = res?.results || res || []
    
    const labelField = props.field.referenceConfig.labelField || 'name'
    const valueField = props.field.referenceConfig.valueField || 'id'
    
    // 转换为树形结构
    treeOptions.value = transformToTree(data, labelField, valueField)
  } catch (error) {
    console.error('加载树形数据失败:', error)
  }
}

function transformToTree(data, labelField, valueField) {
  return data.map(item => ({
    label: item[labelField],
    value: item[valueField],
    children: item.children ? transformToTree(item.children, labelField, valueField) : undefined
  }))
}

// 格式化公式值
function formatFormulaValue(value) {
  if (value === null || value === undefined) return '-'
  
  const format = props.field.formulaConfig?.format
  if (format === 'currency') {
    return `¥ ${Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
  }
  if (format === 'percent') {
    return `${(Number(value) * 100).toFixed(2)}%`
  }
  
  return value
}

// 初始化
onMounted(() => {
  // 设置默认值
  if (localValue.value === null && props.field.defaultValue !== undefined) {
    localValue.value = props.field.defaultValue
    handleInput(localValue.value)
  }
  
  // 加载引用选项
  if (props.field.type === 'reference' && props.modelValue) {
    handleRemoteSearch('')
  }
  
  // 加载树形选项
  if (props.field.type === 'tree_select') {
    loadTreeOptions()
  }
  
  // 初始化文件列表
  if (props.field.type === 'file' && props.modelValue) {
    fileList.value = Array.isArray(props.modelValue) 
      ? props.modelValue.map(url => ({ name: url.split('/').pop(), url }))
      : []
  }
})

// ===== 图片上传处理 =====
function getImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${window.location.origin}${url}`
}

function beforeImageUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

function handleImageSuccess(response) {
  const url = response?.url || response?.data?.url
  if (url) {
    localValue.value = url
    handleInput(url)
    ElMessage.success('图片上传成功')
  }
}

function handleRemoveImage() {
  localValue.value = null
  handleInput(null)
}

// ===== 文件上传处理 =====
function handleFileSuccess(response, file, uploadFiles) {
  const url = response?.url || response?.data?.url
  if (url) {
    const urls = uploadFiles.map(f => f.response?.url || f.response?.data?.url || f.url).filter(Boolean)
    localValue.value = urls
    handleInput(urls)
    ElMessage.success('文件上传成功')
  }
}

function handleFileRemove(file, uploadFiles) {
  const urls = uploadFiles.map(f => f.response?.url || f.response?.data?.url || f.url).filter(Boolean)
  localValue.value = urls
  handleInput(urls)
}

function handleUploadError(error) {
  console.error('上传失败:', error)
  ElMessage.error('上传失败，请重试')
}

// ===== 富文本处理 =====
function handleRichTextInput(e) {
  localValue.value = e.target.innerHTML
}

function handleRichTextBlur() {
  handleInput(localValue.value)
}

function execCommand(command) {
  document.execCommand(command, false, null)
}
</script>

<style lang="scss" scoped>
.formula-field {
  :deep(.el-form-item__content) {
    background: #f5f7fa;
    border-radius: 4px;
    padding: 0 12px;
  }
}

.formula-display {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
  
  .formula-value {
    font-weight: 500;
    color: #409eff;
  }
  
  .formula-icon {
    color: #909399;
    cursor: help;
  }
}

.field-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

// 图片上传
.image-upload-field {
  .image-preview {
    position: relative;
    width: 120px;
    height: 120px;
    border-radius: 8px;
    overflow: hidden;
    
    :deep(.el-image) {
      width: 100%;
      height: 100%;
    }
    
    .image-actions {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 8px;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      gap: 8px;
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    &:hover .image-actions {
      opacity: 1;
    }
  }
  
  .image-placeholder {
    width: 120px;
    height: 120px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #909399;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      border-color: #409eff;
      color: #409eff;
    }
    
    span {
      font-size: 12px;
    }
  }
}

// 文件上传
.file-upload-field {
  .upload-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}

// 富文本编辑器
.rich-text-field {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  
  .rich-text-editor {
    min-height: 120px;
    padding: 12px;
    outline: none;
    
    &.readonly {
      background: #f5f7fa;
      pointer-events: none;
    }
    
    &:focus {
      border-color: #409eff;
    }
  }
  
  .rich-text-toolbar {
    padding: 8px;
    border-top: 1px solid #ebeef5;
    background: #f5f7fa;
  }
}
</style>
