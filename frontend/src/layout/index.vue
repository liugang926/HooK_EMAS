<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="layout-aside">
      <div class="logo-container">
        <img :src="systemLogo || defaultLogo" alt="Logo" class="logo" />
        <span v-show="!sidebarCollapsed" class="logo-text">{{ systemName }}</span>
      </div>
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          :unique-opened="true"
          @select="handleMenuSelect"
          class="sidebar-menu"
        >
          <template v-for="route in menuRoutes" :key="route.path">
            <!-- 单级菜单 -->
            <el-menu-item
              v-if="!route.children || route.children.length === 0"
              :index="'/' + route.path"
            >
              <el-icon><component :is="getIconComponent(route.meta?.icon)" /></el-icon>
              <template #title>{{ route.meta?.title }}</template>
            </el-menu-item>
            
            <!-- 多级菜单 -->
            <el-sub-menu v-else :index="'/' + route.path">
              <template #title>
                <el-icon><component :is="getIconComponent(route.meta?.icon)" /></el-icon>
                <span>{{ route.meta?.title }}</span>
              </template>
              <el-menu-item
                v-for="child in route.children"
                :key="child.path"
                :index="`/${route.path}/${child.path}`"
              >
                {{ child.meta?.title }}
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>
    
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleSidebar">
            <Fold v-if="!sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="(item, index) in breadcrumbs"
              :key="index"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 公司切换 -->
          <el-dropdown class="company-dropdown" trigger="click">
            <span class="company-trigger">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ currentCompanyName }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="company in companies"
                  :key="company.id"
                  @click="switchCompany(company)"
                >
                  {{ company.name }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- 消息通知 -->
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
            <el-icon class="notification-icon" @click="showNotifications">
              <Bell />
            </el-icon>
          </el-badge>
          
          <!-- 用户下拉菜单 -->
          <el-dropdown class="user-dropdown" trigger="click">
            <span class="user-trigger">
              <el-avatar :size="32" :src="userAvatar">
                {{ displayName.charAt(0) }}
              </el-avatar>
              <span class="username">{{ displayName }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToProfile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item @click="changePassword">
                  <el-icon><Lock /></el-icon>
                  修改密码
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容区 -->
      <el-main class="layout-main">
        <router-view v-slot="{ Component, route }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import defaultLogo from '@/assets/logo.svg'
import {
  Fold,
  Expand,
  OfficeBuilding,
  ArrowDown,
  Bell,
  User,
  Lock,
  SwitchButton,
  HomeFilled,
  Box,
  Coin,
  ShoppingCart,
  Document,
  DataAnalysis,
  Money,
  Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

// 公司列表 (from store)
const companies = computed(() => appStore.companies)
const unreadCount = ref(0)
const cachedViews = ref(['Dashboard'])

// 计算属性
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)
const sidebarWidth = computed(() => sidebarCollapsed.value ? '64px' : '220px')
const displayName = computed(() => userStore.displayName)
const userAvatar = computed(() => userStore.avatar)
const currentCompanyName = computed(() => appStore.currentCompany?.name || '选择公司')
const systemName = computed(() => appStore.systemConfig.name || '钩子资产')
const systemLogo = computed(() => appStore.systemConfig.logo)

// 图标映射
const iconMap = {
  HomeFilled,
  Bell,
  Box,
  Coin,
  ShoppingCart,
  Document,
  DataAnalysis,
  Money,
  Setting
}

// 获取图标组件
function getIconComponent(iconName) {
  return iconMap[iconName] || HomeFilled
}

// 菜单路由
const menuRoutes = computed(() => {
  const mainRoute = router.options.routes.find(r => r.path === '/')
  return mainRoute?.children?.filter(child => child.meta?.title) || []
})

// 当前激活菜单
const activeMenu = computed(() => {
  const { path } = route
  return path
})

// 面包屑
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title
  }))
})

// 方法
function toggleSidebar() {
  appStore.toggleSidebar()
}

function switchCompany(company) {
  // Don't do anything if selecting the same company
  if (appStore.currentCompany?.id === company.id) {
    return
  }
  
  appStore.setCurrentCompany(company)
  
  // Refresh the current page to reload data with new company filter
  // Using router replace with a key change to force component remount
  const currentPath = route.fullPath
  router.replace({ path: '/redirect' + currentPath })
}

function showNotifications() {
  router.push('/todo')
}

function handleMenuSelect(index) {
  router.push(index)
}

function goToProfile() {
  router.push('/settings/profile')
}

function changePassword() {
  // 弹出修改密码对话框
}

function handleLogout() {
  userStore.doLogout()
}

// 初始化
onMounted(async () => {
  // Load companies from store (handles persistence and auto-selection)
  await appStore.loadCompanies()
})
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  
  .layout-aside {
    background: linear-gradient(180deg, #1e3a5f 0%, #0d2137 100%);
    transition: width 0.3s;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    
    .logo-container {
      height: 64px;
      min-height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      
      .logo {
        width: 32px;
        height: 32px;
      }
      
      .logo-text {
        margin-left: 12px;
        font-size: 18px;
        font-weight: 600;
        color: #fff;
        white-space: nowrap;
      }
    }
    
    // 滚动容器需要设置正确的高度
    :deep(.el-scrollbar) {
      flex: 1;
      height: calc(100vh - 64px);
      
      .el-scrollbar__wrap {
        overflow-x: hidden;
      }
      
      // 让滚动条始终可见
      .el-scrollbar__bar {
        opacity: 1;
        
        &.is-vertical {
          width: 6px;
          right: 2px;
        }
        
        .el-scrollbar__thumb {
          background-color: rgba(255, 255, 255, 0.3);
          
          &:hover {
            background-color: rgba(255, 255, 255, 0.5);
          }
        }
      }
    }
    
    .sidebar-menu {
      border-right: none;
      background: transparent;
      
      :deep(.el-menu-item),
      :deep(.el-sub-menu__title) {
        color: rgba(255, 255, 255, 0.7);
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: #fff;
        }
      }
      
      :deep(.el-menu-item.is-active) {
        background: linear-gradient(90deg, var(--el-color-primary) 0%, var(--el-color-primary-dark-2) 100%) !important;
        color: #fff !important;
      }
      
      :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
        color: #fff;
      }
      
      // 二级菜单样式
      :deep(.el-menu--inline) {
        background: rgba(0, 0, 0, 0.3) !important;
        
        .el-menu-item {
          color: rgba(255, 255, 255, 0.7) !important;
          padding-left: 50px !important;
          min-width: auto;
          background: transparent !important;
          
          &:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            color: #fff !important;
          }
          
          &.is-active {
            background: linear-gradient(90deg, var(--el-color-primary) 0%, var(--el-color-primary-dark-2) 100%) !important;
            color: #fff !important;
          }
        }
      }
    }
  }
  
  .main-container {
    flex-direction: column;
    background: #f5f7fa;
    height: 100vh; // Ensure container takes full viewport height
    overflow: hidden; // Prevent double scrollbars
    
    .layout-header {
      background: #fff;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
      z-index: 10;
      
      .header-left {
        display: flex;
        align-items: center;
        gap: 16px;
        
        .collapse-btn {
          font-size: 20px;
          cursor: pointer;
          color: #606266;
          
          &:hover {
            color: var(--el-color-primary);
          }
        }
      }
      
      .header-right {
        display: flex;
        align-items: center;
        gap: 24px;
        
        .company-dropdown {
          .company-trigger {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            color: #606266;
            
            .arrow {
              font-size: 12px;
            }
          }
        }
        
        .notification-badge {
          .notification-icon {
            font-size: 20px;
            cursor: pointer;
            color: #606266;
            
            &:hover {
              color: #3b82f6;
            }
          }
        }
        
        .user-dropdown {
          .user-trigger {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            
            .username {
              color: #303133;
            }
            
            .arrow {
              font-size: 12px;
              color: #909399;
            }
          }
        }
      }
    }
    
    .layout-main {
      padding: 20px;
      overflow-y: auto;
      flex: 1; // Take remaining space after header
      min-height: 0; // Important for flex children to enable proper overflow scrolling
    }
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
