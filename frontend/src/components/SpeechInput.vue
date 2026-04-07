<template>
  <div class="speech-input-container">
    <!-- 语音输入按钮 -->
    <el-tooltip :content="tooltipText" placement="top" :disabled="isRecording || isStarting">
      <el-button 
        :type="isRecording ? 'danger' : 'default'" 
        circle 
        :loading="isStarting"
        :class="{ 'recording': isRecording, 'processing': isProcessing }"
        @click="toggleRecording"
        :disabled="isProcessing"
      >
        <template #icon>
          <el-icon v-if="!isStarting">
            <component :is="isRecording ? VideoPause : Microphone" />
          </el-icon>
        </template>
      </el-button>
    </el-tooltip>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed } from 'vue'
import { Microphone, VideoPause, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { getApiBaseUrl } from '../utils/api'

// 状态管理
const isRecording = ref(false)
const isStarting = ref(false) // 新增：启动中状态
const isProcessing = ref(false)
const recognitionResult = ref('')

const tooltipText = computed(() => {
  if (isProcessing.value) return '正在处理，请稍候'
  if (isRecording.value) return '点击结束并识别'
  if (isStarting.value) return '正在请求麦克风'
  return '点击开始语音输入'
})

// 音频上下文变量
let audioContext = null
let mediaStream = null
let scriptProcessor = null
let audioInput = null
let audioChunks = [] // 本地音频缓冲

// 简易重采样函数 (线性插值/平均)
const downsampleBuffer = (buffer, inputSampleRate, outputSampleRate) => {
  if (outputSampleRate === inputSampleRate) return buffer
  const sampleRateRatio = inputSampleRate / outputSampleRate
  const newLength = Math.round(buffer.length / sampleRateRatio)
  const result = new Float32Array(newLength)
  let offsetResult = 0
  let offsetBuffer = 0
  
  while (offsetResult < result.length) {
    let nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio)
    let accum = 0, count = 0
    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
      accum += buffer[i]
      count++
    }
    result[offsetResult] = count > 0 ? accum / count : 0
    offsetResult++
    offsetBuffer = nextOffsetBuffer
  }
  return result
}

let socket = null

// 辅助函数：Float32Array 转 Base64
const float32ToBase64 = (float32Array) => {
  const buffer = float32Array.buffer
  let binary = ''
  const bytes = new Uint8Array(buffer)
  const len = bytes.byteLength
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary)
}

// 开始后端录音 (使用 AudioContext 录制整句)
const startBackendRecording = () => {
  isStarting.value = true // 开始 loading
  console.log('请求麦克风权限 (Whole Sentence)...')
  recognitionResult.value = ''
  audioChunks = [] // 清空缓冲
  
  startAudioCapture()
}

const startAudioCapture = () => {
  navigator.mediaDevices.getUserMedia({ 
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true
    } 
  })
    .then(stream => {
      mediaStream = stream
      // 尝试请求 16k
      audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 })
      
      const actualSampleRate = audioContext.sampleRate
      console.log(`AudioContext SampleRate: ${actualSampleRate}`)
      
      audioInput = audioContext.createMediaStreamSource(stream)
      scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1)
      
      scriptProcessor.onaudioprocess = (event) => {
        if (isRecording.value) {
          const inputData = event.inputBuffer.getChannelData(0)
          // 重采样到 16000
          const outputData = downsampleBuffer(inputData, actualSampleRate, 16000)
          // 存入本地缓冲 (深拷贝)
          audioChunks.push(new Float32Array(outputData))
        }
      }
      
      audioInput.connect(scriptProcessor)
      scriptProcessor.connect(audioContext.destination)
      
      isRecording.value = true
      isStarting.value = false 
      
      // 通知父组件录音开始
      emit('recording-start')
    })
    .catch(err => {
      console.error("无法获取麦克风", err)
      
      let errorMsg = '无法访问麦克风'
      if (err.name === 'NotAllowedError') {
        errorMsg = '麦克风权限被拒绝，请在浏览器设置中允许访问'
      } else if (err.name === 'NotFoundError') {
        errorMsg = '未检测到麦克风设备'
      } else if (err.name === 'NotReadableError') {
        errorMsg = '麦克风被其他应用占用'
      }
      
      ElMessage.error(errorMsg)
      isStarting.value = false
    })
}

// 停止后端录音并识别
const stopBackendRecording = async () => {
  if (isRecording.value) {
    console.log('停止录音，开始识别...')
    isRecording.value = false
    isProcessing.value = true
    
    try {
      if (scriptProcessor) scriptProcessor.disconnect()
      if (audioInput) audioInput.disconnect()
      if (mediaStream) {
          mediaStream.getTracks().forEach(track => track.stop())
      }
      
      if (audioChunks.length > 0) {
        let totalLength = 0
        for (let chunk of audioChunks) {
          totalLength += chunk.length
        }
        
        const mergedAudio = new Float32Array(totalLength)
        let offset = 0
        for (let chunk of audioChunks) {
          mergedAudio.set(chunk, offset)
          offset += chunk.length
        }
        
        console.log(`录音结束，总样本数: ${totalLength}, 时长: ${(totalLength/16000).toFixed(2)}s`)
        
        const base64Data = float32ToBase64(mergedAudio)
        
        try {
          const baseUrl = getApiBaseUrl()

          const response = await axios.post(`${baseUrl}/api/speech/recognize`, {
            audio_data: base64Data,
            audio_format: 'raw_float32',
            sample_rate: 16000
          })
          
          if (response.data.success) {
            const text = response.data.result
            
            if (!text || text.trim().length < 2) {
              ElMessage.warning('语音太短或未识别到内容')
              recognitionResult.value = ''
            } else {
              recognitionResult.value = text
              emit('recognition-update', text)
              emit('recognition-complete', text)
              ElMessage.success(`识别成功: ${text}`)
            }
          } else {
            const errorMsg = response.data.error || '识别失败'
            ElMessage.error(errorMsg)
          }
        } catch (e) {
          console.error('识别请求失败', e)
          
          let errorMsg = '识别请求失败'
          if (e.response) {
            if (e.response.status === 500) {
              errorMsg = '服务器处理出错，请稍后重试'
            } else if (e.response.data?.error) {
              errorMsg = e.response.data.error
            }
          } else if (e.request) {
            errorMsg = '网络连接失败，请检查网络'
          }
          
          ElMessage.error(errorMsg)
        }
      } else {
        ElMessage.warning('录音时间太短')
      }
    } finally {
      if (audioContext && audioContext.state !== 'closed') {
          try {
              await audioContext.close()
          } catch (e) {}
      }
      audioContext = null
      audioChunks = []
      isProcessing.value = false
    }
  }
}

// 统一开始录音
const startRecording = () => {
  startBackendRecording()
}

// 统一停止录音
const stopRecording = () => {
  stopBackendRecording()
}

// 切换录音状态
const toggleRecording = () => {
  console.log('点击了麦克风按钮', { isRecording: isRecording.value, isStarting: isStarting.value })
  
  // 检查环境支持
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    ElMessage.error('您的浏览器不支持录音，或当前环境非 HTTPS 安全环境。')
    console.error('navigator.mediaDevices.getUserMedia is not supported')
    return
  }
  
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// 清理资源
onUnmounted(() => {
  if (isRecording.value) stopRecording()
})

const emit = defineEmits(['recognition-complete', 'recognition-update', 'recording-start'])
</script>

<style scoped>
.speech-input-container {
  position: relative; /* 关键：为气泡提供定位基准 */
  display: inline-flex;
  align-items: center;
}

.speech-bubble {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 12px; /* 距离按钮的间距 */
  width: 280px;
  background: white;
  border: 1px solid #e4e7ed;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  z-index: 2000;
  animation: slideUp 0.2s ease-out;
}

.bubble-content {
  padding: 12px;
}

.bubble-arrow {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%) rotate(45deg);
  width: 12px;
  height: 12px;
  background: white;
  border-right: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
}

.recording-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f56c6c;
  font-size: 12px;
  margin-bottom: 8px;
  font-weight: 500;
}

.pulse-icon {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f56c6c;
  animation: pulse 1.5s infinite ease-in-out;
}

.text-preview {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
  min-height: 24px;
  max-height: 200px;
  overflow-y: auto;
  word-wrap: break-word;
}

.recording {
  animation: pulse-shadow 1.5s infinite;
}

.processing {
  opacity: 0.7;
  cursor: not-allowed;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
  100% { transform: scale(0.95); opacity: 1; }
}

@keyframes pulse-shadow {
  0% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(245, 108, 108, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0); }
}
</style>
