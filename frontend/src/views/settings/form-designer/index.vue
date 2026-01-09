<template>
  <div class="form-designer-page">
    <!-- 模块选择器 -->
    <div v-if="!selectedModule" class="module-selector">
      <div class="page-header">
        <h1>表单设计器</h1>
        <p class="subtitle">选择要配置的模块</p>
      </div>
      
      <div class="module-grid">
        <div
          v-for="mod in availableModules"
          :key="mod.name"
          class="module-card"
          @click="selectModule(mod)"
        >
          <div class="module-icon">
            <el-icon :size="32"><component :is="getModuleIcon(mod.name)" /></el-icon>
          </div>
          <div class="module-info">
            <h3>{{ mod.label }}</h3>
            <p>{{ mod.name }}</p>
          </div>
          <div v-if="hasLayout(mod.name)" class="layout-badge">
            <el-tag type="success" size="small">已配置</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 表单设计器 -->
    <FormDesigner
      v-else
      :module="selectedModule.name"
      :module-label="selectedModule.label"
      :fields="moduleFields"
      :initial-layout="moduleLayout"
      @save="handleSaveLayout"
    />

    <!-- 返回按钮 -->
    <div v-if="selectedModule" class="back-button">
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回模块列表
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, Box, Files, User, OfficeBuilding,
  ShoppingCart, Document, Location, Setting
} from '@element-plus/icons-vue'
import { FormDesigner } from '@/components/dynamic-form'
import request from '@/utils/request'

// 状态
const loading = ref(false)
const availableModules = ref([])
const existingLayouts = ref({})
const selectedModule = ref(null)
const moduleFields = ref([])
const moduleLayout = ref({ rows: [], groups: [] })

// 获取可用模块列表
async function loadModules() {
  loading.value = true
  try {
    // 从 Module Registry 获取模块列表
    const res = await request.get('/api/system/registry/')
    availableModules.value = res || []
  } catch (error) {
    console.error('加载模块失败:', error)
    // 使用默认模块列表
    availableModules.value = [
      { name: 'asset', label: '资产' },
      { name: 'supply', label: '办公用品' },
      { name: 'purchase_order', label: '采购订单' },
      { name: 'user', label: '用户' },
      { name: 'department', label: '部门' },
      { name: 'supplier', label: '供应商' },
      { name: 'location', label: '存放位置' },
    ]
  } finally {
    loading.value = false
  }
}

// 加载已有布局
async function loadExistingLayouts() {
  try {
    const res = await request.get('/api/system/form/layouts/')
    const layouts = res?.results || res || []
    existingLayouts.value = {}
    for (const layout of layouts) {
      existingLayouts.value[layout.module] = true
    }
  } catch (error) {
    console.error('加载布局失败:', error)
  }
}

// 判断模块是否已有布局
function hasLayout(moduleName) {
  return !!existingLayouts.value[moduleName]
}

// 选择模块
async function selectModule(mod) {
  loading.value = true
  try {
    // 加载模块字段定义
    const fieldsRes = await request.get(`/api/system/registry/${mod.name}/fields/`)
    moduleFields.value = fieldsRes || []
    
    // 加载现有布局
    const layoutRes = await request.get('/api/system/form/layouts/for_module/', {
      params: { module: mod.name, type: 'form' }
    })
    moduleLayout.value = layoutRes?.layout || { rows: [], groups: [] }
    
    selectedModule.value = mod
  } catch (error) {
    console.error('加载模块配置失败:', error)
    ElMessage.error('加载模块配置失败')
  } finally {
    loading.value = false
  }
}

// 返回模块列表
function goBack() {
  selectedModule.value = null
  moduleFields.value = []
  moduleLayout.value = { rows: [], groups: [] }
}

// 保存布局
async function handleSaveLayout({ module, layoutConfig }) {
  try {
    await request.post('/api/system/form/layouts/save_layout/', {
      module,
      layout_type: 'form',
      layout_config: layoutConfig
    })
    ElMessage.success('布局保存成功')
    
    // 更新已配置状态
    existingLayouts.value[module] = true
  } catch (error) {
    console.error('保存布局失败:', error)
    ElMessage.error('保存布局失败: ' + (error.message || '未知错误'))
  }
}

// 获取模块图标
function getModuleIcon(moduleName) {
  const iconMap = {
    asset: Box,
    supply: Files,
    user: User,
    department: OfficeBuilding,
    purchase_order: ShoppingCart,
    supplier: Document,
    location: Location
  }
  return iconMap[moduleName] || Setting
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadModules(),
    loadExistingLayouts()
  ])
})
</script>

<style lang="scss" scoped>
.form-designer-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.module-selector {
  padding: 24px;
  
  .page-header {
    margin-bottom: 32px;
    
    h1 {
      font-size: 24px;
      font-weight: 600;
      margin: 0 0 8px;
    }
    
    .subtitle {
      color: #909399;
      margin: 0;
    }
  }
  
  .module-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
  
  .module-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    
    &:hover {
      border-color: #409eff;
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
      transform: translateY(-2px);
    }
    
    .module-icon {
      width: 56px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
      border-radius: 12px;
      color: #fff;
    }
    
    .module-info {
      flex: 1;
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        margin: 0 0 4px;
      }
      
      p {
        font-size: 13px;
        color: #909399;
        margin: 0;
      }
    }
    
    .layout-badge {
      position: absolute;
      top: 12px;
      right: 12px;
    }
  }
}

.back-button {
  position: fixed;
  bottom: 24px;
  left: 24px;
  z-index: 100;
}
</style>
