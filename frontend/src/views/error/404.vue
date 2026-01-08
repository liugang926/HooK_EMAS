<template>
  <div class="error-container">
    <div class="error-content">
      <div class="error-code">404</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-desc">抱歉，您访问的页面不存在或已被移除</p>
      <div class="error-actions">
        <el-button type="primary" size="large" @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button size="large" @click="goBack">
          <el-icon><Back /></el-icon>
          返回上页
        </el-button>
      </div>
    </div>
    <div class="error-illustration">
      <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="grad404" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
          </linearGradient>
        </defs>
        <rect x="50" y="80" width="300" height="180" rx="20" fill="#f3f4f6"/>
        <circle cx="200" cy="140" r="40" fill="url(#grad404)"/>
        <text x="200" y="150" text-anchor="middle" fill="#fff" font-size="24" font-weight="bold">?</text>
        <rect x="100" y="200" width="200" height="20" rx="10" fill="#e5e7eb"/>
        <rect x="130" y="230" width="140" height="15" rx="7" fill="#e5e7eb"/>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { HomeFilled, Back } from '@element-plus/icons-vue'

const router = useRouter()

function goHome() {
  router.push('/')
}

function goBack() {
  router.back()
}
</script>

<style lang="scss" scoped>
.error-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 80px;
  padding: 40px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  
  .error-content {
    text-align: center;
    
    .error-code {
      font-size: 120px;
      font-weight: 800;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1;
      margin-bottom: 20px;
    }
    
    .error-title {
      font-size: 32px;
      color: #1f2937;
      margin: 0 0 12px;
    }
    
    .error-desc {
      font-size: 16px;
      color: #6b7280;
      margin: 0 0 32px;
    }
    
    .error-actions {
      display: flex;
      gap: 16px;
      justify-content: center;
    }
  }
  
  .error-illustration {
    svg {
      width: 400px;
      height: 300px;
    }
  }
}

@media (max-width: 768px) {
  .error-container {
    flex-direction: column-reverse;
    gap: 40px;
    
    .error-illustration svg {
      width: 280px;
      height: 210px;
    }
    
    .error-content .error-code {
      font-size: 80px;
    }
  }
}
</style>
