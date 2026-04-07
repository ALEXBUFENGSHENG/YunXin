<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo-area">
        <img :src="logoIcon" class="logo-icon-img" alt="Logo" />
        <span class="logo-text">知小云</span>
      </div>
      <button class="new-chat-btn" @click="emit('new-session')">
        <span class="icon">+</span> 新开启迪
      </button>
      <button class="chat-mode-btn" @click="emit('go-chat')">
        <span class="icon">💬</span> 返回对话
      </button>
      <button class="math-mode-btn" @click="emit('go-math')">
        <span class="icon">📐</span> 考研数学专栏
      </button>
    </div>

    <div class="history-list">
      <div class="group-title">学习会话</div>
      <div class="history-item active">
        <span class="history-title">{{ currentTopic || '当前学习任务' }}</span>
      </div>
    </div>

    <div class="user-profile">
      <div class="avatar">U</div>
      <div class="username">学习者</div>
      <div class="settings-icon">⚙️</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  logoIcon: {
    type: String,
    required: true
  },
  currentTopic: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['new-session', 'go-chat', 'go-math'])
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: rgba(15, 23, 42, 0.95);
  border-right: 1px solid rgba(148, 163, 184, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  backdrop-filter: blur(12px);
}

.sidebar-header {
  padding: 20px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  font-weight: 700;
  font-size: 18px;
  color: #f8fafc;
}

.logo-icon-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.new-chat-btn,
.chat-mode-btn,
.math-mode-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
}

.new-chat-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.new-chat-btn:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.chat-mode-btn:hover,
.math-mode-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.history-list {
  flex: 1;
  padding: 10px 16px;
  overflow-y: auto;
}

.group-title {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: #94a3b8;
  font-size: 14px;
  transition: all 0.2s;
}

.history-item.active {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}

.user-profile {
  padding: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.avatar {
  width: 28px;
  height: 28px;
  background: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
}

.username {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
}

.settings-icon {
  color: #64748b;
}
</style>
