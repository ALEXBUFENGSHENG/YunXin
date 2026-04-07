<script setup>
import { ref, computed } from 'vue'
import { 
  ClipboardCheck, 
  Clock, 
  ArrowRight, 
  Lightbulb,
  CheckCircle2,
  MessageSquare,
  Send,
  Loader2,
  Trophy,
  AlertCircle
} from 'lucide-vue-next'
import { useLearningStore } from '../../stores/learningStore'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  loading: Boolean
})

const store = useLearningStore()
const userAnswer = ref('')
const isSubmitting = ref(false)
const showSuccess = ref(false)

const tasks = computed(() => props.data?.tasks || [])
const timeAllocation = computed(() => props.data?.time_allocation || {})
const firstStep = computed(() => props.data?.first_step_guide || '')
const coachFeedback = computed(() => props.data?.feedback || null)

const totalTasks = computed(() => tasks.value.length)

const handleSubmit = async () => {
  if (!userAnswer.value.trim() || isSubmitting.value) return
  
  isSubmitting.value = true
  try {
    // 简单获取当前话题，可以从 store 进一步优化
    const topic = tasks.value[0]?.description || '当前学习任务'
    await store.submitFeedback(topic, userAnswer.value)
    userAnswer.value = ''
    showSuccess.value = true
    setTimeout(() => { showSuccess.value = false }, 3000)
  } catch (error) {
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="h-full w-full overflow-y-auto p-6 bg-white space-y-6 pb-10 min-h-0">
    <!-- 引导语 -->
    <div v-if="firstStep" class="bg-blue-50 border border-blue-100 p-4 rounded-xl flex items-start gap-3">
      <div class="bg-blue-500 p-2 rounded-lg text-white mt-1">
        <MessageSquare :size="18" />
      </div>
      <div>
        <h4 class="font-bold text-blue-900 mb-1">教练寄语</h4>
        <p class="text-blue-800 text-sm leading-relaxed">{{ firstStep }}</p>
      </div>
    </div>

    <!-- 时间分配 -->
    <div v-if="Object.keys(timeAllocation).length > 0" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div v-for="(time, phase) in timeAllocation" :key="phase" 
        class="bg-white p-3 rounded-xl border border-gray-200 flex flex-col items-center justify-center text-center shadow-sm">
        <span class="text-xs text-slate-900 mb-1 font-semibold">{{ phase }}</span>
        <div class="flex items-center gap-1 font-bold text-gray-900">
          <Clock :size="14" class="text-blue-600" />
          <span>{{ time }}min</span>
        </div>
      </div>
    </div>

    <!-- 交互反馈区 (新) -->
    <div class="bg-white p-5 rounded-xl border-2 border-blue-100 shadow-sm">
      <h4 class="font-bold text-black mb-3 flex items-center gap-2">
        <Send :size="18" class="text-blue-600" />
        交互练习
      </h4>
      
      <div v-if="coachFeedback" class="mb-4 animate-in slide-in-from-top-2">
        <div class="bg-green-50 border border-green-200 p-4 rounded-xl">
           <div class="flex items-center gap-2 text-green-900 font-bold mb-2">
              <Trophy :size="18" />
              教练评价
           </div>
           <div class="text-sm text-green-950 leading-relaxed whitespace-pre-wrap font-bold">
             {{ typeof coachFeedback === 'string' ? coachFeedback : coachFeedback.feedback }}
           </div>
           <div v-if="coachFeedback.suggestions" class="mt-3 pt-3 border-t border-green-200/50">
             <div class="text-xs font-bold text-green-900 mb-1">改进建议：</div>
             <p class="text-xs text-green-950 font-bold">{{ coachFeedback.suggestions }}</p>
           </div>
        </div>
      </div>

      <div class="relative">
        <textarea 
          v-model="userAnswer"
          placeholder="在此输入你的练习答案或思考过程..."
          class="w-full h-32 p-4 bg-white border border-gray-300 rounded-xl text-base text-black focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none resize-none placeholder:text-gray-500 font-medium"
        ></textarea>
        <button 
          @click="handleSubmit"
          :disabled="!userAnswer.trim() || isSubmitting"
          class="absolute bottom-3 right-3 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold flex items-center gap-2 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Loader2 v-if="isSubmitting" :size="16" class="animate-spin" />
          <span v-else>请求反馈</span>
          <ArrowRight :size="16" />
        </button>
      </div>
      <p v-if="showSuccess" class="text-[10px] text-green-700 mt-2 flex items-center gap-1 font-bold">
        <CheckCircle2 :size="12" /> 反馈已收到，复盘看板已同步更新！
      </p>
    </div>

    <!-- 任务列表 -->
    <div class="space-y-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="font-bold text-black flex items-center gap-2">
          <ClipboardCheck :size="20" class="text-blue-600" />
          个性化学习路径
        </h3>
        <span class="text-xs text-black font-bold">共 {{ totalTasks }} 个阶段</span>
      </div>

      <div v-for="(task, index) in tasks" :key="index" 
        class="relative pl-8 pb-6 last:pb-0 group">
        <!-- 时间线 -->
        <div class="absolute left-3 top-0 bottom-0 w-0.5 bg-gray-300 group-last:hidden"></div>
        <div class="absolute left-0 top-1 w-6 h-6 rounded-full bg-white border-2 border-blue-600 flex items-center justify-center z-10 shadow-sm">
          <span class="text-[10px] font-bold text-blue-700">{{ index + 1 }}</span>
        </div>

        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow group-hover:border-gray-300">
          <div class="flex justify-between items-start mb-2">
            <h4 class="font-bold text-black">{{ task.phase }}</h4>
            <span class="text-[10px] px-2 py-0.5 bg-gray-100 text-black rounded-full font-bold border border-gray-300">
              {{ task.deliverable ? '需交付' : '阅读' }}
            </span>
          </div>
          
          <p class="text-sm text-black mb-3 leading-relaxed font-bold">{{ task.description }}</p>

          <div v-if="task.deliverable" class="bg-green-50 p-3 rounded-lg border border-green-200 mb-3">
            <div class="flex items-center gap-2 text-green-900 font-bold text-xs mb-1">
              <CheckCircle2 :size="14" />
              交付物
            </div>
            <p class="text-green-950 text-xs font-bold">{{ task.deliverable }}</p>
          </div>

          <div v-if="task.hint" class="flex items-start gap-2 text-black italic text-xs bg-amber-50 p-3 rounded-lg border border-amber-200">
            <Lightbulb :size="14" class="text-amber-600 mt-0.5 flex-shrink-0" />
            <span class="font-medium text-slate-700">提示：{{ task.hint }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
