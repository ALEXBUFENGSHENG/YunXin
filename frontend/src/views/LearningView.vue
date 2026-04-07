<template>
  <div class="chat-layout">
    <LearningSidebar
      :logo-icon="logoIcon"
      :current-topic="currentTopic"
      @new-session="handleNewSession"
      @go-chat="goToChatMode"
      @go-math="goToMathMode"
    />

    <div class="learning-container">
      <LearningChatPanel
        v-model="inputMessage"
        :messages="messages"
        :is-agent-working="isAgentWorking"
        :current-working-agent="currentWorkingAgent"
        :is-loading="isLoading"
        @send="handleSend"
        @preset="applyPreset"
        @clear="store.clearSession"
      />

      <LearningVizPanel
        :agent-results="agentResults"
        :current-agent-view="currentAgentView"
        :is-agent-working="isAgentWorking"
        :current-working-agent="currentWorkingAgent"
        :pinned-agent="pinnedAgent"
        @switch-agent="store.switchAgentView"
        @toggle-pin="store.togglePinAgent"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLearningStore } from '../stores/learningStore'
import { useLLMStream } from '../composables/useLLMStream'
import { useLearningActions } from '../composables/useLearningActions'
import LearningSidebar from '../components/learning/LearningSidebar.vue'
import LearningChatPanel from '../components/learning/LearningChatPanel.vue'
import LearningVizPanel from '../components/learning/LearningVizPanel.vue'
import logoIcon from '../assets/logo.png'

const router = useRouter()
const store = useLearningStore()
const {
  messages,
  currentAgentView,
  isAgentWorking,
  currentWorkingAgent,
  agentResults,
  pinnedAgent,
  currentTopic
} = storeToRefs(store)
const { sendMessage, isLoading } = useLLMStream()

const inputMessage = ref('')

const {
  handleSend,
  applyPreset,
  handleNewSession,
  goToChatMode,
  goToMathMode
} = useLearningActions({
  store,
  router,
  sendMessage,
  isLoading,
  inputMessage
})

onMounted(() => {
  if (messages.value.length === 0) {
    store.addMessage({
      role: 'assistant',
      content: '你好！我是你的 AI 深度学习教练。\n\n请输入你想学习的主题（例如："如何学习 Python" 或 "解释量子力学"），我将为你拆解知识、规划路径并辅助复盘。'
    })
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
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.learning-container {
  flex: 1;
  display: flex;
  overflow: hidden;
  background: #f8fafc;
}
</style>
