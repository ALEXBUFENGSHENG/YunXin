<template>
  <div class="learning-chat">
    <div class="chat-header">
      <div class="header-info">
        <h3>深度学习模式</h3>
        <span class="status-dot"></span>
        <span class="status-text">{{ isAgentWorking ? `${currentWorkingAgent} 思考中...` : '就绪' }}</span>
      </div>
      <div class="header-actions">
        <button class="icon-btn" @click="emit('clear')" title="清空会话">
          <Trash2 :size="18" />
        </button>
      </div>
    </div>

    <div class="messages-container" ref="messagesRef">
      <div v-if="messages.length <= 1" class="empty-state">
        <div class="empty-content">
          <BrainCircuit :size="64" class="empty-icon" />
          <h2>开启深度学习之旅</h2>
          <p>输入你想学习的主题，AI 团队将为你拆解知识、规划路径。</p>

          <div class="presets">
            <button @click="handlePreset('用“深度思考链”拆解 TCP 三次握手')" class="preset-btn">
              <span>TCP 三次握手原理</span>
              <ChevronRight :size="14" />
            </button>
            <button @click="handlePreset('用“深度思考链”拆解 Redis 缓存穿透')" class="preset-btn">
              <span>Redis 缓存三大问题</span>
              <ChevronRight :size="14" />
            </button>
          </div>
        </div>
      </div>

      <div v-for="msg in messages" :key="msg.id" class="message-row" :class="msg.role === 'user' ? 'user' : 'ai'">
        <div class="message-avatar" :class="{ 'is-ai': msg.role !== 'user' }">
          <User v-if="msg.role === 'user'" :size="20" />
          <Bot v-else :size="20" />
        </div>
        <div class="message-content">
          <div class="message-sender">{{ msg.role === 'user' ? '你' : 'AI 教练' }}</div>
          <div class="message-bubble" :class="msg.role === 'user' ? 'user' : 'ai'">
            <div v-if="msg.role === 'assistant'" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
            <div v-else class="whitespace-pre-wrap">{{ msg.content }}</div>
          </div>
        </div>
      </div>

      <div v-if="isAgentWorking" class="thinking-indicator">
        <Loader2 :size="16" class="animate-spin" />
        <span>{{ currentWorkingAgent || '智能体' }} 正在生成...</span>
      </div>
    </div>

    <div class="input-wrapper">
      <div class="input-box">
        <textarea
          v-model="inputModel"
          class="chat-textarea"
          placeholder="输入学习主题..."
          @keydown.enter.prevent="handleEnter"
          :disabled="isLoading"
          rows="1"
        ></textarea>
        <button
          class="send-btn"
          :disabled="isLoading || !inputModel.trim()"
          @click="emit('send')"
        >
          <Send :size="18" />
        </button>
      </div>
      <div class="footer-tip">Shift + Enter 换行 · Enter 发送</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import {
  Send,
  User,
  Bot,
  Loader2,
  Trash2,
  BrainCircuit,
  ChevronRight
} from 'lucide-vue-next'
import { renderMarkdown } from '../../utils/markdown'
import 'github-markdown-css/github-markdown-light.css'
import 'katex/dist/katex.min.css'

const props = defineProps({
  messages: {
    type: Array,
    required: true
  },
  isAgentWorking: {
    type: Boolean,
    default: false
  },
  currentWorkingAgent: {
    type: String,
    default: ''
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'send', 'preset', 'clear'])

const inputModel = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})


const handleEnter = (e) => {
  if (!e.shiftKey) {
    if (props.isLoading || !inputModel.value.trim()) return;
    emit('send')
  }
}

const handlePreset = (text) => {
  if (props.isLoading) return; // Prevent preset click if loading
  emit('update:modelValue', text)
  emit('preset', text) // Parent component should handle this and trigger send if needed
  // Note: Parent component (LearningView) handles the preset event, 
  // sets the input, and then calls handleSend. 
  // We don't need to call send here directly to avoid double submission if parent does it.
  // But checking LearningView or useLearningActions might clarify.
  // Based on useLearningActions: applyPreset -> inputMessage = text -> handleSend()
  // So emitting 'preset' is enough if parent calls applyPreset.
}

const messagesRef = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(() => props.messages.length, scrollToBottom)
watch(() => props.messages[props.messages.length - 1]?.content, scrollToBottom, { deep: true })
</script>

<style scoped>
.learning-chat {
  width: 40%;
  min-width: 400px;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(0, 0, 0, 0.05);
  background: #fff;
  position: relative;
  z-index: 10;
}

.chat-header {
  height: 60px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  z-index: 10;
}

.header-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  margin-left: 8px;
}

.status-text {
  font-size: 12px;
  color: #64748b;
  margin-left: 4px;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #f1f5f9;
  color: #ef4444;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #fff;
  position: relative;
  z-index: 1;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.empty-content {
  text-align: center;
  max-width: 320px;
}

.empty-icon {
  color: #cbd5e1;
  margin-bottom: 16px;
}

.empty-content h2 {
  color: #1e293b;
  font-size: 18px;
  margin-bottom: 8px;
}

.empty-content p {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 24px;
}

.presets {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preset-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #475569;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateX(2px);
}

.message-row {
  display: flex;
  gap: 12px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
}

.message-avatar.is-ai {
  background: #3b82f6;
}

.message-row.user .message-avatar {
  background: #10b981;
}

.message-content {
  max-width: 85%;
  display: flex;
  flex-direction: column;
}

.message-row.user .message-content {
  align-items: flex-end;
}

.message-sender {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  word-break: break-word;
}

.message-bubble.ai {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #334155;
  border-top-left-radius: 2px;
}

.message-bubble.user {
  background: #3b82f6;
  color: white;
  border-top-right-radius: 2px;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f8fafc;
  border-radius: 8px;
  width: fit-content;
  font-size: 12px;
  color: #64748b;
  margin-left: 44px;
}

.input-wrapper {
  padding: 20px;
  border-top: 1px solid #f1f5f9;
  background: #fff;
}

.input-box {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 8px;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  transition: all 0.2s;
}

.input-box:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
}

.chat-textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  padding: 10px;
  font-size: 14px;
  outline: none;
  max-height: 120px;
  color: #1e293b;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #1e293b;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #334155;
}

.send-btn:disabled {
  background: #e2e8f0;
  cursor: not-allowed;
}

.footer-tip {
  text-align: center;
  font-size: 11px;
  color: #cbd5e1;
  margin-top: 8px;
}

:deep(.markdown-body) {
  font-size: 14px;
  background: transparent !important;
  color: #334155;
  position: relative;
  z-index: 1;
}

:deep(.markdown-body pre) {
  background: #f1f5f9;
  border-radius: 8px;
}
</style>
