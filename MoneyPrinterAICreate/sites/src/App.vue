<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const isMobile = ref(false)
const showSidebar = ref(true) // 侧边栏始终显示

// 检查屏幕尺寸
const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 768
  // 移除移动设备隐藏侧边栏的逻辑，侧边栏始终显示
}

// 初始化
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  
  // 确保移除深色主题
  document.documentElement.classList.remove('dark')
})</script>

<template>
  <div class="app-container" :class="{ 'mobile': isMobile }">
    <!-- 移除移动端菜单按钮，侧边栏始终显示 -->
    
    <!-- 侧边栏 -->
    <aside 
      class="sidebar expanded"
    >
      <div class="sidebar-header">
        <div class="logo-container">
          <div class="logo-icon">💰</div>
          <h1 class="logo-text">
            <span class="logo-gradient">MoneyPrinter</span>
          </h1>
        </div>
        <!-- 移除侧边栏切换按钮 -->
      </div>
      
      <nav class="sidebar-nav">
        <ul class="nav-list">
          <li class="nav-item">
            <RouterLink to="/" active-class="active">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <span class="nav-text">首页</span>
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/model-management" active-class="active">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
              <span class="nav-text">模型管理</span>
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/template-management" active-class="active">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
              <span class="nav-text">模板管理</span>
            </RouterLink>
          </li>
        </ul>
      </nav>
      
          <!-- 移除了侧边栏底部的用户信息 -->
    </aside>
    
    <!-- 主内容区域 -->
    <main class="main-content sidebar-expanded">
      <!-- 顶部导航栏 -->
      <header class="top-nav">
        <div class="nav-content">
          <div class="nav-left">
            <h2 class="page-title">
              <RouterView name="title" />
            </h2>
          </div>
          <div class="nav-right">
            <!-- 移除了搜索框、通知、主题切换和用户信息 -->
          </div>
        </div>
      </header>
      
      <!-- 页面内容 -->
      <div class="page-content">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #ffffff;
}

/* 主题相关变量 */
:root {
  --primary-color: #f59e0b;
  --primary-hover: #d97706;
  --bg-color: #ffffff;
  --card-bg: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --sidebar-width: 260px;
  --sidebar-collapsed: 60px;
  --top-nav-height: 64px;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}

/* 应用容器 */
.app-container {
  display: flex;
  min-height: 100vh;
  background-color: #ffffff;
  color: var(--text-primary);
}

/* 移动端菜单按钮 */
/* 移除移动端菜单按钮相关样式 */

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: var(--sidebar-width);
  background-color: var(--card-bg);
  border-right: 2px solid var(--border-color);
  z-index: 1000;
  overflow-y: auto;
  /* 移除backdrop-filter以保持简洁外观 */
}

/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  background-color: #fef3c7;
  border-radius: 0.5rem;
  color: var(--primary-color);
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.logo-gradient {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-toggle {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-toggle:hover {
  background-color: var(--border-color);
  color: var(--text-primary);
}

/* 侧边栏导航 */
.sidebar-nav {
  padding: 1rem 0;
}

.nav-group {
  margin-bottom: 1.5rem;
}

.nav-title {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.nav-list {
  list-style: none;
}

.nav-item {
  margin-bottom: 0.25rem;
}

.nav-item a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
}

.nav-item a:hover {
  background-color: var(--border-color);
  color: var(--text-primary);
}

.nav-item a.active {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--primary-color);
  font-weight: 500;
}

.nav-text {
  font-size: 0.875rem;
}

/* 侧边栏底部 */
.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background-color: var(--card-bg);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background-color: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* 移除侧边栏折叠相关的样式 */

/* 顶部导航栏 */
.top-nav {
  height: var(--top-nav-height);
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 999;
}

.nav-content {
  height: 100%;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-left .page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 用户信息样式 */
.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-info:hover {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
}

.user-details .user-name {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 移除导航组标题样式 */
.nav-title {
  display: none;
}

/* 搜索框 */
.search-container {
  position: relative;
}

.search-input {
  width: 180px;
  padding: 0.5rem 2rem 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background-color: transparent;
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
  width: 240px;
}

.search-icon {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

/* 导航按钮 */
.nav-btn {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.nav-btn:hover {
  background-color: var(--border-color);
  color: var(--text-primary);
}

/* 通知徽章 */
.notification-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 8px;
  background-color: #ef4444;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 页面内容 */
.page-content {
  padding: 20px;
  min-height: calc(100vh - var(--top-nav-height));
  flex: 1;
  overflow-y: hidden; /* 修改为hidden以防止滚动条出现 */
  width: 100%;
  box-sizing: border-box;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  :root {
    --sidebar-width: 240px;
  }
  
  .nav-content {
    padding: 0 1.5rem;
  }
  
  .page-content {
    padding: 1.5rem;
  }
}

@media (max-width: 768px) {
  /* 在移动设备上保持侧边栏显示，但可能需要调整宽度以适应小屏幕 */
  :root {
    --sidebar-width: 200px;
  }
  
  .main-content {
    margin-left: var(--sidebar-width);
    width: calc(100% - var(--sidebar-width));
  }
  
  .nav-content {
    padding: 0 1rem;
  }
  
  .search-input {
    width: 140px;
  }
  
  .search-input:focus {
    width: 180px;
  }
  
  .page-content {
    padding: 1rem;
    padding-top: 5rem;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.3s ease;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: var(--border-color);
}

::-webkit-scrollbar-thumb {
  background: var(--text-secondary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-color);
}
</style>