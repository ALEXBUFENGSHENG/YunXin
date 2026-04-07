<template>
  <div class="h-full w-full overflow-y-auto p-6 bg-white space-y-6 pb-10 min-h-0">
    <div class="flex items-center justify-between mb-8">
        <h3 class="font-bold text-gray-900 flex items-center text-lg">
            <ClipboardCheck :size="24" class="mr-2 text-gray-600" />
            学习复盘报告
        </h3>
        <span class="text-xs text-gray-600 font-mono">{{ new Date().toLocaleDateString() }}</span>
    </div>
    
    <div v-if="!data || !data.report" class="flex flex-col items-center justify-center py-20 text-gray-500">
      <Loader2 v-if="loading" :size="32" class="animate-spin text-gray-400 mb-3" />
      <p class="text-sm font-medium">正在分析学习效果...</p>
    </div>

    <div v-else class="space-y-8 animate-in fade-in duration-500">
      <!-- 评分卡片 -->
      <div v-if="data.scores || (data.report && data.report.scores)" class="grid grid-cols-2 gap-4">
        <div v-for="(score, key) in (data.scores || (data.report && data.report.scores) || {})" :key="key" class="bg-white border border-gray-200 p-4 rounded-xl shadow-sm flex flex-col items-center justify-center hover:shadow-md transition-all">
            <div class="text-3xl font-extrabold text-gray-900">
                {{ (score * 100).toFixed(0) }}
            </div>
            <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider mt-1">{{ key }}</div>
            
            <!-- Progress Bar -->
            <div class="w-full h-1.5 bg-gray-100 rounded-full mt-3 overflow-hidden">
                <div class="h-full bg-gray-800 rounded-full transition-all duration-1000 ease-out" :style="{ width: `${score * 100}%` }"></div>
            </div>
        </div>
      </div>

      <!-- 总结与错因 -->
      <div v-if="data.report.summary || (data.report.error_tags && data.report.error_tags.length > 0)" class="space-y-4">
        <div v-if="data.report.summary" class="bg-blue-50/50 p-5 rounded-xl border border-blue-200">
          <h4 class="font-bold text-black mb-2 flex items-center text-sm">
              <MessageSquare :size="16" class="mr-2 text-blue-800" />
              复盘总结
          </h4>
          <div class="text-sm text-black leading-relaxed font-bold markdown-body" v-html="renderMarkdown(data.report.summary)"></div>
        </div>

        <div v-if="data.report.error_tags && data.report.error_tags.length > 0" class="flex flex-wrap gap-2">
          <span v-for="tag in data.report.error_tags" :key="tag" 
            class="px-3 py-1 bg-red-50 text-red-800 rounded-full text-xs font-bold border border-red-200">
            # {{ tag }}
          </span>
        </div>
      </div>

      <!-- 改进建议 (兼容旧版或新版 artifacts.kp_updates) -->
      <div v-if="(data.report.改进空间 && data.report.改进空间.length > 0) || (data.artifacts && data.artifacts.kp_updates && data.artifacts.kp_updates.length > 0)" class="bg-white p-5 rounded-xl border border-gray-300">
        <h4 class="font-bold text-black mb-3 flex items-center">
            <AlertTriangle :size="18" class="mr-2 text-gray-800" />
            能力提升建议
        </h4>
        <ul class="space-y-2">
            <!-- 兼容旧版字段 -->
            <li v-for="(item, idx) in data.report.改进空间" :key="'old-'+idx" class="flex items-start text-sm text-black font-bold">
                <span class="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-black shrink-0"></span>
                <span class="markdown-body" v-html="renderMarkdown(item)"></span>
            </li>
            <!-- 展示新版 KP 更新 -->
            <li v-for="(item, idx) in (data.artifacts?.kp_updates || [])" :key="'new-'+idx" class="flex items-start text-sm text-black">
                <span class="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0"></span>
                <div class="flex flex-col">
                  <span class="font-bold text-black">{{ item.kp_key }} <span class="text-blue-700 ml-1">+{{ (item.delta * 100).toFixed(0) }}%</span></span>
                  <span class="text-xs text-gray-800 mt-0.5 font-bold">{{ item.evidence }}</span>
                </div>
            </li>
        </ul>
      </div>

      <!-- 行动项 (兼容旧版或新版 artifacts.next_actions) -->
      <div v-if="(data.report.行动项 && data.report.行动项.length > 0) || (data.artifacts && data.artifacts.next_actions && data.artifacts.next_actions.length > 0)" class="bg-white p-5 rounded-xl border border-gray-300 shadow-sm">
        <h4 class="font-bold text-black mb-3 flex items-center">
            <CheckSquare :size="18" class="mr-2 text-gray-800" />
            下一步行动
        </h4>
        <div class="space-y-3">
            <!-- 兼容旧版字段 -->
            <div v-for="(item, idx) in data.report.行动项" :key="'old-act-'+idx" class="flex items-start text-sm text-black font-bold bg-gray-50 p-3 rounded-lg border border-gray-300">
                <span class="flex items-center justify-center w-5 h-5 rounded bg-white text-black text-xs font-bold mr-3 shrink-0 border border-gray-400">
                    {{ idx + 1 }}
                </span>
                <span class="markdown-body" v-html="renderMarkdown(item)"></span>
            </div>
            <!-- 展示新版 next_actions -->
            <div v-for="(item, idx) in (data.artifacts?.next_actions || [])" :key="'new-act-'+idx" class="flex items-center justify-between text-sm text-black font-bold bg-blue-50/50 p-3 rounded-lg border border-blue-200">
                <div class="flex items-start">
                  <span class="flex items-center justify-center w-5 h-5 rounded bg-blue-700 text-white text-xs font-bold mr-3 shrink-0">
                      {{ idx + 1 }}
                  </span>
                  <span class="markdown-body" v-html="renderMarkdown(item.action)"></span>
                </div>
                <span v-if="item.eta_min" class="text-[10px] text-gray-800 flex items-center gap-1 font-bold">
                  <Clock :size="10" /> {{ item.eta_min }}min
                </span>
            </div>
        </div>
      </div>

      <!-- 复习卡片 (新功能) -->
      <div v-if="data.artifacts && data.artifacts.review_cards && data.artifacts.review_cards.length > 0" class="space-y-3">
        <h4 class="font-bold text-gray-900 flex items-center px-1">
            <BookOpen :size="18" class="mr-2 text-gray-600" />
            知识卡片
        </h4>
        <div class="grid grid-cols-1 gap-3">
          <div v-for="(card, idx) in data.artifacts.review_cards" :key="idx" 
            class="p-4 rounded-xl border-l-4 shadow-sm"
            :class="{
              'bg-amber-50 border-amber-400': card.type === 'pitfall',
              'bg-blue-50 border-blue-400': card.type === 'concept',
              'bg-purple-50 border-purple-400': card.type === 'procedure',
              'bg-gray-50 border-gray-400': !['pitfall', 'concept', 'procedure'].includes(card.type)
            }">
            <div class="flex justify-between items-start mb-2">
              <span class="text-[10px] uppercase font-black tracking-widest text-gray-500">{{ card.type }}</span>
            </div>
            <div class="text-sm text-gray-900 font-bold markdown-body" v-html="renderMarkdown(card.content)"></div>
            <div v-if="card.source" class="mt-2 text-[10px] text-gray-500 text-right italic">— {{ card.source }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ClipboardCheck, Loader2, AlertTriangle, CheckSquare, MessageSquare, Clock, BookOpen } from 'lucide-vue-next'
import { renderMarkdown } from '../../utils/markdown'

defineProps({
  data: Object,
  loading: Boolean
})
</script>
