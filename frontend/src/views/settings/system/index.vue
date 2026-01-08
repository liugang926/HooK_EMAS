<template>
  <div class="system-config-container">
    <!-- 系统配置 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
          <el-button type="primary" @click="saveConfig" :loading="saving">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
        </div>
      </template>
      
      <el-form :model="configForm" label-width="120px" class="config-form">
        <!-- 基本信息 -->
        <el-divider content-position="left">
          <el-icon><InfoFilled /></el-icon>
          基本信息
        </el-divider>
        
        <el-form-item label="系统名称">
          <el-input v-model="configForm.name" placeholder="请输入系统名称" style="width: 300px" />
          <span class="form-tip">系统名称会显示在登录页面和侧边栏</span>
        </el-form-item>
        
        <el-form-item label="版权信息">
          <el-input v-model="configForm.copyright" placeholder="请输入版权信息" style="width: 400px" />
        </el-form-item>
        
        <!-- Logo设置 -->
        <el-divider content-position="left">
          <el-icon><Picture /></el-icon>
          Logo设置
        </el-divider>
        
        <el-form-item label="系统Logo">
          <div class="logo-upload">
            <el-upload
              class="logo-uploader"
              :show-file-list="false"
              :before-upload="beforeLogoUpload"
              :http-request="handleLogoUpload"
              accept="image/*"
            >
              <div class="logo-preview" v-if="configForm.logo">
                <img :src="configForm.logo" class="logo-image" />
                <div class="logo-mask">
                  <el-icon><Upload /></el-icon>
                  <span>更换</span>
                </div>
              </div>
              <div class="logo-placeholder" v-else>
                <el-icon><Plus /></el-icon>
                <span>上传Logo</span>
              </div>
            </el-upload>
            <el-button v-if="configForm.logo" type="danger" link @click="removeLogo">
              <el-icon><Delete /></el-icon>
              删除Logo
            </el-button>
          </div>
          <span class="form-tip">建议尺寸：200x200像素，支持 PNG、JPG、SVG 格式</span>
        </el-form-item>
        
        <el-form-item label="网站图标">
          <div class="favicon-upload">
            <el-upload
              class="favicon-uploader"
              :show-file-list="false"
              :before-upload="beforeFaviconUpload"
              :http-request="handleFaviconUpload"
              accept="image/*,.ico"
            >
              <div class="favicon-preview" v-if="configForm.favicon">
                <img :src="configForm.favicon" class="favicon-image" />
              </div>
              <div class="favicon-placeholder" v-else>
                <el-icon><Plus /></el-icon>
              </div>
            </el-upload>
          </div>
          <span class="form-tip">建议尺寸：32x32像素，支持 ICO、PNG 格式</span>
        </el-form-item>
        
        <!-- 主题设置 -->
        <el-divider content-position="left">
          <el-icon><Brush /></el-icon>
          主题设置
        </el-divider>
        
        <el-form-item label="主题模式">
          <el-radio-group v-model="configForm.theme">
            <el-radio-button label="light">
              <el-icon><Sunny /></el-icon>
              浅色模式
            </el-radio-button>
            <el-radio-button label="dark">
              <el-icon><Moon /></el-icon>
              深色模式
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="主题色">
          <div class="color-picker-wrapper">
            <el-color-picker v-model="configForm.primaryColor" show-alpha />
            <span class="color-value">{{ configForm.primaryColor }}</span>
          </div>
          <div class="preset-colors">
            <span class="preset-label">预设颜色：</span>
            <div
              v-for="color in presetColors"
              :key="color.value"
              :class="['preset-color', { active: configForm.primaryColor === color.value }]"
              :style="{ backgroundColor: color.value }"
              :title="color.name"
              @click="configForm.primaryColor = color.value"
            />
          </div>
        </el-form-item>
        
        <!-- 预览 -->
        <el-divider content-position="left">
          <el-icon><View /></el-icon>
          效果预览
        </el-divider>
        
        <el-form-item label="侧边栏预览">
          <div class="preview-sidebar" :style="{ '--preview-primary': configForm.primaryColor }">
            <div class="preview-logo">
              <img v-if="configForm.logo" :src="configForm.logo" class="preview-logo-img" />
              <div v-else class="preview-logo-placeholder">Logo</div>
              <span class="preview-name">{{ configForm.name || '系统名称' }}</span>
            </div>
            <div class="preview-menu">
              <div class="preview-menu-item active">
                <el-icon><HomeFilled /></el-icon>
                <span>首页</span>
              </div>
              <div class="preview-menu-item">
                <el-icon><Box /></el-icon>
                <span>资产</span>
              </div>
              <div class="preview-menu-item">
                <el-icon><Setting /></el-icon>
                <span>设置</span>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import {
  Check,
  InfoFilled,
  Picture,
  Plus,
  Upload,
  Delete,
  Brush,
  Sunny,
  Moon,
  View,
  HomeFilled,
  Box,
  Setting
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const saving = ref(false)

const configForm = reactive({
  name: '钩子资产',
  logo: '',
  favicon: '',
  primaryColor: '#3b82f6',
  theme: 'light',
  copyright: '© 2024 钩子资产 版权所有'
})

// 预设颜色
const presetColors = [
  { name: '科技蓝', value: '#3b82f6' },
  { name: '活力橙', value: '#f97316' },
  { name: '清新绿', value: '#22c55e' },
  { name: '优雅紫', value: '#8b5cf6' },
  { name: '热情红', value: '#ef4444' },
  { name: '典雅金', value: '#eab308' },
  { name: '深邃青', value: '#06b6d4' },
  { name: '沉稳灰', value: '#6b7280' }
]

// 加载配置
onMounted(() => {
  const { systemConfig } = appStore
  Object.assign(configForm, systemConfig)
})

// 监听配置变化，实时预览
watch(configForm, (newConfig) => {
  appStore.applyTheme(newConfig)
}, { deep: true })

// 保存配置
async function saveConfig() {
  saving.value = true
  try {
    appStore.updateSystemConfig(configForm)
    
    // 同时保存到后端
    await appStore.saveSystemConfig(configForm)
    
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// Logo上传前验证
function beforeLogoUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

// Logo上传处理
function handleLogoUpload({ file }) {
  const reader = new FileReader()
  reader.onload = (e) => {
    configForm.logo = e.target.result
  }
  reader.readAsDataURL(file)
}

// 删除Logo
function removeLogo() {
  configForm.logo = ''
}

// Favicon上传前验证
function beforeFaviconUpload(file) {
  const isLt500K = file.size / 1024 < 500
  
  if (!isLt500K) {
    ElMessage.error('图标大小不能超过 500KB')
    return false
  }
  return true
}

// Favicon上传处理
function handleFaviconUpload({ file }) {
  const reader = new FileReader()
  reader.onload = (e) => {
    configForm.favicon = e.target.result
    // 更新页面favicon
    updateFavicon(e.target.result)
  }
  reader.readAsDataURL(file)
}

// 更新页面favicon
function updateFavicon(url) {
  let link = document.querySelector("link[rel*='icon']")
  if (!link) {
    link = document.createElement('link')
    link.type = 'image/x-icon'
    link.rel = 'shortcut icon'
    document.getElementsByTagName('head')[0].appendChild(link)
  }
  link.href = url
}
</script>

<style lang="scss" scoped>
.system-config-container {
  // Ensure container takes minimum height and allows proper scrolling
  min-height: 100%;
  padding-bottom: 40px; // Add bottom padding to ensure last card is fully visible
  
  .config-card {
    border-radius: 16px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      font-size: 16px;
    }
  }
  
  .config-form {
    max-width: 800px;
    
    .form-tip {
      margin-left: 12px;
      font-size: 12px;
      color: #9ca3af;
    }
    
    .el-divider {
      margin: 32px 0 24px;
      
      :deep(.el-divider__text) {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        color: #374151;
      }
    }
  }
  
  // Logo上传
  .logo-upload {
    display: flex;
    align-items: flex-end;
    gap: 16px;
    
    .logo-uploader {
      :deep(.el-upload) {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        cursor: pointer;
        overflow: hidden;
        transition: all 0.3s;
        
        &:hover {
          border-color: var(--el-color-primary);
        }
      }
    }
    
    .logo-preview {
      position: relative;
      width: 120px;
      height: 120px;
      
      .logo-image {
        width: 100%;
        height: 100%;
        object-fit: contain;
      }
      
      .logo-mask {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        opacity: 0;
        transition: opacity 0.3s;
        
        .el-icon {
          font-size: 24px;
          margin-bottom: 4px;
        }
      }
      
      &:hover .logo-mask {
        opacity: 1;
      }
    }
    
    .logo-placeholder {
      width: 120px;
      height: 120px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #9ca3af;
      
      .el-icon {
        font-size: 32px;
        margin-bottom: 8px;
      }
    }
  }
  
  // Favicon上传
  .favicon-upload {
    .favicon-uploader {
      :deep(.el-upload) {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          border-color: var(--el-color-primary);
        }
      }
    }
    
    .favicon-preview, .favicon-placeholder {
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      img {
        max-width: 100%;
        max-height: 100%;
      }
    }
    
    .favicon-placeholder {
      color: #9ca3af;
    }
  }
  
  // 颜色选择器
  .color-picker-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .color-value {
      font-family: monospace;
      font-size: 14px;
      color: #6b7280;
    }
  }
  
  .preset-colors {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    
    .preset-label {
      font-size: 13px;
      color: #6b7280;
    }
    
    .preset-color {
      width: 28px;
      height: 28px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
      border: 2px solid transparent;
      
      &:hover {
        transform: scale(1.1);
      }
      
      &.active {
        border-color: #1f2937;
        box-shadow: 0 0 0 2px white, 0 0 0 4px currentColor;
      }
    }
  }
  
  // 预览
  .preview-sidebar {
    width: 220px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border-radius: 12px;
    padding: 16px 0;
    
    .preview-logo {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 16px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      
      .preview-logo-img {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        object-fit: contain;
        background: white;
        padding: 4px;
      }
      
      .preview-logo-placeholder {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(255, 255, 255, 0.5);
        font-size: 10px;
      }
      
      .preview-name {
        color: white;
        font-weight: 600;
        font-size: 14px;
      }
    }
    
    .preview-menu {
      padding: 12px 8px;
      
      .preview-menu-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 13px;
        margin-bottom: 4px;
        transition: all 0.2s;
        
        &.active {
          background: var(--preview-primary, #3b82f6);
          color: white;
        }
        
        &:hover:not(.active) {
          background: rgba(255, 255, 255, 0.1);
        }
      }
    }
  }
}
</style>
