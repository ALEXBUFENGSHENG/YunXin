<template>
  <div class="learning-viz">
    <div class="viz-header">
      <div class="agent-tabs">
        <button
          v-for="agent in ['分解师', '思考师', '教练', '复盘师']"
          :key="agent"
          v-show="agentResults[agent]"
          @click="emit('switch-agent', agent)"
          :class="['agent-tab', { active: currentAgentView && currentAgentView.agent === agent }]"
        >
          <span>{{ agent }}</span>
          <div
            v-if="agent === '思考师'"
            @click.stop="emit('toggle-pin', agent)"
            class="pin-icon"
            :class="{ pinned: pinnedAgent === agent }"
          >
            <Pin :size="10" />
          </div>
        </button>
        <div v-if="Object.keys(agentResults).length === 0" class="empty-tab">
          <LayoutDashboard :size="14" />
          <span>思维白板</span>
        </div>
      </div>
    </div>

    <div class="viz-content">
      <div v-if="!currentAgentView" class="viz-empty">
        <div class="viz-empty-icon">
          <BrainCircuit :size="48" />
        </div>
        <h3>思维可视化</h3>
        <p>当智能体开始工作时，这里将实时展示知识拆解、深度思考路径和复盘报告。</p>
      </div>

      <Transition name="fade" mode="out-in">
        <component
          v-if="currentAgentView"
          :is="activeComponent"
          :data="currentAgentView.data"
          :loading="isAgentWorking && currentWorkingAgent === currentAgentView.agent"
          class="viz-component"
        />
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { BrainCircuit, LayoutDashboard, Pin } from 'lucide-vue-next'
import DecompositionView from '../agents/DecompositionView.vue'
import ThinkingProcess from '../agents/ThinkingProcess.vue'
import ReviewDashboard from '../agents/ReviewDashboard.vue'
import CoachView from '../agents/CoachView.vue'

const props = defineProps({
  agentResults: {
    type: Object,
    required: true
  },
  currentAgentView: {
    type: Object,
    default: null
  },
  isAgentWorking: {
    type: Boolean,
    default: false
  },
  currentWorkingAgent: {
    type: String,
    default: ''
  },
  pinnedAgent: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['switch-agent', 'toggle-pin'])

const activeComponent = computed(() => {
  if (!props.currentAgentView) return null
  switch (props.currentAgentView.agent) {
    case '分解师':
      return DecompositionView
    case '思考师':
      return ThinkingProcess
    case '复盘师':
      return ReviewDashboard
    case '教练':
      return CoachView
    case '策略师':
      return ReviewDashboard
    default:
      return null
  }
})
</script>

<style scoped>
.learning-viz {
  flex: 1;
  background: #f1f5f9;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.viz-header {
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  background: #fff;
}

.agent-tabs {
  display: flex;
  gap: 8px;
}

.agent-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-tab:hover {
  background: #f1f5f9;
  color: #334155;
}

.agent-tab.active {
  background: #1e293b;
  color: white;
  box-shadow: 0 2px 8px rgba(30, 41, 59, 0.2);
}

.pin-icon {
  opacity: 0.5;
  transition: all 0.2s;
}

.pin-icon:hover {
  opacity: 1;
}

.pin-icon.pinned {
  opacity: 1;
  color: #60a5fa;
}

.empty-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.viz-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  padding: 20px;
  color: #1e293b;
  min-height: 0;
}

.viz-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.viz-empty-icon {
  background: #fff;
  padding: 24px;
  border-radius: 50%;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  color: #cbd5e1;
}

.viz-component {
  height: 100%;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
