<template>
  <div class="admin-panel">
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Setting /></el-icon>
          <span>对话管理系统</span>
        </div>
      </template>

      <!-- 功能导航 -->
      <el-tabs v-model="activeTab" class="admin-tabs">
        <!-- 用户管理 -->
        <el-tab-pane label="用户管理" name="users">
          <div class="users-section">
            <el-input
              v-model="userSearch"
              placeholder="搜索用户"
              prefix-icon="Search"
              class="search-input"
            />
            
            <el-table
              :data="filteredUsers"
              style="width: 100%"
              class="users-table"
              v-loading="loadingUsers"
              empty-text="暂无用户"
            >
              <el-table-column prop="username" label="用户名" width="200" />
              <el-table-column prop="created_at" label="创建时间" width="200">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="最后更新" width="200">
                <template #default="scope">
                  {{ formatDate(scope.row.updated_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button
                    type="primary"
                    size="small"
                    @click="viewUserChat(scope.row.username)"
                  >
                    查看对话
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    @click="deleteUser(scope.row.username)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 对话管理 -->
        <el-tab-pane label="对话管理" name="chats">
          <div class="chats-section">
            <el-select
              v-model="selectedUser"
              placeholder="选择用户"
              class="user-select"
              @change="loadUserChat"
            >
              <el-option
                v-for="user in users"
                :key="user.username"
                :label="user.username"
                :value="user.username"
              />
            </el-select>
            
            <el-table
              :data="userMessages"
              style="width: 100%"
              class="messages-table"
              v-loading="loadingMessages"
              empty-text="暂无消息"
            >
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="message_type" label="类型" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.message_type === 'user' ? 'primary' : 'success'">
                    {{ scope.row.message_type === 'user' ? '用户' : 'AI' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="content" label="内容">
                <template #default="scope">
                  <div class="message-content">{{ scope.row.content }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="timestamp" label="时间" width="200">
                <template #default="scope">
                  {{ formatDate(scope.row.timestamp) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button
                    type="danger"
                    size="small"
                    @click="deleteMessage(scope.row.id)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 数据统计 -->
        <el-tab-pane label="数据统计" name="stats">
          <div class="stats-section">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="stats-card">
                  <div class="stats-item">
                    <el-icon class="stats-icon"><User /></el-icon>
                    <div class="stats-info">
                      <div class="stats-value">{{ totalUsers }}</div>
                      <div class="stats-label">总用户数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="stats-card">
                  <div class="stats-item">
                    <el-icon class="stats-icon"><ChatDotRound /></el-icon>
                    <div class="stats-info">
                      <div class="stats-value">{{ totalMessages }}</div>
                      <div class="stats-label">总消息数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="stats-card">
                  <div class="stats-item">
                    <el-icon class="stats-icon"><TrendCharts /></el-icon>
                    <div class="stats-info">
                      <div class="stats-value">{{ activeUsers }}</div>
                      <div class="stats-label">活跃用户</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 消息类型分布 -->
            <el-card class="chart-card">
              <template #header>
                <div class="chart-header">
                  <el-icon><PieChart /></el-icon>
                  <span>消息类型分布</span>
                </div>
              </template>
              <div class="chart-container">
                <el-statistic
                  v-for="(item, index) in messageTypeStats"
                  :key="index"
                  class="stat-item"
                >
                  <template #title>{{ item.type === 'user' ? '用户消息' : 'AI 消息' }}</template>
                  <template #value>{{ item.count }}</template>
                  <template #suffix>{{ item.percentage }}%</template>
                </el-statistic>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 系统设置 -->
        <el-tab-pane label="系统设置" name="settings">
          <div class="settings-section">
            <el-form :model="systemSettings" class="settings-form">
              <el-form-item label="数据库状态" prop="dbStatus">
                <el-tag :type="dbStatus ? 'success' : 'danger'">
                  {{ dbStatus ? '连接正常' : '连接失败' }}
                </el-tag>
              </el-form-item>
              <el-form-item label="系统版本" prop="version">
                <el-input v-model="systemSettings.version" disabled />
              </el-form-item>
              <el-form-item label="清理数据" prop="cleanData">
                <el-button type="danger" @click="confirmCleanData">
                  <el-icon><Delete /></el-icon>
                  清空所有数据
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 确认对话框 -->
    <el-dialog
      v-model="confirmDialog.visible"
      :title="confirmDialog.title"
      width="400px"
    >
      <span>{{ confirmDialog.message }}</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="confirmDialog.visible = false">取消</el-button>
          <el-button type="danger" @click="confirmAction">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Setting, Search, User, ChatDotRound, TrendCharts,
  PieChart, Delete, ChatLineRound
} from '@element-plus/icons-vue'
import axios from 'axios'
import { getApiBaseUrl, getAuthHeaders, clearAdminToken } from '../utils/api'

// 响应式数据
const activeTab = ref('users')
const userSearch = ref('')
const selectedUser = ref('')
const users = ref([])
const userMessages = ref([])
const loadingUsers = ref(false)
const loadingMessages = ref(false)
const dbStatus = ref(true)
const totalUsers = ref(0)
const totalMessages = ref(0)
const activeUsers = ref(0)
const messageTypeStats = ref([])
const apiBase = getApiBaseUrl()
const router = useRouter()

const adminRequest = (config) => axios({
  ...config,
  headers: {
    ...getAuthHeaders(),
    ...(config.headers || {})
  }
})

const handleAuthError = (error) => {
  if (error?.response?.status === 401) {
    clearAdminToken()
    ElMessage.error('登录已失效，请重新登录')
    router.push('/login')
    return true
  }
  return false
}

// 系统设置
const systemSettings = ref({
  version: '1.0.0',
  dbStatus: true
})

// 确认对话框
const confirmDialog = ref({
  visible: false,
  title: '',
  message: '',
  action: null,
  params: null
})

// 过滤用户
const filteredUsers = computed(() => {
  if (!userSearch.value) {
    return users.value
  }
  return users.value.filter(user => 
    user.username.toLowerCase().includes(userSearch.value.toLowerCase())
  )
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 加载用户列表
const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await adminRequest({
      method: 'get',
      url: `${apiBase}/api/admin/users`
    })
    users.value = response.data
    totalUsers.value = users.value.length
    
    if (users.value.length === 0) {
      ElMessage.info('暂无用户数据')
    }
    
    // 获取统计数据
    await loadStats()
  } catch (error) {
    if (handleAuthError(error)) return
    console.error('加载用户失败:', error)
    
    let errorMsg = '加载用户失败'
    if (error.response?.status === 500) {
      errorMsg = '服务器错误，请稍后重试'
    } else if (error.request) {
      errorMsg = '网络连接失败'
    }
    
    ElMessage.error(errorMsg)
    users.value = []
    totalUsers.value = 0
  } finally {
    loadingUsers.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await adminRequest({
      method: 'get',
      url: `${apiBase}/api/admin/stats`
    })
    const statsData = response.data
    totalUsers.value = statsData.total_users
    totalMessages.value = statsData.total_messages
    activeUsers.value = statsData.active_users
    
    // 计算消息类型分布
    const userCount = statsData.message_types.user || 0
    const aiCount = statsData.message_types.ai || 0
    const total = userCount + aiCount
    
    messageTypeStats.value = [
      { type: 'user', count: userCount, percentage: total > 0 ? Math.round((userCount / total) * 100) : 0 },
      { type: 'ai', count: aiCount, percentage: total > 0 ? Math.round((aiCount / total) * 100) : 0 }
    ]
  } catch (error) {
    if (handleAuthError(error)) return
    console.error('加载统计数据失败:', error)
    
    let errorMsg = '加载统计数据失败'
    if (error.response?.status === 500) {
      errorMsg = '服务器错误'
    } else if (error.request) {
      errorMsg = '网络连接失败'
    }
    
    // 静默失败，不中断整体流程
    console.warn(errorMsg)
  }
}

// 加载用户对话
const loadUserChat = async () => {
  if (!selectedUser.value) return
  
  loadingMessages.value = true
  try {
    const response = await adminRequest({
      method: 'get',
      url: `${apiBase}/api/admin/user/${selectedUser.value}/messages`
    })
    userMessages.value = response.data
    totalMessages.value = userMessages.value.length
    
    if (userMessages.value.length === 0) {
      ElMessage.info('该用户暂无对话记录')
    }
    
    // 计算消息类型分布
    const userCount = userMessages.value.filter(msg => msg.message_type === 'user').length
    const aiCount = userMessages.value.filter(msg => msg.message_type === 'ai').length
    const total = userCount + aiCount
    
    messageTypeStats.value = [
      { type: 'user', count: userCount, percentage: total > 0 ? Math.round((userCount / total) * 100) : 0 },
      { type: 'ai', count: aiCount, percentage: total > 0 ? Math.round((aiCount / total) * 100) : 0 }
    ]
  } catch (error) {
    if (handleAuthError(error)) return
    console.error('加载对话失败:', error)
    
    let errorMsg = '加载对话失败'
    if (error.response?.status === 404) {
      errorMsg = '用户不存在或无对话记录'
    } else if (error.response?.status === 500) {
      errorMsg = '服务器错误'
    } else if (error.request) {
      errorMsg = '网络连接失败'
    }
    
    ElMessage.error(errorMsg)
    userMessages.value = []
  } finally {
    loadingMessages.value = false
  }
}

// 查看用户对话
const viewUserChat = (username) => {
  selectedUser.value = username
  activeTab.value = 'chats'
  loadUserChat()
}

// 删除用户
const deleteUser = (username) => {
  confirmDialog.value = {
    visible: true,
    title: '确认删除',
    message: `确定要删除用户 "${username}" 及其所有对话数据吗？此操作不可恢复。`,
    action: 'deleteUser',
    params: username
  }
}

// 删除消息
const deleteMessage = (messageId) => {
  confirmDialog.value = {
    visible: true,
    title: '确认删除',
    message: '确定要删除这条消息吗？此操作不可恢复。',
    action: 'deleteMessage',
    params: messageId
  }
}

// 确认清理数据
const confirmCleanData = () => {
  confirmDialog.value = {
    visible: true,
    title: '确认清理',
    message: '确定要清空所有数据吗？此操作不可恢复，将删除所有用户和对话记录。',
    action: 'cleanData',
    params: null
  }
}

// 执行确认操作
const confirmAction = async () => {
  const { action, params } = confirmDialog.value
  
  try {
    switch (action) {
      case 'deleteUser':
        await adminRequest({
          method: 'delete',
          url: `${apiBase}/api/admin/user/${params}`
        })
        ElMessage.success(`用户 "${params}" 已删除`)
        users.value = users.value.filter(user => user.username !== params)
        await loadStats()
        break
      case 'deleteMessage':
        await adminRequest({
          method: 'delete',
          url: `${apiBase}/api/admin/message/${params}`
        })
        ElMessage.success('消息已删除')
        userMessages.value = userMessages.value.filter(msg => msg.id !== params)
        await loadStats()
        break
      case 'cleanData':
        await adminRequest({
          method: 'delete',
          url: `${apiBase}/api/admin/clean`
        })
        ElMessage.success('所有数据已清空')
        users.value = []
        userMessages.value = []
        await loadStats()
        break
    }
  } catch (error) {
    if (handleAuthError(error)) return
    ElMessage.error('操作失败')
    console.error('操作失败:', error)
  } finally {
    confirmDialog.value.visible = false
  }
}

// 检查数据库状态
const checkDbStatus = () => {
  // 实际项目中检查数据库连接状态
  dbStatus.value = true
}

// 组件挂载
onMounted(() => {
  loadUsers()
  checkDbStatus()
})
</script>

<style scoped>
.admin-panel {
  padding: 24px;
  min-height: 600px;
  background: #f5f7fa;
}

.admin-card {
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.header-icon {
  font-size: 20px;
  color: #409EFF;
}

.admin-tabs {
  margin-top: 20px;
}

/* 用户管理 */
.users-section {
  padding: 20px 0;
}

.search-input {
  margin-bottom: 20px;
  width: 300px;
}

.users-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
}

/* 对话管理 */
.chats-section {
  padding: 20px 0;
}

.user-select {
  margin-bottom: 20px;
  width: 300px;
}

.messages-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.message-content {
  max-width: 400px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 数据统计 */
.stats-section {
  padding: 20px 0;
}

.stats-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stats-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  font-size: 40px;
  color: #4a5568;
}

.stats-value {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
}

.stats-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
  font-weight: 500;
}

.chart-card {
  margin-top: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.chart-container {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

/* 设置管理 */
.settings-section {
  padding: 20px 0;
}

.settings-form {
  max-width: 600px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-panel {
    padding: 10px;
  }
  
  .search-input,
  .user-select {
    width: 100%;
  }
  
  .chart-container {
    flex-direction: column;
    gap: 20px;
  }
  
  .stat-item {
    align-items: center;
  }
}
</style>
