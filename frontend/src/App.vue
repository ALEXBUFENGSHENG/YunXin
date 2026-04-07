<template>
  <div class="app" :class="{ 'full-app': isChatRoute }">
    <el-container class="container" :class="{ fullscreen: isChatRoute }">
      <el-header v-if="!isChatRoute" height="60px" class="header">
        <div class="header-left">
          <h1 class="title">知小云课程助教</h1>
        </div>
        <div class="header-right">
          <router-link to="/" class="nav-link">聊天</router-link>
          <router-link to="/math" class="nav-link math-link">考研数学</router-link>
          <router-link to="/admin" class="nav-link admin-link">管理</router-link>
        </div>
      </el-header>
      <el-main class="main" :class="{ fullscreen: isChatRoute }">
        <router-view />
      </el-main>
      <el-footer v-if="!isChatRoute" height="40px" class="footer">
        <p> 知小云课程助教系统</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isChatRoute = computed(() => ['Chat', 'Learning', 'Math'].includes(route.name))
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f5f7fa;
}

.app.full-app {
  background: #ffffff;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  background: #ffffff;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.1);
}

.container.fullscreen {
  max-width: 100%;
  margin: 0;
  background: transparent;
  box-shadow: none;
}

.header {
  background: #4a5568;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.24);
  box-shadow: 0 6px 14px rgba(0,0,0,0.08);
}

.math-link {
  background: rgba(26, 115, 232, 0.2);
  border: 1px solid rgba(26, 115, 232, 0.4);
  color: #e8f0fe !important;
}

.math-link:hover {
  background: rgba(26, 115, 232, 0.3);
}

.admin-link {
  background: rgba(255, 215, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.4);
}

.admin-link:hover {
  background: rgba(255, 215, 0, 0.3);
}

.main {
  padding: 20px;
  min-height: calc(100vh - 140px);
}

.main.fullscreen {
  padding: 0;
  min-height: 100vh;
}

.footer {
  background: #e2e8f0;
  text-align: center;
  line-height: 40px;
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .container {
    max-width: 100%;
    margin: 0;
  }
  
  .main {
    padding: 10px;
  }
}
</style>
