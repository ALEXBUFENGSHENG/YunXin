<template>
  <div class="admin-view">
    <!-- 管理员导航 -->
    <div class="admin-nav">
      <div class="nav-left">
        <el-button type="primary" @click="goToChat" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回聊天
        </el-button>
      </div>
      <div class="nav-center">
        <h1 class="nav-title">AI 助教管理系统</h1>
      </div>
      <div class="nav-right">
        <el-dropdown>
          <el-button type="text" class="user-btn">
            <el-icon><UserFilled /></el-icon>
            管理员
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="logout">
                <el-icon><SwitchButton /></el-icon>
                退出
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 管理员面板 -->
    <AdminPanel />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, UserFilled, SwitchButton } from '@element-plus/icons-vue'
import { clearAdminToken } from '../utils/api'
import AdminPanel from '../components/AdminPanel.vue'

const router = useRouter()

// 返回聊天页面
const goToChat = () => {
  router.push('/')
}

// 退出登录
const logout = () => {
  clearAdminToken()
  ElMessage.success('已退出管理员模式')
  router.push('/login')
}
</script>

<style scoped>
.admin-view {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.admin-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.nav-left {
  flex: 1;
}

.nav-center {
  flex: 2;
  text-align: center;
}

.nav-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.nav-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-view {
    padding: 10px;
  }
  
  .admin-nav {
    padding: 12px 16px;
    flex-direction: column;
    gap: 12px;
  }
  
  .nav-left,
  .nav-center,
  .nav-right {
    flex: none;
    width: 100%;
    text-align: center;
  }
  
  .nav-right {
    justify-content: center;
  }
  
  .nav-title {
    font-size: 18px;
  }
}
</style>
