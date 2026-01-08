/**
 * 资产表单 Composable
 * 
 * 遵循 .cursorrules 规约:
 * - 组件 <script> 长度禁止超过 100 行
 * - 复杂交互逻辑必须提取到 @/composables
 */
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

/**
 * 资产表单数据逻辑
 */
export function useAssetFormData(props) {
  const formRef = ref(null)
  const submitting = ref(false)
  const activeTab = ref('basic')
  
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
  
  // 是否编辑模式
  const isEdit = computed(() => !!props?.asset?.id)
  
  // 重置表单
  function resetForm() {
    Object.assign(form, { ...defaultForm })
    activeTab.value = 'basic'
  }
  
  // 从资产数据填充表单
  function fillFromAsset(asset) {
    if (!asset) {
      resetForm()
      return
    }
    
    Object.assign(form, {
      asset_code: asset.asset_code || '',
      name: asset.name || '',
      category: asset.category || null,
      categoryPath: asset.category ? [asset.category] : [],
      brand: asset.brand || '',
      model: asset.model || '',
      serial_number: asset.serial_number || '',
      unit: asset.unit || '台',
      quantity: asset.quantity || 1,
      status: asset.status || 'idle',
      original_value: asset.original_value || 0,
      current_value: asset.current_value || 0,
      accumulated_depreciation: asset.accumulated_depreciation || 0,
      acquisition_method: asset.acquisition_method || 'purchase',
      acquisition_date: asset.acquisition_date || null,
      warranty_expiry: asset.warranty_expiry || null,
      using_user: asset.using_user || null,
      using_department: asset.using_department || null,
      location: asset.location || null,
      manage_department: asset.manage_department || null,
      manager: asset.manager || null,
      rfid_code: asset.rfid_code || '',
      barcode: asset.barcode || '',
      qrcode: asset.qrcode || '',
      image: asset.image || '',
      remark: asset.remark || ''
    })
  }
  
  return {
    formRef,
    form,
    rules,
    submitting,
    activeTab,
    isEdit,
    defaultForm,
    resetForm,
    fillFromAsset
  }
}

/**
 * 资产字段配置逻辑
 */
export function useAssetFieldConfig() {
  const fieldConfigs = ref({})
  const configLoading = ref(false)
  
  // 加载字段配置
  async function loadFieldConfigs(mode = 'create') {
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
    } catch (error) {
      console.error('加载字段配置失败:', error)
      fieldConfigs.value = {}
    } finally {
      configLoading.value = false
    }
  }
  
  // 判断字段是否只读
  function isFieldReadonly(fieldKey, isEdit = false) {
    const config = fieldConfigs.value[fieldKey]
    if (!config) {
      // 资产编号默认在新增时自动生成（只读）
      if (fieldKey === 'asset_code') {
        return !isEdit
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
  
  return {
    fieldConfigs,
    configLoading,
    loadFieldConfigs,
    isFieldReadonly,
    isFieldHidden,
    isFieldRequired,
    getFieldPlaceholder
  }
}

/**
 * 资产图片处理逻辑
 */
export function useAssetImage() {
  const imageFile = ref(null)
  const localPreviewUrl = ref('')
  const previewDialogVisible = ref(false)
  
  // 预览图片URL
  function getPreviewUrl(formImage) {
    if (localPreviewUrl.value) {
      return localPreviewUrl.value
    }
    if (formImage) {
      return formImage.startsWith('http') ? formImage : formImage
    }
    return ''
  }
  
  // 处理图片选择
  function handleImageSelect(event) {
    const file = event.target?.files?.[0]
    if (!file) return
    
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      ElMessage.error('只支持 JPG、PNG、GIF、WebP 格式的图片')
      return
    }
    
    // 验证文件大小（5MB）
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过 5MB')
      return
    }
    
    imageFile.value = file
    
    // 创建本地预览
    const reader = new FileReader()
    reader.onload = (e) => {
      localPreviewUrl.value = e.target?.result
    }
    reader.readAsDataURL(file)
  }
  
  // 删除图片
  function removeImage() {
    imageFile.value = null
    localPreviewUrl.value = ''
    return '' // 返回空字符串供表单使用
  }
  
  // 重置图片状态
  function resetImageState() {
    imageFile.value = null
    localPreviewUrl.value = ''
  }
  
  return {
    imageFile,
    localPreviewUrl,
    previewDialogVisible,
    getPreviewUrl,
    handleImageSelect,
    removeImage,
    resetImageState
  }
}

/**
 * 资产提交逻辑
 */
export function useAssetSubmit() {
  const submitting = ref(false)
  
  async function submitAsset(form, imageFile, isEdit, assetId, callback) {
    submitting.value = true
    
    try {
      let result
      
      if (imageFile) {
        // 有图片时使用 FormData
        const formData = new FormData()
        
        Object.keys(form).forEach(key => {
          if (form[key] !== null && form[key] !== undefined && key !== 'categoryPath') {
            formData.append(key, form[key])
          }
        })
        
        formData.append('image_file', imageFile)
        
        if (isEdit) {
          result = await request.put(`/assets/${assetId}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        } else {
          result = await request.post('/assets/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        }
      } else {
        // 无图片时使用 JSON
        const payload = { ...form }
        delete payload.categoryPath
        
        if (isEdit) {
          result = await request.put(`/assets/${assetId}/`, payload)
        } else {
          result = await request.post('/assets/', payload)
        }
      }
      
      ElMessage.success(isEdit ? '资产更新成功' : '资产创建成功')
      
      if (callback) callback(result)
      return true
    } catch (error) {
      console.error('保存资产失败:', error)
      ElMessage.error(error.response?.data?.msg || '保存失败')
      return false
    } finally {
      submitting.value = false
    }
  }
  
  return {
    submitting,
    submitAsset
  }
}

/**
 * 资产状态选项
 */
export function useAssetOptions() {
  const statusOptions = [
    { value: 'idle', label: '闲置' },
    { value: 'in_use', label: '在用' },
    { value: 'borrowed', label: '借用' },
    { value: 'maintenance', label: '维修中' },
    { value: 'pending_maintenance', label: '待维修' },
    { value: 'disposed', label: '已处置' },
    { value: 'pending_disposal', label: '待处置' },
    { value: 'approving', label: '审批中' }
  ]
  
  const acquisitionMethods = [
    { value: 'purchase', label: '采购' },
    { value: 'lease', label: '租赁' },
    { value: 'gift', label: '赠予' },
    { value: 'transfer', label: '调入' },
    { value: 'self_build', label: '自建' },
    { value: 'other', label: '其他' }
  ]
  
  const unitOptions = ['台', '个', '套', '件', '把', '张', '块', '米', '平方米']
  
  return {
    statusOptions,
    acquisitionMethods,
    unitOptions
  }
}
