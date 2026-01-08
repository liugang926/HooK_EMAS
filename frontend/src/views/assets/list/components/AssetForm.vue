<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑资产' : '新增资产'"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="asset-form-container">
      <!-- 头部区域：图片和基本信息 -->
      <div class="form-header">
        <div class="image-section">
          <div class="image-uploader" @click="triggerUpload">
            <el-image
              v-if="previewImageUrl"
              :src="previewImageUrl"
              fit="cover"
              class="preview-image"
            />
            <div v-else class="upload-placeholder">
              <el-icon class="upload-icon"><Plus /></el-icon>
              <span>点击上传图片</span>
            </div>
            <div class="image-overlay" v-if="previewImageUrl" @click.stop>
              <el-icon @click="handlePreviewImage"><ZoomIn /></el-icon>
              <el-icon @click="handleRemoveImage"><Delete /></el-icon>
            </div>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            class="hidden-input"
            @change="handleFileChange"
          />
          <div class="upload-tip">支持 jpg、png 格式，不超过 5MB</div>
        </div>
        <div class="basic-info">
          <el-form-item label="资产编号" label-width="80px" v-if="!isFieldHidden('asset_code')">
            <el-input
              v-model="form.asset_code"
              :disabled="isFieldReadonly('asset_code')"
              :placeholder="getFieldPlaceholder('asset_code', isEdit ? '' : '系统自动生成')"
              class="code-input"
            />
          </el-form-item>
          <el-form-item label="资产名称" label-width="80px" prop="name">
            <el-input v-model="form.name" placeholder="请输入资产名称" class="name-input" />
          </el-form-item>
          <div class="status-row">
            <el-form-item label="资产状态" label-width="80px">
              <el-select v-model="form.status" style="width: 150px">
                <el-option label="闲置" value="idle" />
                <el-option label="在用" value="in_use" />
                <el-option label="借用" value="borrowed" />
                <el-option label="维修中" value="maintenance" />
                <el-option label="待处置" value="pending_disposal" />
              </el-select>
            </el-form-item>
          </div>
        </div>
      </div>
      
      <!-- 分组标签页 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="asset-form"
      >
        <el-tabs v-model="activeTab" class="form-tabs">
          <!-- 基本信息 -->
          <el-tab-pane label="基本信息" name="basic">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="资产分类">
                  <CategorySelect
                    v-model="form.categoryPath"
                    @change="handleCategoryChange"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="品牌">
                  <el-input v-model="form.brand" placeholder="请输入品牌" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="型号">
                  <el-input v-model="form.model" placeholder="请输入型号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="序列号">
                  <el-input v-model="form.serial_number" placeholder="请输入序列号" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="计量单位">
                  <el-select v-model="form.unit" placeholder="请选择" style="width: 100%">
                    <el-option label="台" value="台" />
                    <el-option label="个" value="个" />
                    <el-option label="套" value="套" />
                    <el-option label="件" value="件" />
                    <el-option label="张" value="张" />
                    <el-option label="把" value="把" />
                    <el-option label="辆" value="辆" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="数量">
                  <el-input-number v-model="form.quantity" :min="1" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
          
          <!-- 财务信息 -->
          <el-tab-pane label="财务信息" name="finance">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="原值(元)" prop="original_value">
                  <el-input-number
                    v-model="form.original_value"
                    :min="0"
                    :precision="2"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="净值(元)">
                  <el-input-number
                    v-model="form.current_value"
                    :min="0"
                    :precision="2"
                    disabled
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="累计折旧">
                  <el-input-number
                    v-model="form.accumulated_depreciation"
                    :min="0"
                    :precision="2"
                    disabled
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="取得方式">
                  <el-select v-model="form.acquisition_method" style="width: 100%">
                    <el-option label="采购" value="purchase" />
                    <el-option label="租赁" value="lease" />
                    <el-option label="赠予" value="gift" />
                    <el-option label="调入" value="transfer" />
                    <el-option label="自建" value="self_build" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="取得日期">
                  <el-date-picker
                    v-model="form.acquisition_date"
                    type="date"
                    placeholder="请选择"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="保修到期">
                  <el-date-picker
                    v-model="form.warranty_expiry"
                    type="date"
                    placeholder="请选择"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
          
          <!-- 使用信息 -->
          <el-tab-pane label="使用信息" name="usage">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="使用人">
                  <UserSelect
                    v-model="form.using_user"
                    placeholder="请选择使用人"
                    @change="handleUserChange"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="使用部门">
                  <DepartmentSelect
                    v-model="form.using_department"
                    placeholder="请选择使用部门"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="存放位置">
                  <LocationSelect
                    v-model="form.location"
                    placeholder="请选择存放位置"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="管理部门">
                  <DepartmentSelect
                    v-model="form.manage_department"
                    placeholder="请选择管理部门"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="资产管理员">
                  <UserSelect
                    v-model="form.manager"
                    placeholder="请选择资产管理员"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
          
          <!-- 标签信息 -->
          <el-tab-pane label="标签信息" name="tags">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="RFID编码">
                  <el-input v-model="form.rfid_code" placeholder="请输入RFID编码" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="条形码">
                  <el-input v-model="form.barcode" placeholder="请输入条形码" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="二维码">
                  <el-input v-model="form.qrcode" disabled placeholder="系统自动生成" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
          
          <!-- 备注 -->
          <el-tab-pane label="备注" name="remark">
            <el-form-item label="备注信息" label-width="80px">
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="5"
                placeholder="请输入备注信息"
                style="width: 100%"
              />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </div>
    
    <!-- 图片预览弹窗 -->
    <el-dialog v-model="previewDialogVisible" title="图片预览" width="600px" append-to-body>
      <img :src="previewImageUrl" style="width: 100%;" />
    </el-dialog>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, ZoomIn, Delete } from '@element-plus/icons-vue'
import { UserSelect, DepartmentSelect, LocationSelect, CategorySelect } from '@/components/common'
import { createAsset, updateAsset, createAssetWithImage, updateAssetWithImage } from '@/api/assets'
import request from '@/utils/request'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  asset: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref(null)
const fileInputRef = ref(null)
const submitting = ref(false)
const activeTab = ref('basic')
const previewDialogVisible = ref(false)

// 字段配置
const fieldConfigs = ref({})
const configLoading = ref(false)

// 图片相关
const imageFile = ref(null)
const localPreviewUrl = ref('')

// 显示状态
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 是否编辑模式
const isEdit = computed(() => !!props.asset?.id)

// 预览图片URL
const previewImageUrl = computed(() => {
  if (localPreviewUrl.value) {
    return localPreviewUrl.value
  }
  if (form.image) {
    return form.image.startsWith('http') ? form.image : form.image
  }
  return ''
})

// 默认表单数据
const defaultForm = {
  asset_code: '',
  name: '',
  category: null,
  categoryPath: [],
  brand: '',
  model: '',
  serial_number: '',
  unit: '台',
  quantity: 1,
  status: 'idle',
  original_value: 0,
  current_value: 0,
  accumulated_depreciation: 0,
  acquisition_method: 'purchase',
  acquisition_date: null,
  warranty_expiry: null,
  using_user: null,
  using_department: null,
  location: null,
  manage_department: null,
  manager: null,
  rfid_code: '',
  barcode: '',
  qrcode: '',
  image: '',
  remark: ''
}

// 表单数据
const form = reactive({ ...defaultForm })

// 表单校验规则
const rules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  original_value: [{ required: true, message: '请输入资产原值', trigger: 'blur' }]
}

// 加载字段配置
async function loadFieldConfigs() {
  const mode = isEdit.value ? 'edit' : 'create'
  configLoading.value = true
  
  try {
    const res = await request.get('/system/form/fields/by_module/', {
      params: { module: 'asset', mode }
    })
    
    // 将字段配置转换为以 field_key 为键的对象
    const configs = {}
    const fields = res.data || res
    if (Array.isArray(fields)) {
      fields.forEach(field => {
        configs[field.key] = field
      })
    }
    fieldConfigs.value = configs
    console.log('Field configs loaded:', configs)
  } catch (error) {
    console.error('加载字段配置失败:', error)
    // 失败时使用默认配置（所有字段可编辑）
    fieldConfigs.value = {}
  } finally {
    configLoading.value = false
  }
}

// 判断字段是否只读
function isFieldReadonly(fieldKey) {
  const config = fieldConfigs.value[fieldKey]
  if (!config) {
    // 如果没有配置，使用默认逻辑
    // 资产编号默认在新增时自动生成（只读），编辑时可编辑（根据配置）
    if (fieldKey === 'asset_code') {
      return !isEdit.value // 新增时只读
    }
    return false
  }
  return config.readonly === true
}

// 判断字段是否隐藏
function isFieldHidden(fieldKey) {
  const config = fieldConfigs.value[fieldKey]
  if (!config) return false
  return config.hidden === true
}

// 判断字段是否必填
function isFieldRequired(fieldKey) {
  const config = fieldConfigs.value[fieldKey]
  if (!config) {
    // 默认必填字段
    return ['name'].includes(fieldKey)
  }
  return config.required === true
}

// 获取字段占位符
function getFieldPlaceholder(fieldKey, defaultText = '') {
  const config = fieldConfigs.value[fieldKey]
  if (config?.placeholder) {
    return config.placeholder
  }
  return defaultText
}

// 监听 asset 属性变化
watch(() => props.asset, (val) => {
  if (val) {
    Object.assign(form, {
      asset_code: val.asset_code || '',
      name: val.name || '',
      category: val.category || null,
      categoryPath: val.category ? [val.category] : [],
      brand: val.brand || '',
      model: val.model || '',
      serial_number: val.serial_number || '',
      unit: val.unit || '台',
      quantity: val.quantity || 1,
      status: val.status || 'idle',
      original_value: val.original_value || 0,
      current_value: val.current_value || 0,
      accumulated_depreciation: val.accumulated_depreciation || 0,
      acquisition_method: val.acquisition_method || 'purchase',
      acquisition_date: val.acquisition_date || null,
      warranty_expiry: val.warranty_expiry || null,
      using_user: val.using_user || null,
      using_department: val.using_department || null,
      location: val.location || null,
      manage_department: val.manage_department || null,
      manager: val.manager || null,
      rfid_code: val.rfid_code || '',
      barcode: val.barcode || '',
      qrcode: val.qrcode || '',
      image: val.image || '',
      remark: val.remark || ''
    })
    // 清除本地图片状态
    imageFile.value = null
    localPreviewUrl.value = ''
  } else {
    resetForm()
  }
}, { immediate: true })

// 监听对话框显示，加载字段配置
watch(() => props.modelValue, (visible) => {
  if (visible) {
    loadFieldConfigs()
  }
}, { immediate: true })

// 重置表单
function resetForm() {
  Object.assign(form, { ...defaultForm })
  imageFile.value = null
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
  }
  localPreviewUrl.value = ''
  activeTab.value = 'basic'
  formRef.value?.clearValidate()
}

// 触发文件选择
function triggerUpload() {
  // 使用 ref 触发文件选择
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

// 处理文件选择
function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  
  // 检查文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB!')
    return
  }
  
  // 释放旧的预览URL
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
  }
  
  // 创建本地预览
  imageFile.value = file
  localPreviewUrl.value = URL.createObjectURL(file)
  
  // 清空 input，允许重复选择同一文件
  event.target.value = ''
  
  ElMessage.success('图片已选择，保存时将一并上传')
}

// 预览图片
function handlePreviewImage() {
  if (previewImageUrl.value) {
    previewDialogVisible.value = true
  }
}

// 移除图片
function handleRemoveImage() {
  imageFile.value = null
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
  }
  localPreviewUrl.value = ''
  form.image = ''
}

// 处理分类变化
function handleCategoryChange(path, lastId) {
  form.category = lastId
}

// 处理用户变化
function handleUserChange(userId, user) {
  if (user && user.department) {
    form.using_department = user.department
  }
}

// 关闭弹窗
function handleClose() {
  visible.value = false
  resetForm()
}

// 构建提交数据
function buildSubmitData() {
  const data = {
    name: form.name,
    category: form.category,
    brand: form.brand,
    model: form.model,
    serial_number: form.serial_number,
    unit: form.unit,
    quantity: form.quantity,
    status: form.status,
    original_value: form.original_value,
    acquisition_method: form.acquisition_method,
    acquisition_date: form.acquisition_date,
    warranty_expiry: form.warranty_expiry,
    using_user: form.using_user,
    using_department: form.using_department,
    location: form.location,
    manage_department: form.manage_department,
    manager: form.manager,
    rfid_code: form.rfid_code,
    barcode: form.barcode,
    remark: form.remark
  }
  
  // 如果资产编号有值，则包含在提交数据中（允许编辑时修改资产编号）
  if (form.asset_code && form.asset_code.trim() !== '') {
    data.asset_code = form.asset_code
  }
  
  // 移除空值
  Object.keys(data).forEach(key => {
    if (data[key] === null || data[key] === '' || data[key] === undefined) {
      delete data[key]
    }
  })
  
  return data
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch (error) {
    // 切换到包含校验错误的标签页
    ElMessage.warning('请检查表单信息')
    return
  }
  
  submitting.value = true
  try {
    let result
    const submitData = buildSubmitData()
    
    // 判断是否有图片文件需要上传
    if (imageFile.value instanceof File) {
      // 使用 FormData 上传
      const formData = new FormData()
      Object.keys(submitData).forEach(key => {
        if (submitData[key] !== undefined && submitData[key] !== null) {
          formData.append(key, submitData[key])
        }
      })
      formData.append('image', imageFile.value)
      
      if (isEdit.value) {
        result = await updateAssetWithImage(props.asset.id, formData)
      } else {
        result = await createAssetWithImage(formData)
      }
    } else {
      // 普通 JSON 提交
      if (isEdit.value) {
        result = await updateAsset(props.asset.id, submitData)
      } else {
        result = await createAsset(submitData)
      }
    }
    
    ElMessage.success(isEdit.value ? '编辑成功' : '新增成功')
    emit('success', result)
    handleClose()
  } catch (error) {
    console.error('保存资产失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.hidden-input {
  display: none !important;
}

.asset-form-container {
  max-height: 70vh;
  overflow-y: auto;
  
  .form-header {
    display: flex;
    gap: 24px;
    padding-bottom: 20px;
    margin-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;
    
    .image-section {
      flex-shrink: 0;
      position: relative;
      
      .image-uploader {
        display: block;
        width: 160px;
        height: 160px;
        border: 2px dashed #d9d9d9;
        border-radius: 12px;
        cursor: pointer;
        overflow: hidden;
        position: relative;
        transition: all 0.3s;
        background: #fafafa;
        
        &:hover {
          border-color: var(--el-color-primary);
          
          .image-overlay {
            opacity: 1;
          }
        }
        
        .preview-image {
          width: 100%;
          height: 100%;
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
            font-size: 40px;
            margin-bottom: 8px;
            color: #c0c4cc;
          }
          
          span {
            font-size: 13px;
          }
        }
        
        .image-overlay {
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
          
          .el-icon {
            font-size: 24px;
            color: #fff;
            cursor: pointer;
            padding: 8px;
            border-radius: 4px;
            transition: all 0.2s;
            
            &:hover {
              background: rgba(255, 255, 255, 0.2);
              color: var(--el-color-primary-light-3);
            }
          }
        }
      }
      
      .upload-tip {
        margin-top: 8px;
        font-size: 12px;
        color: #909399;
        text-align: center;
      }
    }
    
    .basic-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 12px;
      
      .el-form-item {
        margin-bottom: 0;
      }
      
      .code-input {
        width: 200px;
        
        :deep(.el-input__wrapper) {
          background: #f5f7fa;
        }
      }
      
      .name-input {
        width: 300px;
        
        :deep(.el-input__inner) {
          font-size: 18px;
          font-weight: 500;
        }
      }
      
      .status-row {
        display: flex;
        align-items: center;
        gap: 16px;
      }
    }
  }
  
  .asset-form {
    .form-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 20px;
      }
      
      :deep(.el-tabs__item) {
        font-size: 14px;
        
        &.is-active {
          font-weight: 600;
        }
      }
    }
    
    .el-row {
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}
</style>
