<template>
  <div class="chat-layout">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="logo-area">
          <img :src="logoIcon" class="logo-icon-img" alt="Logo" />
          <span class="logo-text">知小云</span>
        </div>
        <button class="new-chat-btn" @click="createNewChat">
          <span class="icon">+</span> 新建对话
        </button>
        <button class="learn-mode-btn" @click="goToLearnMode">
          <span class="icon">🎓</span> 进入学习模式
        </button>
        <button class="math-mode-btn" @click="goToMathMode">
          <span class="icon">📐</span> 考研数学专栏
        </button>
        <button class="admin-entry-btn" @click="goToAdmin">
          <span class="icon">⚡</span> 管理后台
        </button>
      </div>

      <div class="history-list">
        <div class="history-group">
          <div class="group-title">最近</div>
          <div 
            v-for="chat in chatHistory" 
            :key="chat.id"
            class="history-item"
            :class="{ active: currentChatId === chat.id }"
            @click="switchChat(chat.id)"
          >
            <span class="history-title">{{ chat.title || '新对话' }}</span>
            <button class="delete-btn" @click.stop="deleteChat(chat.id)">×</button>
          </div>
        </div>
      </div>

      <div class="user-profile" @click="showUserInfoDialog = true">
        <div class="avatar">{{ displayUsername[0] || 'U' }}</div>
        <div class="username">{{ displayUsername }}</div>
        <div class="settings-icon">⚙️</div>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="main-chat">
      <!-- Chat Header -->
      <div class="chat-header">
        <div class="header-info">
          <h3>{{ displayUsername }}</h3>
          <span class="status-dot"></span>
          <el-tag size="small" type="success" effect="plain">{{ deepThinkingEnabled ? '深度思考' : '流式输出' }}</el-tag>
          <el-tag v-if="isStreaming" size="small" type="warning" effect="dark">生成中...</el-tag>
        </div>
        <div class="header-actions"></div>
      </div>

      <!-- Chat Messages -->
      <div class="messages-container" ref="messageArea">
        <div v-if="messages.length === 0" class="empty-state">
          <img :src="logoIcon" class="empty-logo-img" alt="Logo" />
          <h2>我叫知小云，你的课程助教</h2>
          <p>我可以帮你理解知识，解答课程疑问。</p>
        </div>

        <div v-for="(msg, index) in messages" :key="index" class="message-row" :class="msg.type">
          <div class="message-avatar" :class="{ 'is-ai': msg.type !== 'user' }">
            <span v-if="msg.type === 'user'">👤</span>
            <img v-else :src="logoIcon" class="avatar-img" alt="AI" />
          </div>
          <div class="message-content">
            <div class="message-sender">{{ msg.type === 'user' ? displayUsername : 'AI 助教' }}</div>
            <div class="message-bubble" :class="msg.type">
              <!-- Message Text (Markdown) -->
              <div 
                class="markdown-body" 
                v-html="renderMarkdown(msg.content)"
              ></div>
              
              <div v-if="msg.isStreaming" class="streaming-cursor"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-wrapper">
        <div class="input-box">
          <div class="input-tools">
            <SpeechInput 
              @recognition-complete="handleSpeechComplete"
              @recognition-update="handleSpeechUpdate"
              @recording-start="handleSpeechStart"
            />
            <el-button circle @click="showCallOverlay = true" title="实时通话" style="margin-right: 12px;">
              <el-icon><PhoneFilled /></el-icon>
            </el-button>
            <el-switch v-model="ttsEnabled" active-text="朗读回复" size="small" />
            <el-switch v-model="deepThinkingEnabled" active-text="深度思考" size="small" />
          </div>
          
          <textarea
            v-model="inputMessage"
            class="chat-textarea"
            placeholder="给知小云助教发送消息..."
            @keydown.enter.prevent="handleEnter"
            :disabled="loading || isStreaming"
            rows="1"
            ref="textareaRef"
          ></textarea>
          
          <button 
            class="send-btn" 
            :disabled="!inputMessage.trim() || (loading && !isStreaming)"
            @click="handleSend"
            :title="isStreaming ? '停止生成' : '发送消息'"
          >
            <span v-if="isStreaming">⏹</span>
            <span v-else>↑</span>
          </button>
        </div>
        <div class="footer-tip">
          内容由 AI 生成，请仔细甄别。
        </div>
      </div>
    </div>

    <!-- Call Overlay -->
    <CallOverlay 
      :visible="showCallOverlay" 
      :username="username"
      @close="showCallOverlay = false"
      @new-message="handleCallNewMessage"
    />

    <!-- Learn Drawer removed -->
    
    <!-- Dialogs -->
    <el-dialog v-model="showUserInfoDialog" title="设置" width="400px">
      <el-form label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="username" />
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import MarkdownIt from 'markdown-it'
import MarkdownItKatex from 'markdown-it-katex'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css' // Import a dark theme for code
import 'katex/dist/katex.min.css'
import SpeechInput from './SpeechInput.vue'
import CallOverlay from './CallOverlay.vue'
import { PhoneFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getApiBaseUrl, getAdminToken } from '../utils/api'
import logoIcon from '../assets/logo.png'

const HISTORY_KEY = 'ai-assistant-chat-history'

// Markdown Setup
const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
})
md.use(MarkdownItKatex)

// Custom renderer to handle protected formulas outside code blocks
const defaultRender = md.renderer.rules.text || function(tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

// 重写 renderMarkdown 方法，而不是修改 md 配置
const renderMarkdown = (text) => {
  if (!text) return ''
  
  // 1. 处理数学公式
  const formulaRegex = /\$\$([\s\S]*?)\$\$|\$((?:\\.|[^\\$])*)\$/g;
  const formulas = [];
  const protectedText = text.replace(formulaRegex, (match, display, inline) => {
    formulas.push({ display, inline, match });
    return `FORMULA-PLACEHOLDER-${formulas.length - 1}`;
  });

  // 2. 渲染 Markdown
  let html = md.render(protectedText);

  // 3. 还原并渲染公式
  html = html.replace(/FORMULA-PLACEHOLDER-(\d+)/g, (_, index) => {
    const { display, inline, match } = formulas[index];
    const formula = display || inline;
    const isDisplay = !!display;
    
    try {
      return katex.renderToString(formula, { 
        throwOnError: false, 
        displayMode: isDisplay 
      });
    } catch (e) {
      return match;
    }
  });

  return html;
}

// State
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const isStreaming = ref(false)
const ttsEnabled = ref(true)
const deepThinkingEnabled = ref(false)
const username = ref(localStorage.getItem('ai-assistant-username') || '访客')
const chatHistory = ref([]) // Mock history for now
const currentChatId = ref(null)
const useServerSessions = ref(true)
const showUserInfoDialog = ref(false)
const showCallOverlay = ref(false) // State for call overlay
const messageArea = ref(null)
const textareaRef = ref(null)
const streamingMessage = ref('')
let streamController = null
let currentStreamIndex = null
const requestAbortController = new AbortController()

// Computed
const displayUsername = computed(() => username.value || '访客')
const router = useRouter()

const goToAdmin = () => {
  const token = getAdminToken()
  router.push(token ? '/admin' : '/login')
}

const goToLearnMode = () => {
  router.push('/learn')
}

const goToMathMode = () => {
  router.push('/math')
}

// Helpers for history
const deriveTitle = (msgs = []) => {
  const firstUser = msgs.find(m => m.type === 'user')
  if (firstUser && firstUser.content) {
    const preview = firstUser.content.trim()
    return preview.length > 20 ? preview.slice(0, 20) + '...' : preview
  }
  return '新对话'
}

const loadHistoryFromStorage = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        chatHistory.value = parsed
      }
    }
  } catch (e) {
    console.error('加载历史失败', e)
  }
}

const persistHistory = () => {
  if (useServerSessions.value) return
  try {
    const limited = chatHistory.value.slice(0, 50)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(limited))
  } catch (e) {
    console.error('保存历史失败', e)
  }
}

const syncCurrentChatToHistory = (titleHint) => {
  if (!currentChatId.value) return
  const clonedMessages = messages.value.map(m => ({ ...m }))
  const payload = {
    id: currentChatId.value,
    title: titleHint || deriveTitle(clonedMessages),
    messages: clonedMessages
  }
  const idx = chatHistory.value.findIndex(c => c.id === currentChatId.value)
  if (idx >= 0) {
    chatHistory.value.splice(idx, 1)
  }
  chatHistory.value.unshift(payload)
  persistHistory()
}

const normalizeSession = (session) => ({
  id: session.id,
  title: session.name || '新对话',
  createdAt: session.created_at,
  messages: []
})

const loadSessionMessages = async (sessionId) => {
  const baseUrl = getApiBaseUrl()
  try {
    const response = await axios.get(`${baseUrl}/api/chat/sessions/${sessionId}/messages`, {
      params: { username: encodeURIComponent(username.value) },
      signal: requestAbortController.signal
    })
    const serverMessages = Array.isArray(response.data?.messages) ? response.data.messages : []
    return serverMessages.map(msg => ({
      type: msg.type === 'user' ? 'user' : 'ai',
      content: msg.content,
      conversation_id: sessionId,
      timestamp: msg.timestamp
    }))
  } catch (e) {
    if (axios.isCancel(e) || e.name === 'CanceledError') {
      return []
    }
    throw e
  }
}

const createLocalSession = () => {
  currentChatId.value = Date.now()
  messages.value = []
  const exists = chatHistory.value.findIndex(c => c.id === currentChatId.value)
  if (exists === -1) {
    chatHistory.value.unshift({ id: currentChatId.value, title: '新对话', messages: [] })
  }
  persistHistory()
}

const createSessionOnServer = async () => {
  const baseUrl = getApiBaseUrl()
  const response = await axios.post(`${baseUrl}/api/chat/sessions`, {
    username: username.value
  })
  return response.data
}

const fetchSessions = async () => {
  const baseUrl = getApiBaseUrl()
  try {
    const response = await axios.get(`${baseUrl}/api/chat/sessions`, {
      params: { username: encodeURIComponent(username.value) },
      signal: requestAbortController.signal
    })
    const sessions = Array.isArray(response.data?.sessions) ? response.data.sessions : []
    useServerSessions.value = true
    if (sessions.length) {
      chatHistory.value = sessions.map(normalizeSession)
      currentChatId.value = chatHistory.value[0].id
      messages.value = await loadSessionMessages(currentChatId.value)
    } else {
      await createNewChat()
    }
  } catch (e) {
    if (axios.isCancel(e) || e.name === 'CanceledError') {
      return
    }
    console.warn('服务端会话同步失败，回退本地', e)
    useServerSessions.value = false
    loadHistoryFromStorage()
    if (chatHistory.value.length) {
      currentChatId.value = chatHistory.value[0].id
      messages.value = chatHistory.value[0].messages ? chatHistory.value[0].messages.map(m => ({ ...m })) : []
    } else {
      createLocalSession()
    }
  }
}

// Methods
const playTextToSpeech = (text) => {
  const baseUrl = getApiBaseUrl()
  // Clean text for TTS: remove code blocks, markdown, emojis, etc.
  const cleanText = cleanTextForTTS(text)
  if (!cleanText) return
  
  const audio = new Audio(`${baseUrl}/api/speech/tts?text=${encodeURIComponent(cleanText)}`)
  audio.play().catch(e => console.error("TTS Playback failed:", e))
}

const cleanTextForTTS = (text) => {
  if (!text) return ''
  let clean = text

  // 1. Remove code blocks (```...```)
  clean = clean.replace(/```[\s\S]*?```/g, '')

  // 2. Remove HTML tags
  clean = clean.replace(/<[^>]*>/g, '')

  // 3. Remove images ![alt](url)
  clean = clean.replace(/!\[([^\]]*)\]\([^)]+\)/g, '')

  // 4. Replace Markdown links [text](url) with text
  clean = clean.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')

  // 5. Remove bold/italic markers (* or _)
  clean = clean.replace(/[*_]{1,3}([^*_]+)[*_]{1,3}/g, '$1')

  // 6. Remove headers markers (#)
  clean = clean.replace(/^#+\s+/gm, '')

  // 7. Remove blockquotes (>)
  clean = clean.replace(/^>\s+/gm, '')

  // 8. Remove inline code backticks (`)
  clean = clean.replace(/`([^`]+)`/g, '$1')
  
  // 9. Remove LaTeX formulas ($$...$$ and $...$) - usually hard to read by simple TTS
  clean = clean.replace(/\$\$[\s\S]*?\$\$/g, '')
  clean = clean.replace(/\$[^$]+\$/g, '')

  // 10. Remove Emojis
  clean = clean.replace(/[\u{1F300}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{1F600}-\u{1F64F}\u{2600}-\u{27BF}]/gu, '')
  
  // 11. Remove extra whitespace
  clean = clean.replace(/\s+/g, ' ').trim()

  return clean
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageArea.value) {
    messageArea.value.scrollTop = messageArea.value.scrollHeight
  }
}

// Auto-resize textarea
watch(inputMessage, () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
})

const handleEnter = (e) => {
  if (e.shiftKey) return
  handleSend()
}

const handleSend = async () => {
  const msg = inputMessage.value.trim()
  if (!msg) return

  // 如果正在流式，点击即停止
  if (isStreaming.value) {
    stopStreaming()
    return
  }

  if (loading.value) return
  
  messages.value.push({ 
    type: 'user', 
    content: msg,
    conversation_id: currentChatId.value,
    timestamp: new Date().toISOString()
  })
  syncCurrentChatToHistory()
  inputMessage.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  
  scrollToBottom()
  
  await sendMessageStream(msg)
}

const sendMessageStream = async (msg) => {
  loading.value = true
  isStreaming.value = true
  const baseUrl = getApiBaseUrl()
  
  // Ensure previous controller is aborted before starting new one
  if (streamController) {
    streamController.abort()
  }
  streamController = new AbortController()
  const signal = streamController.signal
  
  // Use object reference instead of index for stability
  const aiMessage = { 
    type: 'ai', 
    content: '', 
    isStreaming: true,
    conversation_id: currentChatId.value,
    timestamp: new Date().toISOString()
  }
  messages.value.push(aiMessage)
  // Get the reactive version from the array
  const activeMessage = messages.value[messages.value.length - 1]
  
  // We still track index for legacy compatibility with stopStreaming if needed, 
  // but we won't use it for updates
  currentStreamIndex = messages.value.length - 1
  
  try {
    const response = await fetch(`${baseUrl}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: msg,
        username: username.value,
        conversation_id: parseInt(currentChatId.value) || null,
        mode: 'chat',
        deep_thinking: deepThinkingEnabled.value
      }),
      signal
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    // Performance Optimization: Buffer updates to reduce render frequency
    let pendingContent = ''
    let lastUpdateTime = 0
    const UPDATE_INTERVAL = 100 // Update UI every 100ms
    
    const flushBuffer = () => {
      if (pendingContent) {
        activeMessage.content += pendingContent
        pendingContent = ''
        lastUpdateTime = Date.now()
        scrollToBottom()
      }
    }

    while (true) {
      const { value, done } = await reader.read()
      if (done) {
        flushBuffer() // Ensure remaining content is written
        break
      }
      
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      
      const lines = buffer.split('\n\n')
      buffer = lines.pop()
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6)
          try {
            const data = JSON.parse(jsonStr)
            if (data.type === 'chunk') {
              pendingContent += data.content
              
              // Check if it's time to update UI
              const now = Date.now()
              if (now - lastUpdateTime >= UPDATE_INTERVAL) {
                flushBuffer()
              }
            } else if (data.type === 'end') {
              flushBuffer() // Flush before ending
              isStreaming.value = false
              activeMessage.isStreaming = false
              if (ttsEnabled.value && data.full_response) {
                playTextToSpeech(data.full_response)
              }
              scrollToBottom()
            } else if (data.type === 'error') {
              flushBuffer()
              activeMessage.content += `\n[错误: ${data.message}]`
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e)
          }
        }
      }
    }
  } catch (error) {
    // Flush any pending content before showing error
    if (typeof flushBuffer === 'function') flushBuffer() // Safety check if defined
    
    if (error.name === 'AbortError') {
      activeMessage.content += '\n[已手动停止]'
    } else {
      activeMessage.content += `\n[网络错误: ${error.message}]`
    }
  } finally {
    loading.value = false
    isStreaming.value = false
    activeMessage.isStreaming = false
    syncCurrentChatToHistory()
    streamController = null
    currentStreamIndex = null
    scrollToBottom()
  }
}

// Speech Handlers
const handleSpeechComplete = (text) => {
  inputMessage.value = text
  handleSend()
}

const handleSpeechUpdate = (text) => {
  // Optional: show realtime preview
}

const handleSpeechStart = () => {
  // Optional: show recording state
}

const handleCallNewMessage = (msg) => {
  messages.value.push({
    ...msg,
    conversation_id: currentChatId.value,
    timestamp: new Date().toISOString()
  })
  syncCurrentChatToHistory()
  scrollToBottom()
}

const stopStreaming = () => {
  if (streamController) {
    // Only abort if we are actually streaming
    streamController.abort()
  }
  isStreaming.value = false
  loading.value = false
  
  if (currentStreamIndex !== null && messages.value[currentStreamIndex]) {
    messages.value[currentStreamIndex].isStreaming = false
  }
  
  // Do NOT clear streamController here if you want to reuse it, 
  // but usually we create a new one for each request.
  // The important part is making sure we don't abort a NEW request 
  // that might have just started.
  streamController = null
  currentStreamIndex = null
}

const createNewChat = async () => {
  if (messages.value.length && currentChatId.value) {
    syncCurrentChatToHistory()
  }
  if (useServerSessions.value) {
    try {
      const session = await createSessionOnServer()
      currentChatId.value = session.id
      messages.value = []
      const payload = normalizeSession(session)
      const exists = chatHistory.value.findIndex(c => c.id === session.id)
      if (exists >= 0) {
        chatHistory.value.splice(exists, 1)
      }
      chatHistory.value.unshift(payload)
      return
    } catch (e) {
      console.warn('创建服务端会话失败，回退本地', e)
      useServerSessions.value = false
      loadHistoryFromStorage()
    }
  }
  createLocalSession()
}

const deleteChat = async (id) => {
  if (useServerSessions.value) {
    const baseUrl = getApiBaseUrl()
    try {
      await axios.delete(`${baseUrl}/api/chat/sessions/${id}`, {
        params: { username: encodeURIComponent(username.value) }
      })
    } catch (e) {
      console.warn('删除服务端会话失败，回退本地', e)
      useServerSessions.value = false
    }
  }
  const idx = chatHistory.value.findIndex(c => c.id === id)
  if (idx !== -1) {
    chatHistory.value.splice(idx, 1)
    persistHistory()
  }
  if (currentChatId.value === id) {
    if (chatHistory.value.length) {
      const next = chatHistory.value[0]
      currentChatId.value = next.id
      if (useServerSessions.value) {
        messages.value = await loadSessionMessages(next.id)
      } else {
        messages.value = next.messages ? next.messages.map(m => ({ ...m })) : []
      }
    } else {
      await createNewChat()
    }
  }
}

const switchChat = async (id) => {
  syncCurrentChatToHistory()
  const target = chatHistory.value.find(c => c.id === id)
  if (target) {
    currentChatId.value = target.id
    if (useServerSessions.value) {
      try {
        messages.value = await loadSessionMessages(target.id)
      } catch (e) {
        console.warn('加载会话消息失败，回退本地', e)
        useServerSessions.value = false
        messages.value = target.messages ? target.messages.map(m => ({ ...m })) : []
      }
    } else {
      messages.value = target.messages ? target.messages.map(m => ({ ...m })) : []
    }
    scrollToBottom()
  }
}

onMounted(async () => {
  await fetchSessions()
})

onUnmounted(() => {
  // Only abort if we are actually loading or streaming
  if (loading.value || isStreaming.value) {
    requestAbortController.abort()
    if (streamController) {
      streamController.abort()
    }
  }
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  color: #e2e8f0;
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: rgba(15, 23, 42, 0.92);
  border-right: 1px solid rgba(148, 163, 184, 0.2);
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
  margin-bottom: 20px;
  font-weight: 600;
  font-size: 18px;
  color: #f8fafc;
}

.logo-icon-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.new-chat-btn {
  width: 100%;
  padding: 12px;
  background: rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s;
  color: #f8fafc;
  font-size: 15px;
  font-weight: 600;
}

.new-chat-btn:hover {
  background: rgba(148, 163, 184, 0.22);
  border-color: rgba(148, 163, 184, 0.4);
}

.learn-mode-btn {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: 1px solid rgba(59, 130, 246, 0.5);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s;
  color: white;
  font-size: 15px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.learn-mode-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
  filter: brightness(1.1);
}

.math-mode-btn {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: 1px solid rgba(16, 185, 129, 0.5);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s;
  color: white;
  font-size: 15px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
}

.math-mode-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(5, 150, 105, 0.3);
  filter: brightness(1.1);
}

.admin-entry-btn {
  width: 100%;
  margin-top: 10px;
  padding: 10px 12px;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.7), rgba(99, 102, 241, 0.6));
  border: 1px solid rgba(99, 102, 241, 0.5);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #f8fafc;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 10px 22px rgba(79, 70, 229, 0.25);
}

.admin-entry-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(79, 70, 229, 0.35);
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.group-title {
  font-size: 13px;
  color: #999;
  margin-bottom: 10px;
  padding-left: 8px;
}

.history-item {
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #cbd5f5;
  font-size: 15px;
}

.history-item:hover {
  background-color: rgba(148, 163, 184, 0.18);
}

.history-item.active {
  background-color: rgba(148, 163, 184, 0.28);
  font-weight: 600;
}

.delete-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  opacity: 0;
  font-size: 16px;
}

.history-item:hover .delete-btn {
  opacity: 1;
}

.user-profile {
  padding: 15px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #e2e8f0;
}

.user-profile:hover {
  background-color: rgba(148, 163, 184, 0.18);
}

.avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.username {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Main Chat */
.main-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: rgba(248, 250, 252, 0.96);
  border-left: 1px solid rgba(148, 163, 184, 0.2);
}

.chat-header {
  padding: 15px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(248, 250, 252, 0.86);
  backdrop-filter: blur(12px);
  z-index: 10;
  position: sticky;
  top: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-info h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #67c23a;
  border-radius: 50%;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Learn Drawer styles removed */

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 28px 24px 120px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.98) 0%, rgba(239, 246, 255, 0.9) 100%);
}

.empty-state {
  margin-top: 10vh;
  text-align: center;
  color: #666;
}

.empty-logo-img {
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
  object-fit: contain;
}

.message-row {
  display: flex;
  gap: 16px;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
}

.message-avatar {
  width: 38px;
  height: 38px;
  background: #f0f0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-row.user .message-avatar {
  background: #e0e0ff;
}

.message-content {
  flex: 1;
  min-width: 0;
  line-height: 1.6;
}

.message-bubble {
  background: #f7f9fb;
  border: 1px solid #edf1f6;
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.03);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.message-bubble.user {
  background: #eef4ff;
  border-color: #dbe6ff;
}

.message-bubble.ai {
  background: #f9fafc;
}

.message-row:hover .message-bubble {
  transform: translateY(-1px);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.05);
}

.message-sender {
  font-size: 13px;
  color: #999;
  margin-bottom: 4px;
}

/* Markdown Styles */
:deep(.markdown-body) {
  font-size: 16px;
  color: #24292e;
}

:deep(.markdown-body pre) {
  background-color: #1e1e1e;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin: 10px 0;
}

:deep(.markdown-body code) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
}

:deep(.markdown-body p) {
  margin-bottom: 10px;
}

/* Input Area */
.input-wrapper {
  max-width: 980px;
  width: 100%;
  margin: 0 auto;
  padding: 24px 24px 30px;
  position: sticky;
  bottom: 0;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0) 0%, rgba(248, 250, 252, 0.9) 30%, rgba(248, 250, 252, 1) 100%);
  z-index: 9;
}

.input-box {
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 18px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
}

.input-box:focus-within {
  border-color: rgba(59, 130, 246, 0.7);
  background: #fff;
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.18);
  transform: translateY(-1px);
}

.chat-textarea {
  width: 100%;
  border: none;
  background: transparent;
  resize: none;
  outline: none;
  font-size: 16px;
  line-height: 1.6;
  max-height: 200px;
  font-family: inherit;
  color: #1e293b;
}

.input-tools {
  display: flex;
  align-items: center;
  gap: 14px;
}

.send-btn {
  align-self: flex-end;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s ease, box-shadow 0.2s;
  box-shadow: 0 10px 18px rgba(37, 99, 235, 0.35);
  font-size: 18px;
}

.send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 16px 26px rgba(37, 99, 235, 0.45);
}

.send-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.footer-tip {
  text-align: center;
  font-size: 13px;
  color: #999;
  margin-top: 10px;
}

/* Streaming Cursor */
.streaming-cursor {
  display: inline-block;
  width: 6px;
  height: 16px;
  background: #333;
  animation: blink 1s step-end infinite;
  vertical-align: middle;
  margin-left: 4px;
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
