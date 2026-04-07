<!-- CallOverlay.vue -->
<template>
  <div class="call-overlay" v-if="visible">
    <!-- 背诵小达人独立界面 -->
    <div class="recitation-interface" v-if="isRecitationMode">
      <!-- 顶部导航栏 -->
      <div class="recitation-header">
        <div class="header-left" @click="exitRecitationMode">
          <el-icon class="back-icon"><ArrowLeft /></el-icon>
          <span>退出背诵</span>
        </div>
        <div class="header-title">
          <el-icon><Reading /></el-icon> 背诵小达人
        </div>
        <div class="header-right">
           <!-- 占位，保持标题居中 -->
           <span class="progress-badge">{{ recitationIndex + 1 }}/{{ memoryWords.length }}</span>
        </div>
      </div>

      <!-- 核心内容区 -->
      <div class="recitation-content" v-if="currentRecitationWord">
        
        <!-- 进度条 -->
        <div class="progress-bar-container">
          <div class="progress-bar-track">
            <div class="progress-bar-fill" :style="{ width: ((recitationIndex + 1) / memoryWords.length * 100) + '%' }"></div>
          </div>
        </div>

        <!-- 顶部设置栏 (跟读模式 & 纠音开关) -->
        <div class="recitation-settings">
           <div class="setting-item">
             <span class="label">AI跟读语速:</span>
             <el-radio-group v-model="shadowingSpeed" size="small" @change="updateShadowingSpeed">
               <el-radio-button label="-20%">慢速</el-radio-button>
               <el-radio-button label="+0%">常速</el-radio-button>
               <el-radio-button label="+20%">快速</el-radio-button>
             </el-radio-group>
           </div>
           <div class="setting-item">
             <el-switch 
               v-model="voiceCorrectionEnabled" 
               active-text="语音纠正" 
               inactive-text="关闭纠正"
               size="small"
               @change="updateCorrectionState"
             />
           </div>
        </div>

        <!-- 单词卡片 -->
        <div class="word-card-container">
          <div class="word-card" @click="playCurrentWord">
            <div class="word-main-text">{{ currentRecitationWord.word }}</div>
            <div class="word-pron-text">
              <el-icon><Microphone /></el-icon> {{ currentRecitationWord.pronunciation }}
            </div>
            <div class="word-hint-text">点击卡片朗读</div>
          </div>
        </div>
        
        <!-- AI 互动区 -->
        <div class="ai-interaction-container">
          <div class="ai-avatar-wrapper" :class="{ 'speaking': status === 'speaking' }">
             <img :src="status === 'speaking' ? humanTalking : humanIdle" alt="AI" />
          </div>
          <div class="ai-chat-bubble">
             <div class="bubble-content">
               <p v-if="transcript">{{ transcript }}</p>
               <p v-else class="placeholder">正在准备教学内容...</p>
             </div>
             <div class="bubble-tail"></div>
          </div>
        </div>
      </div>

      <!-- 底部操作区 -->
      <div class="recitation-footer">
        <div class="recitation-actions">
          <el-button 
            class="recitation-btn forget" 
            @click="submitRecitationReview(1)"
            :loading="memoryActionLoading"
          >😫 忘记</el-button>
          <el-button 
            class="recitation-btn fuzzy" 
            @click="submitRecitationReview(3)"
            :loading="memoryActionLoading"
          >🤔 模糊</el-button>
          <el-button 
            class="recitation-btn know" 
            @click="submitRecitationReview(5)"
            :loading="memoryActionLoading"
          >😎 认识</el-button>
        </div>
        <el-button 
          class="next-word-btn" 
          @click="nextRecitationWord"
          :loading="status === 'processing'"
        >
          <span>跳过</span>
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 常规通话界面 -->
    <template v-else>
      <!-- 主通话区域（左侧） -->
      <div class="call-main-area">
      <div class="call-header">
        <div class="signal-icon">
          <div class="bar" v-for="i in 4" :key="i" :class="{ active: i <= 3 }"></div>
        </div>
        <span class="carrier">知小云 · 通话中</span>
        <el-button 
          circle 
          size="small" 
          class="toggle-sidebar-btn"
          @click="isSidebarCollapsed = !isSidebarCollapsed"
          :title="isSidebarCollapsed ? '展开记忆面板' : '收起记忆面板'"
        >
          <el-icon><Reading /></el-icon>
        </el-button>
      </div>

      <div class="call-center">
        <div class="avatar-container" :class="{ 'speaking': status === 'speaking', 'listening': status === 'listening' }">
          <div class="digital-human-wrapper">
            <img :src="status === 'speaking' ? humanTalking : humanIdle" class="digital-human-img" alt="Digital Human" />
          </div>
          <div class="listening-waves" v-if="status === 'listening'">
            <span class="wave wave-1"></span>
            <span class="wave wave-2"></span>
            <span class="wave wave-3"></span>
          </div>
        </div>
        
        <!-- 音频波形可视化 -->
        <div class="waveform-container" v-show="status === 'listening'">
           <canvas ref="waveformCanvas" width="200" height="40"></canvas>
        </div>

        <h2 class="status-text">{{ statusText }}</h2>
        <p class="sub-status" v-if="transcript">{{ transcript }}</p>
      </div>

      <div class="call-controls">
        <div class="control-btn mute-btn" @click="toggleMute">
          <el-icon :size="24"><component :is="isMuted ? Mute : Microphone" /></el-icon>
          <span>{{ isMuted ? '取消静音' : '静音' }}</span>
        </div>
        
        <!-- 手动结束说话按钮 (仅在 Listening 状态显示) -->
        <div 
          class="control-btn finish-speaking-btn" 
          v-if="status === 'listening'"
          @click="manualFinishSpeaking"
        >
          <div class="btn-circle">
             <el-icon :size="24"><VideoPause /></el-icon>
          </div>
          <span>我说完了</span>
        </div>

        <div class="control-btn end-call-btn" @click="endCall">
          <el-icon :size="32"><PhoneFilled /></el-icon>
        </div>
      </div>
    </div>

    <!-- 右侧记忆边栏 -->
    <aside class="memory-sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
        <el-icon><Reading /></el-icon>
        <span v-if="!isSidebarCollapsed">今日记忆</span>
        <el-tooltip 
          v-else 
          content="点击展开记忆面板" 
          placement="left"
        >
          <span class="collapsed-badge">{{ memoryWords.length || 0 }}</span>
        </el-tooltip>
      </div>

      <div class="sidebar-content" v-if="!isSidebarCollapsed">
        <div class="memory-stats-card">
          <div class="stat-item">
            <div class="stat-value">{{ memoryWords.length }}</div>
            <div class="stat-label">待复习</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">{{ memoryProgress?.mastered_words || 0 }}</div>
            <div class="stat-label">已掌握</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">{{ avgMemoryStrength }}</div>
            <div class="stat-label">记忆强度</div>
          </div>
        </div>

        <div style="margin-bottom: 20px">
          <el-button type="primary" style="width: 100%" @click="startRecitationMode">
            <el-icon style="margin-right: 5px"><Microphone /></el-icon>
            进入背诵小达人
          </el-button>
        </div>

        <div class="current-word-section">
          <h4>当前单词</h4>
          <!-- Recitation Mode Controls -->
          <div v-if="isRecitationMode" class="recitation-controls" style="margin-bottom: 15px;">
             <div class="recitation-word-display" v-if="currentRecitationWord">
               <h3 style="margin: 0; font-size: 24px;">{{ currentRecitationWord.word }}</h3>
               <span style="opacity: 0.8">{{ currentRecitationWord.pronunciation }}</span>
             </div>
             <el-button type="success" @click="nextRecitationWord" style="width: 100%; margin-top: 10px;">
               下一个单词 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
             </el-button>
          </div>

          <div class="memory-card" v-if="memoryLoading">
            <p>记忆任务加载中...</p>
          </div>
          <div class="memory-card" v-else-if="memoryError">
            <p>{{ memoryError }}</p>
            <el-button size="small" type="primary" @click="fetchMemoryData">重试</el-button>
          </div>
          <div class="memory-card" v-else-if="currentMemoryWord">
            <div class="word-top">
              <div class="word-main">
                <div class="word-text">
                  {{ currentMemoryWord.word }}
                  <span class="word-tag" v-if="currentMemoryWord.is_new">新词</span>
                </div>
                <div class="word-pron" v-if="currentMemoryWord.pronunciation">{{ currentMemoryWord.pronunciation }}</div>
              </div>
            </div>
            <div class="word-def">{{ currentMemoryWord.definition || '暂无释义' }}</div>
            <div class="word-example" v-if="currentMemoryWord.example_sentence">{{ currentMemoryWord.example_sentence }}</div>
          <div class="memory-actions">
            <el-button 
              size="small" 
              @click="submitMemoryReview(1)" 
              :loading="memoryActionLoading"
              class="action-btn forget"
            >😫 忘记</el-button>
            <el-button 
              size="small" 
              @click="submitMemoryReview(3)" 
              :loading="memoryActionLoading"
              class="action-btn fuzzy"
            >🤔 模糊</el-button>
            <el-button 
              size="small" 
              @click="submitMemoryReview(5)" 
              :loading="memoryActionLoading"
              class="action-btn know"
            >😎 认识</el-button>
          </div>

          </div>
          <div class="memory-card empty-card" v-else>
            <p>🎉 今日任务完成！</p>
            <el-button size="small" @click="fetchMemoryData">再来一组</el-button>
          </div>
        </div>

        <div class="word-queue-section" v-if="memoryWords.length > 1">
          <h4>后续单词 ({{ memoryWords.length - 1 }})</h4>
          <div class="queue-list">
            <div 
              v-for="(word, idx) in memoryWords.slice(1, 5)" 
              :key="word.word_id || idx"
              class="queue-item"
              @click="switchToWord(idx + 1)"
            >
              <span class="queue-word">{{ word.word }}</span>
              <span class="queue-pron" v-if="word.pronunciation">{{ word.pronunciation }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="sidebar-collapsed-hint" v-else @click="isSidebarCollapsed = false">
        <el-icon><ArrowLeft /></el-icon>
        <span>展开</span>
      </div>
    </aside>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Microphone, Mute, PhoneFilled, Reading, ArrowLeft, ArrowRight, VideoPause } from '@element-plus/icons-vue'
import { ElMessage, ElTooltip } from 'element-plus'
import axios from 'axios'
import { getApiBaseUrl } from '../utils/api'
import humanIdle from '../assets/human-idle.png'
import humanTalking from '../assets/human.gif'
import { useLearningStore } from '../stores/learningStore'

const props = defineProps({
  visible: Boolean,
  username: String
})

const store = useLearningStore()
const emit = defineEmits(['close', 'new-message'])

// 状态: idle, listening, processing, speaking
const status = ref('idle')
const transcript = ref('')
const isMuted = ref(false)
const processingSpeech = ref(false)
const voiceHistory = ref([]) // 记忆最近用户语音内容
const isSidebarCollapsed = ref(false) // 侧边栏折叠状态
const isRecitationMode = ref(false)
const allowInterrupt = ref(true)
const interruptSignal = ref(false)
const shadowingSpeed = ref('+0%')
const voiceCorrectionEnabled = ref(true)

let ws = null
const audioQueue = ref([])
const isPlaying = ref(false)
const waveformCanvas = ref(null) // 画布引用
let animationFrameId = null

const resolveWsUrl = () => {
  const baseUrl = getApiBaseUrl()
  if (baseUrl) {
    const normalized = baseUrl.startsWith('http') ? baseUrl : `${window.location.origin}${baseUrl}`
    const url = new URL(normalized)
    const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${wsProtocol}//${url.host}/ws/duplex`
  }
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const hostname = window.location.hostname
  let port = window.location.port
  if (port === '3000') port = '8000'
  return `${wsProtocol}//${hostname}${port ? `:${port}` : ''}/ws/duplex`
}

const initWebSocket = () => {
  const wsUrl = resolveWsUrl()
  console.log('Connecting to WS:', wsUrl)
  ws = new WebSocket(wsUrl)
  ws.binaryType = 'arraybuffer'
  
  ws.onopen = () => {
    console.log('WS Connected')
    reconnectAttempts = 0
  }
  
  ws.onmessage = handleWebSocketMessage
  
  ws.onclose = (event) => {
    console.log('WS Closed', event.code, event.reason)
    // 尝试重连 (最多5次)
    if (status.value !== 'idle' && reconnectAttempts < 5) {
      reconnectAttempts++
      console.log(`Attempting reconnect ${reconnectAttempts}...`)
      setTimeout(initWebSocket, 2000)
    }
  }

  ws.onerror = (err) => {
    console.error('WS Error', err)
  }
}

let reconnectAttempts = 0

const handleWebSocketMessage = (event) => {
  try {
    const data = JSON.parse(event.data)
    
    if (data.type === 'asr_partial') {
      if (status.value === 'listening' || status.value === 'speaking') {
        transcript.value = data.text
      }
    } else if (data.type === 'user_commit') {
      transcript.value = data.text
      emit('new-message', { type: 'user', content: data.text })
      status.value = 'processing'
    } else if (data.type === 'llm_start') {
      status.value = 'speaking'
      transcript.value = '小云正在思考...'
      audioQueue.value = [] // 准备接收新音频
    } else if (data.type === 'llm_partial') {
      // 流式文本更新，如果还没播放音频，可以先更新文本
      if (status.value === 'speaking' && !isPlaying.value) {
         transcript.value += data.text
      }
    } else if (data.type === 'llm_result') {
      const text = data.text
      emit('new-message', { type: 'ai', content: text })
      // transcript.value = text // 最终文本由播放器按句显示
    } else if (data.type === 'tts_audio') {
      const audioData = data.data 
      const text = data.text
      
      const binary = atob(audioData)
      const array = new Uint8Array(binary.length)
      for(let i=0; i<binary.length; i++) array[i] = binary.charCodeAt(i)
      const blob = new Blob([array], { type: 'audio/mpeg' })
      const url = URL.createObjectURL(blob)
      
      audioQueue.value.push({ url, text })
      if (!isPlaying.value) {
        playAudioQueue()
      }
    } else if (data.type === 'tts_end') {
      // AI 说话结束逻辑在 playAudioQueue 完成后处理
      console.log('AI TTS 传输完成')
    } else if (data.type === 'interrupt') {
       // 服务端 VAD 检测到打断
       console.log('收到服务端打断指令')
       interruptAIPlayback()
    } else if (data.type === 'error') {
      ElMessage.error(data.message || '通信出错')
      status.value = 'listening'
    } else if (data.type === 'status') {
       // 后端推送的状态更新
       status.value = data.status
       transcript.value = data.text
    } else if (data.type === 'agent_start') {
       // 智能体开始工作
       console.log('[CallOverlay] Received agent_start:', data); // DEBUG LOG
       store.setAgentStatus(data.agent, data.status)
    } else if (data.type === 'agent_data') {
       // 智能体产出数据
       console.log('[CallOverlay] Received agent_data:', data); // DEBUG LOG
       store.updateAgentData(data.agent, data.data)
    }
  } catch (e) {
    console.error('WS Message Error', e)
  }
}

const playAudioQueue = async () => {
  if (isPlaying.value || audioQueue.value.length === 0) {
    // 如果播放结束且队列已空，恢复监听状态
    if (!isPlaying.value && status.value === 'speaking') {
      status.value = 'listening'
      transcript.value = '轮到你了...'
      isSpeaking = false
      silenceStart = null
    }
    return
  }
  
  isPlaying.value = true
  const item = audioQueue.value.shift()
  
  audioPlayer.src = item.url
  transcript.value = item.text
  
  try {
    await audioPlayer.play()
    audioPlayer.onended = () => {
      isPlaying.value = false
      URL.revokeObjectURL(item.url) // 释放内存
      playAudioQueue()
    }
    audioPlayer.onerror = () => {
        isPlaying.value = false
        URL.revokeObjectURL(item.url)
        playAudioQueue()
    }
  } catch (e) {
    console.error('Play error', e)
    isPlaying.value = false
    URL.revokeObjectURL(item.url)
    playAudioQueue()
  }
}


const memoryUserId = computed(() => {
  const base = props.username || 'guest'
  let hash = 0
  for (let i = 0; i < base.length; i++) {
    hash = (hash * 31 + base.charCodeAt(i)) >>> 0
  }
  return (hash % 100000) + 1
})

watch(() => props.username, () => {
  if (props.visible) {
    fetchMemoryData()
  }
})
const memoryWords = ref([])
const memoryLoading = ref(false)
const memoryError = ref('')
const memoryActionLoading = ref(false)
const currentMemoryIndex = ref(0)
const memoryProgress = ref(null)
const currentMemoryWord = computed(() => memoryWords.value[currentMemoryIndex.value] || null)
const avgMemoryStrength = computed(() => {
  const val = memoryProgress.value?.avg_memory_strength
  return typeof val === 'number' && !Number.isNaN(val) ? val.toFixed(2) : '0.00'
})

// Audio Context 相关
let audioContext = null
let mediaStream = null
let analyser = null
let microphone = null
let scriptProcessor = null

// VAD 参数
const VAD_THRESHOLD = 0 // 彻底交给服务端 VAD，前端只负责传输
const SILENCE_DURATION = 5000 // 前端不再主动提交，由服务端控制
let silenceStart = null
let isSpeaking = false
let audioChunks = []

// 播放器
const audioPlayer = new Audio()

const statusText = computed(() => {
  switch (status.value) {
    case 'idle': return '准备就绪'
    case 'listening': return '正在听你说...'
    case 'processing': return '思考中...'
    case 'speaking': return '小云飞奔来回复...'
    default: return ''
  }
})

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    startCall()
  } else {
    stopCall()
  }
})

const refreshProgress = async () => {
  try {
    const baseUrl = getApiBaseUrl()
    const res = await axios.get(`${baseUrl}/api/memory/progress/${memoryUserId.value}`)
    memoryProgress.value = res.data || {}
  } catch (e) {
    console.warn('刷新记忆进度失败', e)
  }
}

const fetchMemoryData = async () => {
  memoryLoading.value = true
  memoryError.value = ''
  try {
    const baseUrl = getApiBaseUrl()
    console.log('Fetching memory data from:', baseUrl)
    
    const [queueRes, progressRes] = await Promise.all([
      axios.get(`${baseUrl}/api/memory/today/${memoryUserId.value}?limit=12`),
      axios.get(`${baseUrl}/api/memory/progress/${memoryUserId.value}`)
    ])
    
    console.log('Memory data received:', queueRes.data)
    memoryWords.value = queueRes.data || []
    currentMemoryIndex.value = 0
    memoryProgress.value = progressRes.data || {}
  } catch (e) {
    console.error('记忆任务加载失败 details:', e)
    if (e.response) {
       console.error('Response status:', e.response.status)
       console.error('Response data:', e.response.data)
    }
    memoryError.value = `单词记忆任务加载失败: ${e.message}`
  } finally {
    memoryLoading.value = false
  }
}

const submitRecitationReview = async (score) => {
  if (!currentRecitationWord.value) return
  
  // 1. 提交复习记录
  await submitMemoryReview(score, currentRecitationWord.value)
  
  // 2. 自动切换到下一个（因为 submitMemoryReview 已经从列表中移除了当前单词）
  // 此时 recitationIndex 指向的已经是"下一个"单词了（因为数组前移了）
  // 但为了安全起见，我们检查一下是否越界
  if (memoryWords.value.length === 0) {
    ElMessage.success('今日单词已全部学完！')
    exitRecitationMode()
  } else {
    // 保持 index 不变，因为数组 shift 了，新单词自动补位到当前 index
    // 但如果 recitationIndex > 0，我们需要决定是继续往后还是回退
    // 简单策略：始终保持 index 指向当前位置，或者重置为 0 如果我们总是处理头部
    // 之前的逻辑是 splice(currentMemoryIndex, 1)
    
    // 如果 recitationIndex 超过了新数组长度，重置为 0
    if (recitationIndex.value >= memoryWords.value.length) {
      recitationIndex.value = 0
    }
    
    // 触发新单词教学
    triggerAIForCurrentWord()
  }
}

const submitMemoryReview = async (score, wordObj = null) => {
  const word = wordObj || currentMemoryWord.value
  if (!word) {
    ElMessage.info('今日任务已经完成')
    return
  }
  
  // 查找该单词在数组中的真实索引（防止 index 错位）
  const realIndex = memoryWords.value.findIndex(w => w.word_id === word.word_id)
  if (realIndex === -1) return

  memoryActionLoading.value = true
  try {
    const baseUrl = getApiBaseUrl()
    await axios.post(`${baseUrl}/api/memory/review`, {
      user_id: memoryUserId.value,
      word_id: word.word_id,
      score,
      interaction_type: 'call_overlay'
    })
    ElMessage.success('已记录复习')
    
    // 从列表中移除
    memoryWords.value.splice(realIndex, 1)
    
    // 刷新进度
    refreshProgress()
    
    // 如果是在普通模式（非背诵模式），更新索引以显示下一个
    if (!isRecitationMode.value) {
       if (currentMemoryIndex.value >= memoryWords.value.length) {
         currentMemoryIndex.value = 0
       }
    }
    
  } catch (e) {
    console.error('记录复习失败', e)
    ElMessage.error('记录失败，请重试')
  } finally {
    memoryActionLoading.value = false
  }
}

// 切换单词
const switchToWord = (index) => {
  currentMemoryIndex.value = index
}

// 启动通话
const startCall = async () => {
  try {
    status.value = 'idle'
    transcript.value = '正在连接麦克风...'
    await initAudio()
    initWebSocket()
    status.value = 'listening'
    transcript.value = '请开始说话'
    ElMessage.success('通话已接通')
    fetchMemoryData()
  } catch (e) {
    console.error('无法启动通话', e)
    const errorMsg = e.name === 'NotAllowedError' 
      ? '麦克风权限被拒绝，请在浏览器设置中允许访问'
      : e.name === 'NotFoundError'
      ? '未检测到麦克风设备'
      : '无法访问麦克风，请检查设备连接'
    ElMessage.error(errorMsg)
    transcript.value = errorMsg
    setTimeout(() => emit('close'), 2000)
  }
}

// 结束通话
const endCall = () => {
  stopCall()
  emit('close')
}

// 停止资源
const stopCall = () => {
  status.value = 'idle'
  interruptSignal.value = false
  
  if (scriptProcessor) scriptProcessor.disconnect()
  if (microphone) microphone.disconnect()
  if (analyser) analyser.disconnect()
  
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
  
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
  
  if (ws) {
    ws.close()
    ws = null
  }
  
  audioPlayer.pause()
  audioPlayer.currentTime = 0
}

// 初始化音频
const initAudio = async () => {
  mediaStream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
          sampleRate: 16000
      } 
  })
  
  // 确保 AudioContext 已经恢复 (Chrome 策略可能导致 suspended)
  audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 })
  if (audioContext.state === 'suspended') {
      await audioContext.resume()
  }
  
  analyser = audioContext.createAnalyser()
  analyser.fftSize = 2048
  microphone = audioContext.createMediaStreamSource(mediaStream)
  scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1)
  
  microphone.connect(analyser)
  analyser.connect(scriptProcessor)
  scriptProcessor.connect(audioContext.destination)
  
  scriptProcessor.onaudioprocess = handleAudioProcess
  
  // 启动波形绘制
  drawWaveform()
}

// 绘制波形图
const drawWaveform = () => {
  if (!analyser || !waveformCanvas.value) return
  
  const canvas = waveformCanvas.value
  const ctx = canvas.getContext('2d')
  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  
  const draw = () => {
    animationFrameId = requestAnimationFrame(draw)
    
    // 如果不在 listening 状态，清空画布或暂停绘制
    if (status.value !== 'listening') {
       ctx.clearRect(0, 0, canvas.width, canvas.height)
       return
    }

    analyser.getByteTimeDomainData(dataArray)
    
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.lineWidth = 2
    ctx.strokeStyle = '#4ade80' // 绿色波形
    ctx.beginPath()
    
    const sliceWidth = canvas.width * 1.0 / bufferLength
    let x = 0
    
    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0 // 归一化到 0-2
      const y = v * canvas.height / 2
      
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
      
      x += sliceWidth
    }
    
    ctx.lineTo(canvas.width, canvas.height / 2)
    ctx.stroke()
  }
  
  draw()
}

// VAD 与录音逻辑
const handleAudioProcess = (event) => {
  const canListen = status.value === 'listening' || (status.value === 'speaking' && allowInterrupt.value)
  if (!canListen || isMuted.value) return
  
  const inputData = event.inputBuffer.getChannelData(0)
  
  // 1. 简单的音量检测 (仅用于决定是否发送数据以节省带宽)
  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  analyser.getByteFrequencyData(dataArray)
  
  let sum = 0
  for(let i = 0; i < bufferLength; i++) {
    sum += dataArray[i]
  }
  const average = sum / bufferLength
  
  // 只要有声音就发送，服务端做精准 VAD
  // 降低前端发送阈值，确保所有可能的人声都发出去
  // VAD_THRESHOLD = 0 (已定义)
  if (average > VAD_THRESHOLD) {
      if (ws && ws.readyState === WebSocket.OPEN) {
         // 降采样并发送
         const finalData = downsampleBuffer(inputData, audioContext.sampleRate, 16000)
         // 直接发送 TypedArray
         ws.send(finalData)
      } else {
         // 连接可能还没好
         // console.warn('WS not open, audio dropped')
      }
      
      // 更新 UI 状态
      if (!isSpeaking) {
          isSpeaking = true
          // 如果是 listening 状态，才更新为“正在聆听”，避免覆盖其他状态
          if (status.value === 'listening') {
             transcript.value = '正在聆听...'
          }
      }
      silenceStart = Date.now()
  } else {
      // 静音状态
      if (isSpeaking && Date.now() - silenceStart > 1000) {
          isSpeaking = false
      }
  }
}

const interruptAIPlayback = () => {
  if (status.value !== 'speaking') return
  interruptSignal.value = true
  audioPlayer.pause()
  audioPlayer.currentTime = 0
  audioQueue.value = [] // 清空队列
  isPlaying.value = false
  
  // 发送打断信号给后端
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'interrupt' }))
  }
  
  status.value = 'listening'
  transcript.value = '正在聆听...'
}

// 辅助函数：降采样
const downsampleBuffer = (buffer, sampleRate, outSampleRate) => {
  if (outSampleRate === sampleRate) {
    return buffer
  }
  if (outSampleRate > sampleRate) {
    throw new Error('downsampling rate show be smaller than original sample rate')
  }
  const sampleRateRatio = sampleRate / outSampleRate
  const newLength = Math.round(buffer.length / sampleRateRatio)
  const result = new Float32Array(newLength)
  let offsetResult = 0
  let offsetBuffer = 0
  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio)
    let accum = 0, count = 0
    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
      accum += buffer[i]
      count++
    }
    result[offsetResult] = accum / count
    offsetResult++
    offsetBuffer = nextOffsetBuffer
  }
  return result
}

// 辅助函数：Float32Array 转 Base64 (保留以备不时之需，但 WS 直接发二进制)
const float32ToBase64 = (float32Array) => {
  const buffer = new ArrayBuffer(float32Array.length * 2)
  const view = new DataView(buffer)
  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i]))
    s = s < 0 ? s * 0x8000 : s * 0x7FFF
    view.setInt16(i * 2, s, true)
  }
  let binary = ''
  const bytes = new Uint8Array(buffer)
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary)
}

// 处理语音
const cleanForTts = (text) => {
  // 去除表情符号，避免朗读 😊 等 emoji
  return text.replace(/[\u{1F300}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{1F600}-\u{1F64F}\u{2600}-\u{27BF}]/gu, '')
}

const sendMessageToAI = async (userText, systemOverride = null) => {
  try {
    const baseUrl = getApiBaseUrl()
    interruptSignal.value = false

    // 预先切换状态，减少视觉延迟
    status.value = 'speaking'
    transcript.value = '小云正在思考...'

    let persona = `你正在和用户电话通话，请用第一人称口语化简短回复，称呼用户：王程萧，语气亲和。`
    
    if (isRecitationMode.value) {
      persona = `角色：背诵小达人（中英文单词口语教练）
目标：帮助用户背诵与巩固单词。要求：
1) 语气鼓励、口语化，短句分行，优先中文解释，示范英文发音与用法；
2) 提供 1-2 句地道例句，提示重读/断句；
3) 引导用户跟读或造句，少提问长篇知识点；
4) 速度适中，逐句输出，别一口气讲太长。`
    }

    if (systemOverride) {
      persona = systemOverride
    }

    const response = await fetch(`${baseUrl}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `${persona}\n用户：${userText}`,
        username: props.username || 'User',
        mode: isRecitationMode.value ? 'recite' : 'chat'
      })
    })

    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`)
    }

    if (!response.body) {
      throw new Error('流式响应不可用')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let fullResponse = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        const jsonStr = trimmed.slice(5).trim()
        if (!jsonStr) continue
        try {
          const data = JSON.parse(jsonStr)
          if (data.type === 'chunk') {
            fullResponse += data.content
            transcript.value = fullResponse
          } else if (data.type === 'end') {
            if (data.full_response) {
              fullResponse = data.full_response
              transcript.value = fullResponse
            }
          } else if (data.type === 'error') {
            throw new Error(data.message || '流式请求失败')
          }
        } catch (e) {
          console.error('解析流式数据失败', e)
        }
      }

      if (interruptSignal.value) {
        try {
          await reader.cancel()
        } catch (e) {
          console.warn('取消流式读取失败', e)
        }
        return
      }
    }

    let aiText = fullResponse

    if (isRecitationMode.value && aiText.trim().startsWith('{')) {
      try {
        const data = JSON.parse(aiText)
        aiText = data.speak || aiText
      } catch (e) {
        console.warn('AI 返回非 JSON 格式，回退到文本', e)
      }
    }

    transcript.value = aiText
    emit('new-message', { type: 'ai', content: aiText })
    
    // TTS 分句播放 (HTTP 方式，用于 Button Triggered Events)
    const sentences = aiText.split(/(?<=[。！？!?])/).map(s => s.trim()).filter(Boolean)
    const playSentence = (sentence) => {
      return new Promise((resolve, reject) => {
        if (interruptSignal.value) {
          resolve(false)
          return
        }
        const ttsSentence = cleanForTts(sentence)
        if (!ttsSentence.trim()) {
          resolve(true)
          return
        }
        const url = `${baseUrl}/api/speech/tts?text=${encodeURIComponent(ttsSentence)}`
        audioPlayer.src = url
        transcript.value = sentence
        audioPlayer.onended = () => resolve(true)
        audioPlayer.onerror = (e) => reject(e)
        audioPlayer.play().catch(reject)
      })
    }
    
    for (const s of (sentences.length ? sentences : [aiText])) {
      const played = await playSentence(s)
      if (interruptSignal.value || played === false) {
        return
      }
    }
    
    // 播放结束，恢复监听
    status.value = 'listening'
    transcript.value = '轮到你了...'
    isSpeaking = false
    silenceStart = null

  } catch (e) {
    console.error("AI 回复失败", e)
    ElMessage.warning('AI 回复失败')
    status.value = 'listening'
  }
}

const recitationIndex = ref(0)
const currentRecitationWord = computed(() => memoryWords.value[recitationIndex.value] || null)

const nextRecitationWord = () => {
  if (recitationIndex.value < memoryWords.value.length - 1) {
    recitationIndex.value++
    // 自动触发 AI 教学下一个单词
    triggerAIForCurrentWord()
  } else {
    ElMessage.success('今日单词已全部学完！')
    exitRecitationMode()
  }
}

const exitRecitationMode = () => {
  isRecitationMode.value = false
  recitationIndex.value = 0
  transcript.value = '背诵结束，回到通话'
  
  // 发送模式退出给 WebSocket
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ 
      type: 'update_context', 
      context: '普通聊天',
      detail: '用户退出了背诵模式' 
    }))
  }
}

const updateShadowingSpeed = () => {
  ElMessage.success(`语速已调整: ${shadowingSpeed.value === '-20%' ? '慢速' : shadowingSpeed.value === '+20%' ? '快速' : '常速'}`)
}

const updateCorrectionState = () => {
  const state = voiceCorrectionEnabled.value ? '开启' : '关闭'
  ElMessage.success(`语音纠正已${state}`)
  
  // 实时更新上下文
  if (ws && ws.readyState === WebSocket.OPEN && currentRecitationWord.value) {
    const detail = `当前单词: ${currentRecitationWord.value.word}, 释义: ${currentRecitationWord.value.definition}. ${voiceCorrectionEnabled.value ? '【注意：请严格纠正用户的发音错误】' : '【注意：以鼓励为主，忽略轻微发音错误】'}`
    
    ws.send(JSON.stringify({ 
      type: 'update_context', 
      context: `正在背诵单词: ${currentRecitationWord.value.word}`,
      detail: detail
    }))
  }
}

const playCurrentWord = () => {
  if (currentRecitationWord.value) {
    const word = currentRecitationWord.value.word
    const baseUrl = getApiBaseUrl()
    const url = `${baseUrl}/api/speech/tts?text=${encodeURIComponent(word)}&voice=en-US-JennyNeural&rate=${shadowingSpeed.value}`
    const audio = new Audio(url)
    audio.play().catch(e => console.error('单词播放失败', e))
  }
}

const triggerAIForCurrentWord = async () => {
  const word = currentRecitationWord.value
  if (!word) return

  // 同步上下文到 WebSocket
  if (ws && ws.readyState === WebSocket.OPEN) {
    const correctionInstruction = voiceCorrectionEnabled.value 
      ? '【重要：请仔细聆听用户发音，如有错误必须指出并示范正确发音】' 
      : '【提示：以鼓励为主】'
      
    ws.send(JSON.stringify({ 
      type: 'update_context', 
      context: `正在背诵单词: ${word.word}`,
      detail: `当前单词: ${word.word}, 释义: ${word.definition}. ${correctionInstruction}` 
    }))
  }

  // 1. 构造强制教学文本 (Strict Format)
  // 格式: Read -> Spell -> Read -> Explain -> Ask
  const spelling = word.word.split('').join('-').toUpperCase()
  const teachingText = `${word.word}. ${spelling}. ${word.word}. ${word.definition}. 你读懂没有？`
  
  // 2. 更新 UI 文本
  transcript.value = teachingText
  emit('new-message', { type: 'ai', content: teachingText })
  
  // 3. 直接调用 TTS 播放 (绕过 LLM 生成，确保内容一致且不可打断)
  // 设置为 speaking 状态并临时禁止打断
  status.value = 'speaking'
  allowInterrupt.value = false // 禁止打断
  
  try {
      const baseUrl = getApiBaseUrl()
      // 清理文本用于 TTS (移除标点等可能影响发音的符号，但保留句号停顿)
      // 注意: cleanForTts 已经移除 emoji
      const ttsText = cleanForTts(teachingText)
      const url = `${baseUrl}/api/speech/tts?text=${encodeURIComponent(ttsText)}&voice=zh-CN-XiaoxiaoNeural&rate=${shadowingSpeed.value}`
      
      audioPlayer.src = url
      await audioPlayer.play()
      
      // 等待播放结束
      await new Promise((resolve, reject) => {
          audioPlayer.onended = resolve
          audioPlayer.onerror = reject
      })
      
  } catch (e) {
      console.error('强制教学播放失败', e)
      ElMessage.warning('播放语音失败')
  } finally {
      // 恢复状态
      status.value = 'listening'
      transcript.value = '轮到你了...'
      allowInterrupt.value = true // 恢复可打断
      isSpeaking = false
      silenceStart = null
  }
}

const startRecitationMode = async () => {
  isRecitationMode.value = true
  recitationIndex.value = 0
  ElMessage.success('进入背诵小达人模式')
  
  // 发送模式更新给 WebSocket
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ 
      type: 'update_context', 
      context: '背诵小达人',
      detail: '用户正在进入背诵模式，请以口语教练身份互动' 
    }))
  }
  
  // 确保数据已加载
  if (memoryWords.value.length === 0) {
    await fetchMemoryData()
  }

  // 直接触发第一个单词的教学
  triggerAIForCurrentWord()
}

const toggleMute = () => {
  isMuted.value = !isMuted.value
}

const manualFinishSpeaking = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    // 发送手动结束信号
    ws.send(JSON.stringify({ type: 'manual_stop' }))
    // 更新本地状态，提供即时反馈
    status.value = 'processing'
    transcript.value = '正在提交...'
  }
}

</script>

<style scoped>
.call-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
  z-index: 9999;
  display: flex;
  color: white;
  overflow: hidden;
}

.call-main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 30px 40px;
  position: relative;
  min-width: 0;
}

.call-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
}

.signal-icon {
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 12px;
}
.signal-icon .bar {
  width: 3px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 1px;
}
.signal-icon .bar:nth-child(1) { height: 4px; }
.signal-icon .bar:nth-child(2) { height: 6px; }
.signal-icon .bar:nth-child(3) { height: 8px; }
.signal-icon .bar:nth-child(4) { height: 10px; }
.signal-icon .bar.active {
  background: white;
}

.carrier {
  font-size: 14px;
  opacity: 0.8;
  flex-grow: 1;
  text-align: center;
}

.toggle-sidebar-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}
.toggle-sidebar-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
}

.call-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.avatar-container {
  position: relative;
  width: 200px;
  height: 200px;
  margin-bottom: 40px;
  animation: breathe 4s ease-in-out infinite;
}
.avatar-container.speaking {
  animation: talk 0.6s ease-in-out infinite alternate;
}
.avatar-container.listening {
  animation: listen 2s ease-in-out infinite;
}
.digital-human-wrapper {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  background: #000;
  transition: all 0.3s ease;
}
.digital-human-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-container.speaking .digital-human-wrapper {
  border-color: rgba(103, 194, 58, 0.8);
  box-shadow: 0 0 50px rgba(103, 194, 58, 0.6);
}
.avatar-container.listening .digital-human-wrapper {
  border-color: rgba(64, 158, 255, 0.6);
  box-shadow: 0 0 30px rgba(64, 158, 255, 0.4);
}

.waveform-container {
  margin-top: 20px;
  width: 200px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.status-text {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
}
.sub-status {
  font-size: 14px;
  opacity: 0.7;
  text-align: center;
  max-width: 80%;
  line-height: 1.4;
  height: 40px;
}

.call-controls {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-top: auto;
}
.control-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  opacity: 0.8;
  transition: all 0.2s;
}
.control-btn:hover {
  opacity: 1;
}
.control-btn span {
  font-size: 12px;
}
.finish-speaking-btn .btn-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.finish-speaking-btn:hover .btn-circle {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.6);
}

.end-call-btn {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #ff4d4f;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(255, 77, 79, 0.4);
}

.memory-sidebar {
  width: 320px;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(10px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  height: 100vh;
}
.memory-sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 20px;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.collapsed-badge {
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.sidebar-collapsed-hint {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  cursor: pointer;
  opacity: 0.7;
  font-size: 14px;
}
.sidebar-collapsed-hint:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.05);
}

.memory-stats-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

/* Styles for learning panel removed */

.learning-header,
.learning-body,
.learning-actions,
.learning-result,
.learning-result-title,
.learning-result-content,
.learning-error {
  display: none;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stat-value {
  font-size: 20px;
  font-weight: 800;
  color: #f9fafb;
}
.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}
.stat-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.2);
}

.current-word-section h4,
.word-queue-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 12px;
}

.memory-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  padding: 20px;
  color: #e5e7eb;
  line-height: 1.5;
}
.empty-card {
  text-align: center;
  padding: 30px 20px;
}
.word-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.word-main {
  flex: 1;
}
.word-text {
  font-size: 24px;
  font-weight: 800;
  color: #f9fafb;
  display: flex;
  align-items: center;
  gap: 10px;
}
.word-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.15);
  color: #c7d2fe;
  border: 1px solid rgba(99, 102, 241, 0.25);
}
.word-pron {
  font-size: 14px;
  color: rgba(229, 231, 235, 0.7);
  margin-top: 4px;
}
.word-def {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  margin: 12px 0;
}
.word-example {
  font-size: 13px;
  color: rgba(229, 231, 235, 0.8);
  font-style: italic;
  padding: 10px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  margin-top: 10px;
}
.memory-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
.action-btn {
  flex: 1;
}
.action-btn.forget:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.action-btn.fuzzy:not(:disabled) {
  background: rgba(245, 158, 11, 0.2);
  border-color: rgba(245, 158, 11, 0.4);
  color: #fde68a;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.queue-item {
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.queue-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.1);
}
.queue-word {
  font-weight: 500;
  color: #e5e7eb;
}
.queue-pron {
  font-size: 12px;
  color: rgba(229, 231, 235, 0.6);
}

@media (max-width: 1024px) {
  .memory-sidebar:not(.collapsed) {
    width: 280px;
  }
}
@media (max-width: 768px) {
  .call-overlay {
    flex-direction: column;
  }
  .memory-sidebar {
    width: 100%;
    height: 40vh;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  .memory-sidebar.collapsed {
    width: 100%;
    height: 50px;
  }
  .sidebar-collapsed-hint {
    writing-mode: horizontal-tb;
    padding: 15px;
    justify-content: center;
    gap: 10px;
  }
}

@keyframes breathe {
  0% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-5px) scale(1.02); }
  100% { transform: translateY(0) scale(1); }
}
@keyframes talk {
  0% { transform: scale(1); filter: brightness(1); }
  100% { transform: scale(1.08); filter: brightness(1.1); }
}
@keyframes listen {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

.listening-waves {
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.wave {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: rgba(96, 165, 250, 0.8);
  box-shadow: 0 0 14px rgba(96, 165, 250, 0.6);
  animation: wavePulse 1.2s ease-in-out infinite;
}

.wave-2 {
  animation-delay: 0.2s;
  background: rgba(147, 197, 253, 0.85);
}

.wave-3 {
  animation-delay: 0.4s;
  background: rgba(59, 130, 246, 0.85);
}

@keyframes wavePulse {
  0% { transform: scale(0.6); opacity: 0.6; }
  50% { transform: scale(1.4); opacity: 1; }
  100% { transform: scale(0.6); opacity: 0.6; }
}

.action-btn.forget:not(:disabled) {
  background: #ef4444;
  border-color: #ef4444;
  color: #fff;
}

.action-btn.fuzzy:not(:disabled) {
  background: #f59e0b;
  border-color: #f59e0b;
  color: #fff;
}

.action-btn.know:not(:disabled) {
  background: #22c55e;
  border-color: #22c55e;
  color: #fff;
}

.action-btn {
  border-radius: 12px;
  font-weight: 600;
  height: 40px;
}

.recitation-footer {
  padding: 16px 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  background: linear-gradient(to top, rgba(0,0,0,0.2), transparent);
}

.recitation-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  width: 100%;
  max-width: 420px;
}

.recitation-btn {
  border-radius: 16px;
  height: 52px;
  font-size: 16px;
  font-weight: 700;
  border: none;
  color: #fff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.recitation-btn.forget {
  background: linear-gradient(135deg, #f87171, #ef4444);
}

.recitation-btn.fuzzy {
  background: linear-gradient(135deg, #fbbf24, #f97316);
}

.recitation-btn.know {
  background: linear-gradient(135deg, #4ade80, #22c55e);
}

.recitation-btn:active {
  transform: scale(0.98);
}

/* Recitation Mode Styles - Redesigned */
.recitation-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  z-index: 10;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.recitation-header {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: opacity 0.2s;
}
.header-left:hover {
  opacity: 0.8;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right {
  min-width: 60px;
  display: flex;
  justify-content: flex-end;
}

.progress-badge {
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.recitation-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 24px 30px;
  gap: 30px;
  overflow-y: auto;
}

.progress-bar-container {
  width: 100%;
  max-width: 400px;
  padding: 0 10px;
}

.progress-bar-track {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: #4ade80;
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.recitation-settings {
  width: 100%;
  max-width: 400px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 12px;
  margin-top: 10px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
}

.setting-item .label {
  font-weight: 500;
}

.word-card-container {
  width: 100%;
  max-width: 360px;
  margin-top: 10px;
}

.word-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 40px 20px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}

.word-card:active {
  transform: scale(0.98);
}

.word-main-text {
  font-size: 48px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1.2;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.word-pron-text {
  font-size: 18px;
  color: #6b7280;
  font-family: monospace;
  background: #f3f4f6;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  margin-bottom: 24px;
}

.word-hint-text {
  font-size: 13px;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

.ai-interaction-container {
  width: 100%;
  max-width: 400px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-top: auto;
  margin-bottom: 20px;
}

.ai-avatar-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
  background: #000;
}

.ai-avatar-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ai-avatar-wrapper.speaking {
  border-color: #4ade80;
  box-shadow: 0 0 15px rgba(74, 222, 128, 0.6);
}

.ai-chat-bubble {
  flex: 1;
  background: white;
  padding: 16px 20px;
  border-radius: 4px 20px 20px 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: relative;
  color: #374151;
  font-size: 16px;
  line-height: 1.6;
}

.bubble-content p {
  margin: 0;
}

.placeholder {
  color: #9ca3af;
  font-style: italic;
}

.recitation-footer {
  padding: 24px 30px 40px;
  display: flex;
  justify-content: center;
  background: linear-gradient(to top, rgba(0,0,0,0.2), transparent);
}

.next-word-btn {
  width: 100%;
  max-width: 360px;
  height: 56px;
  border-radius: 28px;
  font-size: 18px;
  font-weight: 700;
  border: none;
  background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
  color: white;
  box-shadow: 0 10px 25px rgba(245, 87, 108, 0.4);
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.next-word-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px rgba(245, 87, 108, 0.5);
  background: linear-gradient(90deg, #ec8bf9 0%, #f64f66 100%);
}

.next-word-btn:active {
  transform: scale(0.98);
}
</style>
