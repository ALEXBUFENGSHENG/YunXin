<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand-panel">
        <div class="brand-logo">AI</div>
        <h1>管理员控制台</h1>
        <p>统一管理用户、对话与系统指标，确保运营稳定与安全。</p>
        <div class="brand-tags">
          <span>安全登录</span>
          <span>数据洞察</span>
          <span>权限保护</span>
        </div>
      </div>
      <div class="form-panel">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>请输入管理员账号以继续进入控制台。</p>
        </div>
        <el-alert
          v-if="errorMessage"
          class="error-alert"
          type="error"
          :closable="false"
          show-icon
        >
          {{ errorMessage }}
        </el-alert>
        <el-form :model="form" class="login-form" @keyup.enter="handleLogin">
          <el-form-item label="用户名">
            <el-input
              v-model="form.username"
              placeholder="输入管理员账号"
              size="large"
              clearable
            />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="输入密码"
              size="large"
              show-password
              clearable
            />
          </el-form-item>
        </el-form>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          登录管理后台
        </el-button>
        <div class="form-footer">
          <span>登录失败会自动提示原因</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { getApiBaseUrl, setAdminToken } from '../utils/api'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    errorMessage.value = '请输入用户名与密码'
    return
  }
  loading.value = true
  errorMessage.value = ''
  const baseUrl = getApiBaseUrl()

  try {
    const payload = new URLSearchParams()
    payload.append('username', form.value.username)
    payload.append('password', form.value.password)

    const response = await axios.post(`${baseUrl}/api/auth/login`, payload, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    setAdminToken(response.data.access_token)
    ElMessage.success('登录成功')
    router.push('/admin')
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value = '用户名或密码错误'
    } else if (error.request) {
      errorMessage.value = '网络连接失败，请稍后重试'
    } else {
      errorMessage.value = '登录失败，请检查输入信息'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: radial-gradient(circle at top, rgba(79, 70, 229, 0.2), transparent 55%),
    linear-gradient(135deg, #0f172a, #111827 60%, #1f2937);
  font-family: "PingFang SC", sans-serif;
}

.login-card {
  width: min(960px, 95vw);
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 30px 60px rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(18px);
}

.brand-panel {
  padding: 48px 40px;
  background: linear-gradient(160deg, rgba(79, 70, 229, 0.85), rgba(30, 41, 59, 0.8));
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.brand-logo {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 20px;
  background: rgba(255, 255, 255, 0.2);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.25);
}

.brand-panel h1 {
  font-size: 28px;
  margin: 0;
  font-weight: 600;
}

.brand-panel p {
  margin: 0;
  line-height: 1.6;
  color: rgba(226, 232, 240, 0.9);
}

.brand-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.brand-tags span {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.35);
  font-size: 12px;
  font-weight: 500;
}

.form-panel {
  padding: 48px 40px;
  background: rgba(248, 250, 252, 0.98);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 18px;
}

.form-header h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
  font-weight: 600;
}

.form-header p {
  margin: 8px 0 0;
  color: #64748b;
}

.error-alert {
  margin-bottom: 8px;
}

.login-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #1f2937;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.06);
}

.login-btn {
  width: 100%;
  border-radius: 12px;
  height: 48px;
  font-weight: 600;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  box-shadow: 0 12px 24px rgba(79, 70, 229, 0.35);
  border: none;
}

.login-btn:hover {
  transform: translateY(-1px);
}

.form-footer {
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}

@media (max-width: 860px) {
  .login-card {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    display: none;
  }
}
</style>
