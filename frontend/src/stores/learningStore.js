import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLearningStore = defineStore('learning', () => {
  const messages = ref([])
  const currentAgentView = ref(null) // { agent: string, data: object }
  const agentResults = ref({}) // { '分解师': data, '思考师': data, ... }
  const isAgentWorking = ref(false)
  const currentWorkingAgent = ref('')
  const pinnedAgent = ref(null) // '思考师', etc.
  const currentTopic = ref('')
  const currentUser = ref('Guest')
  const currentSessionId = ref(Date.now()) // Use integer

  // Message Actions
  const addMessage = (msg) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    messages.value.push({ ...msg, id })
    return id
  }

  const appendMessageContent = (id, content) => {
    const msg = messages.value.find(m => m.id === id)
    if (msg) {
      msg.content = (msg.content || '') + content
    }
  }

  // Agent Actions
  const setAgentStatus = (agent, status) => {
    currentWorkingAgent.value = agent
    isAgentWorking.value = status === 'working'
  }

  const updateAgentData = (agent, data, merge = false) => {
    // Store data in history
    if (merge && agentResults.value[agent]) {
      agentResults.value[agent] = { ...agentResults.value[agent], ...data }
    } else {
      agentResults.value[agent] = data
    }
    
    // If we have a pinned agent, only switch if the incoming data is for that agent
    if (pinnedAgent.value) {
      if (agent === pinnedAgent.value) {
        currentAgentView.value = { agent, data: agentResults.value[agent] }
      }
    } else {
      // Automatically switch view to the active agent if not pinned
      currentAgentView.value = { agent, data: agentResults.value[agent] }
    }
  }

  const submitFeedback = async (topic, userAnswer, phase) => {
    try {
      const session_data = {
        thinking: agentResults.value['思考师'],
        path: agentResults.value['教练'],
        policy: agentResults.value['策略师']
      }

      const response = await fetch('/api/learn/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          user_answer: userAnswer,
          phase,
          session_data
        })
      })
      
      const result = await response.json()
      if (result.status === 'success') {
        // 更新教练数据（增加反馈）
        updateAgentData('教练', { feedback: result.data.coach_feedback }, true)
        // 更新复盘数据
        updateAgentData('复盘师', result.data.review_update, true)
        return result.data
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      throw error
    }
  }

  const togglePinAgent = (agent) => {
    if (pinnedAgent.value === agent) {
      pinnedAgent.value = null
    } else {
      pinnedAgent.value = agent
      // Immediately switch to it if it has data
      if (agentResults.value[agent]) {
        currentAgentView.value = { agent, data: agentResults.value[agent] }
      }
    }
  }

  const switchAgentView = (agent) => {
    if (agentResults.value[agent]) {
      currentAgentView.value = { agent, data: agentResults.value[agent] }
      // If user manually switches, we unpin to allow they exploring
      // pinnedAgent.value = null 
    }
  }

  const setCurrentTopic = (topic) => {
    currentTopic.value = topic
  }

  const clearSession = () => {
    messages.value = []
    currentAgentView.value = null
    agentResults.value = {}
    isAgentWorking.value = false
    currentWorkingAgent.value = ''
    pinnedAgent.value = null
    currentTopic.value = ''
    currentSessionId.value = Date.now()
  }

  return {
    messages,
    currentAgentView,
    agentResults,
    isAgentWorking,
    currentWorkingAgent,
    pinnedAgent,
    currentTopic,
    currentUser,
    currentSessionId,
    addMessage,
    appendMessageContent,
    setAgentStatus,
    updateAgentData,
    submitFeedback,
    togglePinAgent,
    switchAgentView,
    setCurrentTopic,
    clearSession
  }
})
