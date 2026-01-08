<template>
  <div class="asset-create-container">
    <el-card class="create-card">
      <template #header>
        <div class="card-header">
          <h2>{{ isEdit ? '编辑资产' : '新增资产' }}</h2>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="asset-form"
        v-loading="loading"
      >
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="资产名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入资产名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资产分类" prop="category">
              <el-cascader
                v-model="form.categoryPath"
                :options="categoryOptions"
                :props="{ value: 'id', label: 'name', children: 'children', checkStrictly: true, emitPath: true }"
                placeholder="请选择资产分类"
                style="width: 100%"
                @change="handleCategoryChange"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="资产编号" prop="asset_code">
              <el-input v-model="form.asset_code" placeholder="留空自动生成">
                <template #append>
                  <el-button @click="generateCode">自动生成</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SN序列号" prop="serial_number">
              <el-input v-model="form.serial_number" placeholder="请输入SN序列号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="品牌" prop="brand">
              <el-input v-model="form.brand" placeholder="请输入品牌" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="型号" prop="model">
              <el-input v-model="form.model" placeholder="请输入型号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="规格" prop="specification">
              <el-input v-model="form.specification" placeholder="请输入规格" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="form.unit" placeholder="请选择单位" style="width: 100%">
                <el-option label="台" value="台" />
                <el-option label="套" value="套" />
                <el-option label="个" value="个" />
                <el-option label="件" value="件" />
                <el-option label="张" value="张" />
                <el-option label="把" value="把" />
                <el-option label="辆" value="辆" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">财务信息</el-divider>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="原值(元)" prop="original_value">
              <el-input-number
                v-model="form.original_value"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="购置日期" prop="acquisition_date">
              <el-date-picker
                v-model="form.acquisition_date"
                type="date"
                placeholder="请选择购置日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="取得方式" prop="acquisition_method">
              <el-select v-model="form.acquisition_method" placeholder="请选择取得方式" style="width: 100%">
                <el-option label="采购" value="purchase" />
                <el-option label="租赁" value="lease" />
                <el-option label="赠予" value="gift" />
                <el-option label="调入" value="transfer" />
                <el-option label="自建" value="self_build" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保修到期" prop="warranty_expiry">
              <el-date-picker
                v-model="form.warranty_expiry"
                type="date"
                placeholder="请选择保修到期日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">位置与责任人</el-divider>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="存放位置" prop="location">
              <el-cascader
                v-model="form.locationPath"
                :options="locationOptions"
                :props="{ value: 'id', label: 'name', children: 'children', checkStrictly: true, emitPath: true }"
                placeholder="请选择存放位置"
                style="width: 100%"
                @change="handleLocationChange"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="使用部门" prop="using_department">
              <DepartmentSelect
                v-model="form.using_department"
                placeholder="请选择使用部门"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="使用人" prop="using_user">
              <UserSelect
                v-model="form.using_user"
                placeholder="请选择使用人"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="管理员" prop="manager">
              <UserSelect
                v-model="form.manager"
                placeholder="请选择管理员"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">其他信息</el-divider>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="RFID编码" prop="rfid_code">
              <el-input v-model="form.rfid_code" placeholder="请输入RFID编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="条形码" prop="barcode">
              <el-input v-model="form.barcode" placeholder="请输入条形码" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="资产图片" prop="images">
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
          </div>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileChange"
          />
          <div class="upload-tip">支持 jpg、png 格式，不超过 5MB</div>
        </el-form-item>
        
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { generateAssetCode } from '@/api/assets'
import { DepartmentSelect, UserSelect } from '@/components/common'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const isEdit = computed(() => !!route.query.id)
const formRef = ref()
const fileInputRef = ref(null)
const loading = ref(false)
const submitting = ref(false)

// 图片相关
const imageFile = ref(null)
const previewImageUrl = ref('')

const form = reactive({
  name: '',
  category: null,
  categoryPath: [],
  asset_code: '',
  serial_number: '',
  brand: '',
  model: '',
  specification: '',
  unit: '台',
  original_value: 0,
  acquisition_date: '',
  acquisition_method: 'purchase',
  warranty_expiry: '',
  location: null,
  locationPath: [],
  using_department: null,
  using_user: null,
  manager: null,
  rfid_code: '',
  barcode: '',
  image: '',
  remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  original_value: [{ required: true, message: '请输入原值', trigger: 'blur' }]
}

// 选项数据 (DepartmentSelect and UserSelect components handle their own data loading)
const categoryOptions = ref([])
const locationOptions = ref([])

// 加载分类选项（使用 tree API）
async function loadCategories() {
  try {
    const res = await request.get('/assets/categories/tree/')
    // tree API 直接返回树形结构
    categoryOptions.value = res || []
  } catch (error) {
    console.error('加载资产分类失败:', error)
  }
}

// 加载位置选项（使用 tree API）
async function loadLocations() {
  try {
    const res = await request.get('/organizations/locations/tree/')
    // tree API 直接返回树形结构
    locationOptions.value = res || []
  } catch (error) {
    console.error('加载位置失败:', error)
  }
}

// Note: Department and User loading is handled by DepartmentSelect and UserSelect components

// 加载资产详情（编辑模式）
async function loadAssetDetail(id) {
  loading.value = true
  try {
    const res = await request.get(`/assets/list/${id}/`)
    const data = res.data || res
    
    // 填充表单
    Object.assign(form, {
      name: data.name || '',
      category: data.category || null,
      categoryPath: data.category ? [data.category] : [],
      asset_code: data.asset_code || '',
      serial_number: data.serial_number || '',
      brand: data.brand || '',
      model: data.model || '',
      specification: data.specification || '',
      unit: data.unit || '台',
      original_value: data.original_value || 0,
      acquisition_date: data.acquisition_date || '',
      acquisition_method: data.acquisition_method || 'purchase',
      warranty_expiry: data.warranty_expiry || '',
      location: data.location || null,
      locationPath: data.location ? [data.location] : [],
      using_department: data.using_department || null,
      using_user: data.using_user || null,
      manager: data.manager || null,
      rfid_code: data.rfid_code || '',
      barcode: data.barcode || '',
      image: data.image || '',
      remark: data.remark || ''
    })
    
    if (data.image) {
      previewImageUrl.value = data.image
    }
  } catch (error) {
    console.error('加载资产详情失败:', error)
    ElMessage.error('加载资产详情失败')
  } finally {
    loading.value = false
  }
}

// 处理分类变化
function handleCategoryChange(path) {
  if (path && path.length > 0) {
    form.category = path[path.length - 1]
  } else {
    form.category = null
  }
}

// 处理位置变化
function handleLocationChange(path) {
  if (path && path.length > 0) {
    form.location = path[path.length - 1]
  } else {
    form.location = null
  }
}

// 生成资产编号 - 调用后端API使用配置的编号规则
// Following .cursorrules: API requests encapsulated in @/api
async function generateCode() {
  const companyId = appStore.currentCompany?.id
  if (!companyId) {
    ElMessage.warning('请先选择公司')
    return
  }
  
  try {
    const res = await generateAssetCode(companyId)
    if (res.code) {
      form.asset_code = res.code
      ElMessage.success(`已生成编号: ${res.code}`)
    } else if (res.error) {
      ElMessage.error(res.error)
    }
  } catch (error) {
    console.error('生成编号失败:', error)
    // Fallback to local generation if API fails
    const date = new Date()
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const random = Math.random().toString(36).substr(2, 8).toUpperCase()
    form.asset_code = `ZC${year}${month}${day}${random}`
    ElMessage.warning('使用了备用编号生成方式')
  }
}

// 触发文件选择
function triggerUpload() {
  fileInputRef.value?.click()
}

// 处理文件选择
function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB!')
    return
  }
  
  imageFile.value = file
  if (previewImageUrl.value && previewImageUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewImageUrl.value)
  }
  previewImageUrl.value = URL.createObjectURL(file)
  event.target.value = ''
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
    original_value: form.original_value,
    acquisition_method: form.acquisition_method,
    acquisition_date: form.acquisition_date || null,
    warranty_expiry: form.warranty_expiry || null,
    using_user: form.using_user,
    using_department: form.using_department,
    location: form.location,
    manager: form.manager,
    rfid_code: form.rfid_code,
    barcode: form.barcode,
    remark: form.remark
  }
  
  // 如果有资产编号，包含在提交数据中
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
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.error('请检查表单填写是否完整')
    return
  }
  
  submitting.value = true
  
  try {
    const submitData = buildSubmitData()
    let result
    
    if (imageFile.value) {
      // 有图片上传，使用 FormData
      const formData = new FormData()
      Object.keys(submitData).forEach(key => {
        formData.append(key, submitData[key])
      })
      formData.append('image', imageFile.value)
      
      if (isEdit.value) {
        result = await request.put(`/assets/list/${route.query.id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } else {
        result = await request.post('/assets/list/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }
    } else {
      // 普通 JSON 提交
      if (isEdit.value) {
        result = await request.put(`/assets/list/${route.query.id}/`, submitData)
      } else {
        result = await request.post('/assets/list/', submitData)
      }
    }
    
    ElMessage.success(isEdit.value ? '编辑成功' : '新增成功')
    router.push('/assets/list')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  router.back()
}

// 初始化
onMounted(async () => {
  loading.value = true
  
  try {
    // 并行加载选项数据 (DepartmentSelect and UserSelect handle their own loading)
    await Promise.all([
      loadCategories(),
      loadLocations()
    ])
    
    // 编辑模式下加载资产详情
    if (isEdit.value && route.query.id) {
      await loadAssetDetail(route.query.id)
    }
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
.asset-create-container {
  .create-card {
    border-radius: 16px;
    
    .card-header {
      h2 {
        margin: 0;
        font-size: 18px;
        color: #1f2937;
      }
    }
    
    .asset-form {
      max-width: 1000px;
      
      :deep(.el-divider__text) {
        font-size: 14px;
        font-weight: 600;
        color: #1f2937;
      }
    }
    
    .image-uploader {
      width: 160px;
      height: 160px;
      border: 2px dashed #d9d9d9;
      border-radius: 12px;
      cursor: pointer;
      overflow: hidden;
      position: relative;
      transition: all 0.3s;
      background: #fafafa;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      
      &:hover {
        border-color: var(--el-color-primary);
        color: var(--el-color-primary);
      }
      
      .preview-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      
      .upload-placeholder {
        text-align: center;
        color: #909399;
        
        .upload-icon {
          font-size: 28px;
          margin-bottom: 8px;
        }
      }
    }
    
    .upload-tip {
      font-size: 12px;
      color: #909399;
      margin-top: 8px;
    }
  }
}
</style>
