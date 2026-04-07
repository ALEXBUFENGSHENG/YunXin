<template>
  <div class="h-full w-full bg-white border-none rounded-none overflow-hidden relative">
    <div class="absolute top-4 left-4 z-10 bg-white/90 p-3 rounded-xl shadow-sm border border-gray-200 backdrop-blur-sm">
        <h3 class="font-bold text-sm text-gray-900 flex items-center">
            <Share2 :size="16" class="mr-2 text-gray-700" />
            知识图谱
        </h3>
        <p class="text-xs text-gray-600 mt-1" v-if="nodes.length > 0">
            已生成 {{ nodes.length }} 个知识节点
        </p>
    </div>
    
    <VueFlow 
      v-if="nodes.length > 0"
      v-model:nodes="nodes" 
      v-model:edges="edges" 
      :fit-view-on-init="true"
      :default-zoom="1.4"
      class="h-full w-full bg-white"
    >
      <Background pattern-color="#e5e7eb" :gap="20" :size="1" class="bg-white" />
      <Controls class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden" />
    </VueFlow>
    
    <div v-else class="flex items-center justify-center h-full text-gray-600">
        <div class="text-center flex flex-col items-center">
             <Loader2 v-if="loading" class="animate-spin text-gray-700 mb-2" :size="32" />
             <p v-if="loading" class="font-medium text-gray-800">正在构建知识图谱...</p>
             <p v-else class="text-gray-500">暂无数据</p>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { Share2, Loader2 } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  loading: Boolean
})

const nodes = ref([])
const edges = ref([])

// Transform hierarchical data to graph data
watch(() => props.data, (newData) => {
  if (!newData || !newData.核心概念) return

  const newNodes = []
  const newEdges = []
  
    // Root Node
    const rootId = 'root'
    newNodes.push({
      id: rootId,
      label: newData.知识体系?.root || '核心主题',
      position: { x: 400, y: 50 },
      type: 'input',
      style: { 
          background: '#ffffff', 
          color: '#0f172a', 
          border: '2px solid #cbd5e1', 
          padding: '14px 28px', 
          borderRadius: '12px',
          fontSize: '18px',
          fontWeight: 'bold',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          width: 'auto',
          minWidth: '180px',
          textAlign: 'center'
      }
    })

    // Core Concepts
    if (newData.核心概念) {
      const total = newData.核心概念.length
      const width = 800
      const startX = 400 - (width / 2)
      const gap = width / (total - 1 || 1)

      newData.核心概念.forEach((concept, index) => {
        const id = `c-${index}`
        const x = total === 1 ? 400 : startX + (index * gap)
        
        newNodes.push({
          id,
          label: concept,
          position: { x, y: 250 },
          style: { 
              background: '#ffffff', 
              border: '1px solid #94a3b8', 
              color: '#000000',
              padding: '12px 18px',
              borderRadius: '8px',
              fontWeight: '700',
              fontSize: '16px',
              boxShadow: '0 2px 4px 0 rgba(0, 0, 0, 0.1)',
              width: '200px',
              textAlign: 'center'
          }
        })
        newEdges.push({
          id: `e-root-${id}`,
          source: rootId,
          target: id,
          animated: true,
          style: { stroke: '#000000', strokeWidth: 2 }
        })
      })
    }
    
    // Learning Path Steps (if available, visualize as a sequence below)
      if (newData.学习路径) {
      newData.学习路径.forEach((step, index) => {
        const id = `s-${index}`
        // Simple vertical layout for path steps or connect to relevant concepts
        // Here we just put them in a row below concepts
        newNodes.push({
          id,
          label: `${index + 1}. ${step}`,
          position: { x: 200 + (index % 3) * 250, y: 450 + Math.floor(index / 3) * 100 },
          style: { 
              background: '#f8fafc', 
              border: '1px solid #94a3b8', 
              color: '#000000',
              borderRadius: '20px',
              padding: '10px 18px',
              fontSize: '15px',
              fontWeight: '600'
          }
        })
      })
    }

  nodes.value = newNodes
  edges.value = newEdges
}, { immediate: true })
</script>

<style>
/* Vue Flow styles are imported in main.js */
</style>
