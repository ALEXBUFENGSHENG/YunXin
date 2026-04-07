import { computed } from 'vue'

export const useLearningActions = ({
  store,
  router,
  sendMessage,
  isLoading,
  inputMessage
}) => {
  const canSend = computed(() => inputMessage.value.trim() && !isLoading.value)

  const handleSend = async () => {
    if (!canSend.value) return
    const msg = inputMessage.value
    store.setCurrentTopic(msg)
    inputMessage.value = ''
    // Pass 'learn' as type to sendMessage
    await sendMessage(msg, store.currentUser, store.currentSessionId, false, 'learn')
  }

  const applyPreset = async (text) => {
    inputMessage.value = text
    store.pinnedAgent = '思考师'
    await handleSend()
  }

  const handleNewSession = () => {
    store.clearSession()
  }

  const goToChatMode = () => router.push('/')
  const goToMathMode = () => router.push('/math')

  return {
    canSend,
    handleSend,
    applyPreset,
    handleNewSession,
    goToChatMode,
    goToMathMode
  }
}
