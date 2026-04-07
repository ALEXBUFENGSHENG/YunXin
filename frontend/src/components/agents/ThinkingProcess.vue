<template>
  <div class="h-full w-full overflow-y-auto p-6 bg-white space-y-6 pb-10 min-h-0">
    <!-- Header with Toggle -->
    <div 
        class="flex items-center justify-between mb-6 border-b border-gray-100 pb-4 cursor-pointer hover:bg-gray-50 transition-colors rounded-lg p-2 -mx-2 select-none"
        @click="isExpanded = !isExpanded"
    >
        <h3 class="font-bold text-gray-900 flex items-center">
            <div class="mr-2 transition-transform duration-200" :class="{ 'rotate-[-90deg]': !isExpanded }">
                <ChevronDown :size="20" class="text-gray-500" />
            </div>
            <BrainCircuit :size="20" class="mr-2 text-gray-500" />
            深度思考链
        </h3>
        <span class="text-xs px-2 py-1 bg-white border border-gray-200 text-slate-700 rounded-full font-medium" v-if="data?.questioning_chain">
            {{ data.questioning_chain.length }} 层深度
        </span>
    </div>
    
    <div v-show="isExpanded">
        <div v-if="!data || !data.questioning_chain" class="flex flex-col items-center justify-center py-20 text-slate-600">
          <Loader2 v-if="loading" :size="32" class="animate-spin text-blue-600 mb-3" />
          <p class="text-sm font-bold">正在构建思维模型...</p>
        </div>

        <div v-else class="space-y-8 relative pb-8">
          <!-- Vertical Line -->
          <div class="absolute left-[19px] top-4 bottom-4 w-0.5 bg-gray-200 -z-10"></div>

          <!-- Chain Steps -->
          <div v-for="(step, index) in data.questioning_chain" :key="index" class="relative pl-12 group animate-in slide-in-from-bottom-4 duration-500" :style="{ animationDelay: `${index * 150}ms` }">
            <!-- Node Dot -->
            <div class="absolute left-0 top-1 w-10 h-10 rounded-full bg-white border-2 border-gray-200 flex items-center justify-center shadow-sm group-hover:border-gray-300 group-hover:scale-110 transition-all z-10">
                <span class="text-xs font-bold text-slate-800">{{ step.level || index + 1 }}</span>
            </div>
            
            <!-- Content Card -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5 hover:shadow-md transition-shadow group-hover:border-gray-300">
                <h4 class="text-md font-bold text-black mb-3 flex items-start">
                    <HelpCircle :size="16" class="mt-1 mr-2 text-slate-800 shrink-0" />
                    {{ step.question }}
                </h4>
                
                <div class="bg-gray-50 p-4 rounded-lg text-sm text-slate-900 leading-relaxed border border-gray-200 font-bold">
                    {{ step.answer }}
                </div>
            </div>
          </div>

          <!-- Insights -->
          <div v-if="data.key_insights" class="mt-10 animate-in fade-in duration-700 delay-300">
            <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h4 class="font-bold text-black mb-4 flex items-center">
                    <Lightbulb :size="18" class="mr-2 text-slate-800" />
                    核心洞察
                </h4>
                <ul class="space-y-3">
                  <li v-for="(insight, idx) in data.key_insights" :key="idx" class="flex items-start text-sm text-black font-bold">
                      <span class="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-black shrink-0"></span>
                      {{ insight }}
                  </li>
                </ul>
            </div>
          </div>
        </div>
    </div>
    
    <div v-show="!isExpanded" class="text-center text-sm text-slate-600 py-10 italic">
        思考过程已折叠 (点击标题展开)
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BrainCircuit, Loader2, HelpCircle, Lightbulb, ChevronDown } from 'lucide-vue-next'

defineProps({
  data: Object,
  loading: Boolean
})

const isExpanded = ref(true)
</script>
