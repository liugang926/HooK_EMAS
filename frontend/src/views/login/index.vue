<template>
  <div class="login-container">
    <div class="login-bg">
      <div class="bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>
    
    <div class="login-content">
      <div class="login-card">
        <div class="login-header">
          <img src="@/assets/logo.svg" alt="Logo" class="logo" />
          <h1 class="title">钩子资产</h1>
          <p class="subtitle">企业固定资产管理系统</p>
        </div>
        
        <!-- 登录方式切换 -->
        <div class="login-tabs">
          <div
            v-for="tab in loginTabs"
            :key="tab.key"
            :class="['tab-item', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            <el-icon><component :is="tab.icon" /></el-icon>
            <span>{{ tab.label }}</span>
          </div>
        </div>
        
        <!-- 账号密码登录 -->
        <el-form
          v-if="activeTab === 'password'"
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
              @input="handleCredentialChange"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @input="handleCredentialChange"
              @blur="handlePasswordBlur"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item prop="company">
            <el-select
              v-model="loginForm.company"
              :placeholder="companyPlaceholder"
              size="large"
              style="width: 100%"
              :loading="companiesLoading"
              :disabled="!credentialsVerified"
              @focus="handleCompanyFocus"
            >
              <template #prefix>
                <el-icon><OfficeBuilding /></el-icon>
              </template>
              <el-option
                v-for="company in companies"
                :key="company.id"
                :label="company.name"
                :value="company.id"
              />
            </el-select>
            <div v-if="credentialsVerified && companies.length > 0" class="verify-success">
              <el-icon color="#67c23a"><CircleCheck /></el-icon>
              <span>账号验证成功</span>
            </div>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" class="forget-link">忘记密码？</el-link>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              :disabled="!canLogin"
              class="login-btn"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
        
        <!-- SSO 登录 -->
        <div v-else class="sso-login">
          <div class="qr-container">
            <div v-if="ssoLoading" class="qr-loading">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <span>正在获取登录二维码...</span>
            </div>
            <template v-else>
              <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="QR Code" class="qr-code" />
              <div v-else class="qr-placeholder">
                <el-icon><View /></el-icon>
                <span>请使用{{ ssoTypeLabel }}扫码登录</span>
              </div>
            </template>
          </div>
          <p class="sso-tip">
            <el-icon><InfoFilled /></el-icon>
            请使用{{ ssoTypeLabel }}扫描上方二维码登录
          </p>
        </div>
        
      </div>
      
      <div class="login-footer">
        <p>&copy; 2026 钩子资产 版权所有</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import axios from 'axios'
import {
  User,
  Lock,
  Loading,
  View,
  InfoFilled,
  ChatLineRound,
  Iphone,
  OfficeBuilding,
  CircleCheck
} from '@element-plus/icons-vue'
import {
  getWeWorkLoginUrl,
  getDingTalkLoginUrl,
  getFeishuLoginUrl
} from '@/api/auth'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()

// 登录方式
const loginTabs = [
  { key: 'password', label: '账号登录', icon: User },
  { key: 'wework', label: '企业微信', icon: ChatLineRound },
  { key: 'dingtalk', label: '钉钉', icon: Iphone }
]

const activeTab = ref('password')
const loading = ref(false)
const ssoLoading = ref(false)
const qrCodeUrl = ref('')

// 临时token用于完成登录
const tempToken = ref('')
// 凭证是否已验证
const credentialsVerified = ref(false)
// 上次验证的凭证（用于检测变化）
const lastVerifiedCredentials = ref({ username: '', password: '' })

// 公司列表
const companies = ref([])
const companiesLoading = ref(false)

// 登录表单
const loginFormRef = ref()
const loginForm = ref({
  username: '',
  password: '',
  company: null,
  remember: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  company: [
    { required: true, message: '请选择登录公司', trigger: 'change' }
  ]
}

// 公司选择器占位文本
const companyPlaceholder = computed(() => {
  if (companiesLoading.value) return '正在验证账号...'
  if (!credentialsVerified.value) return '请先输入正确的账号密码'
  return '请选择登录公司'
})

// 是否可以登录
const canLogin = computed(() => {
  return credentialsVerified.value && loginForm.value.company
})

// 当账号密码变化时，重置验证状态
function handleCredentialChange() {
  if (credentialsVerified.value) {
    // 检查凭证是否变化
    if (loginForm.value.username !== lastVerifiedCredentials.value.username ||
        loginForm.value.password !== lastVerifiedCredentials.value.password) {
      credentialsVerified.value = false
      tempToken.value = ''
      companies.value = []
      loginForm.value.company = null
    }
  }
}

// 密码输入框失去焦点时，自动验证凭证
async function handlePasswordBlur() {
  // 已验证或正在验证则跳过
  if (credentialsVerified.value || companiesLoading.value) return
  
  // 检查账号密码是否填写完整
  if (!loginForm.value.username || !loginForm.value.password) {
    return
  }
  
  // 密码长度不足
  if (loginForm.value.password.length < 6) {
    return
  }
  
  // 自动验证凭证
  await verifyCredentials()
}

// 当点击公司选择器时，自动验证凭证（备用触发）
async function handleCompanyFocus() {
  if (credentialsVerified.value || companiesLoading.value) return
  
  // 检查账号密码是否填写
  if (!loginForm.value.username || !loginForm.value.password) {
    return
  }
  
  if (loginForm.value.password.length < 6) {
    return
  }
  
  await verifyCredentials()
}

// 验证凭证并获取公司列表
async function verifyCredentials() {
  companiesLoading.value = true
  try {
    const res = await axios.post('/api/auth/verify-credentials/', {
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    
    // 保存验证结果
    tempToken.value = res.data.temp_token
    companies.value = res.data.companies || []
    credentialsVerified.value = true
    lastVerifiedCredentials.value = {
      username: loginForm.value.username,
      password: loginForm.value.password
    }
    
    // 自动选择公司
    if (companies.value.length === 1) {
      loginForm.value.company = companies.value[0].id
    } else {
      const savedCompanyId = localStorage.getItem('currentCompanyId')
      if (savedCompanyId) {
        const savedCompany = companies.value.find(c => c.id === parseInt(savedCompanyId))
        if (savedCompany) {
          loginForm.value.company = savedCompany.id
        }
      }
    }
    
  } catch (error) {
    credentialsVerified.value = false
    companies.value = []
    ElMessage.error(error.response?.data?.detail || error.response?.data?.error || '用户名或密码错误')
  } finally {
    companiesLoading.value = false
  }
}

const ssoTypeLabel = computed(() => {
  const labels = {
    wework: '企业微信',
    dingtalk: '钉钉',
    feishu: '飞书'
  }
  return labels[activeTab.value] || '应用'
})

// 登录
async function handleLogin() {
  if (!loginFormRef.value) return
  
  // 如果凭证未验证，先验证
  if (!credentialsVerified.value) {
    await verifyCredentials()
    if (!credentialsVerified.value) return
  }
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      // Complete login with temp token and selected company
      const res = await axios.post('/api/auth/complete-login/', {
        temp_token: tempToken.value,
        company_id: loginForm.value.company
      })
      
      // Store tokens - update both localStorage AND store's token ref
      const { access, refresh, user } = res.data
      userStore.updateToken(access, refresh)
      
      // Set user info directly from response (avoid extra API call that may fail due to CSRF)
      if (user) {
        userStore.setUserInfo(user)
      }
      
      // Save selected company to store and localStorage
      const selectedCompany = companies.value.find(c => c.id === loginForm.value.company)
      if (selectedCompany) {
        appStore.setCurrentCompany(selectedCompany)
      }
      
      ElMessage.success('登录成功')
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.error || '登录失败'
      // If token expired, re-verify credentials and retry login
      if (error.response?.status === 401 && errorMsg.includes('过期')) {
        credentialsVerified.value = false
        tempToken.value = ''
        ElMessage.warning('验证已过期，正在重新验证...')
        await verifyCredentials()
        // If re-verification succeeded, retry login automatically
        if (credentialsVerified.value && tempToken.value) {
          try {
            const retryRes = await axios.post('/api/auth/complete-login/', {
              temp_token: tempToken.value,
              company_id: loginForm.value.company
            })
            const { access, refresh, user } = retryRes.data
            userStore.updateToken(access, refresh)
            if (user) {
              userStore.setUserInfo(user)
            }
            const selectedCompany = companies.value.find(c => c.id === loginForm.value.company)
            if (selectedCompany) {
              appStore.setCurrentCompany(selectedCompany)
            }
            ElMessage.success('登录成功')
            const redirect = route.query.redirect || '/'
            router.push(redirect)
            return
          } catch (retryError) {
            ElMessage.error('登录失败，请重试')
          }
        }
      } else {
        ElMessage.error(errorMsg)
      }
    } finally {
      loading.value = false
    }
  })
}

// SSO 登录
async function handleSSOLogin(type) {
  ssoLoading.value = true
  
  try {
    const redirectUri = window.location.origin + '/sso/callback'
    let loginUrl = ''
    
    switch (type) {
      case 'wework':
        loginUrl = await getWeWorkLoginUrl(redirectUri)
        break
      case 'dingtalk':
        loginUrl = await getDingTalkLoginUrl(redirectUri)
        break
      case 'feishu':
        loginUrl = await getFeishuLoginUrl(redirectUri)
        break
    }
    
    if (loginUrl) {
      window.location.href = loginUrl.url || loginUrl
    }
  } catch (error) {
    ElMessage.error('获取登录链接失败')
  } finally {
    ssoLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
  
  .login-bg {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    
    .bg-shapes {
      position: absolute;
      inset: 0;
      overflow: hidden;
      
      .shape {
        position: absolute;
        border-radius: 50%;
        opacity: 0.1;
        background: #fff;
        animation: float 15s infinite ease-in-out;
        
        &.shape-1 {
          width: 400px;
          height: 400px;
          top: -100px;
          right: -100px;
          animation-delay: 0s;
        }
        
        &.shape-2 {
          width: 300px;
          height: 300px;
          bottom: -80px;
          left: -80px;
          animation-delay: -5s;
        }
        
        &.shape-3 {
          width: 200px;
          height: 200px;
          top: 50%;
          left: 30%;
          animation-delay: -10s;
        }
      }
    }
  }
  
  .login-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    position: relative;
    z-index: 1;
    
    .login-card {
      width: 100%;
      max-width: 420px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-radius: 24px;
      padding: 48px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      
      .login-header {
        text-align: center;
        margin-bottom: 32px;
        
        .logo {
          width: 64px;
          height: 64px;
          margin-bottom: 16px;
        }
        
        .title {
          font-size: 28px;
          font-weight: 700;
          color: #1f2937;
          margin: 0 0 8px;
          letter-spacing: 2px;
        }
        
        .subtitle {
          font-size: 14px;
          color: #6b7280;
          margin: 0;
        }
      }
      
      .login-tabs {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
        
        .tab-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          padding: 12px;
          border-radius: 12px;
          cursor: pointer;
          color: #6b7280;
          background: #f3f4f6;
          transition: all 0.3s;
          
          &:hover {
            background: #e5e7eb;
          }
          
          &.active {
            color: #fff;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
          }
          
          .el-icon {
            font-size: 20px;
          }
          
          span {
            font-size: 12px;
          }
        }
      }
      
      .login-form {
        .verify-success {
          display: flex;
          align-items: center;
          gap: 4px;
          margin-top: 6px;
          font-size: 12px;
          color: #67c23a;
        }
        
        .el-form-item:nth-child(4) {
          margin-bottom: 8px;
          
          :deep(.el-form-item__content) {
            justify-content: space-between;
          }
        }
        
        .forget-link {
          font-size: 13px;
        }
        
        .login-btn {
          width: 100%;
          height: 48px;
          font-size: 16px;
          border-radius: 12px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          
          &:hover {
            opacity: 0.9;
          }
          
          &:disabled {
            opacity: 0.6;
            cursor: not-allowed;
          }
        }
      }
      
      .sso-login {
        text-align: center;
        padding: 20px 0;
        
        .qr-container {
          width: 200px;
          height: 200px;
          margin: 0 auto 20px;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f9fafb;
          
          .qr-loading,
          .qr-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            color: #6b7280;
            
            .el-icon {
              font-size: 48px;
            }
            
            .loading-icon {
              animation: spin 1s linear infinite;
            }
          }
          
          .qr-code {
            width: 180px;
            height: 180px;
          }
        }
        
        .sso-tip {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          color: #9ca3af;
          font-size: 13px;
        }
      }
      
      .third-party-login {
        margin-top: 24px;
        
        :deep(.el-divider__text) {
          color: #9ca3af;
          font-size: 13px;
        }
        
        .login-icons {
          display: flex;
          justify-content: center;
          gap: 24px;
          margin-top: 16px;
          
          .login-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            
            svg {
              width: 24px;
              height: 24px;
            }
            
            &.wework {
              background: #e8f5e9;
              color: #4caf50;
              
              &:hover {
                background: #4caf50;
                color: #fff;
              }
            }
            
            &.dingtalk {
              background: #e3f2fd;
              color: #2196f3;
              
              &:hover {
                background: #2196f3;
                color: #fff;
              }
            }
            
            &.feishu {
              background: #fce4ec;
              color: #e91e63;
              
              &:hover {
                background: #e91e63;
                color: #fff;
              }
            }
          }
        }
      }
    }
    
    .login-footer {
      margin-top: 32px;
      
      p {
        color: rgba(255, 255, 255, 0.7);
        font-size: 13px;
        margin: 0;
      }
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(10deg);
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
</style>
