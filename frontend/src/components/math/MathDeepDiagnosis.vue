<template>
  <div class="math-deep-diagnosis">
    <div class="feedback-header">
      <div class="header-title">
        <span class="icon">🧠</span>
        <h3>云心深度诊断模型</h3>
      </div>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <div class="feedback-content-scroll">
      <!-- 1. 评分雷达 -->
      <div class="analysis-section" v-if="result.scores">
        <h4><span class="section-icon">📊</span> 维度评分</h4>
        <div class="score-grid">
          <div v-for="(score, key) in result.scores" :key="key" class="score-item">
            <span class="score-label">{{ translateScoreKey(key) }}</span>
            <div class="progress-bg">
              <div class="progress-fill" 
                   :class="getScoreClass(score)"
                   :style="{ width: (score * 100) + '%' }"></div>
            </div>
            <span class="score-val" :class="getScoreTextClass(score)">{{ (score * 100).toFixed(0) }}</span>
          </div>
        </div>
      </div>

      <!-- 2. 错误诊断 -->
      <div class="analysis-section" v-if="result.error_tags && result.error_tags.length">
        <h4><span class="section-icon">🩺</span> 错误诊断</h4>
        <div class="tags-container">
          <span v-for="tag in result.error_tags" :key="tag" class="error-tag">
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- 3. 名师点评 -->
      <div class="analysis-section">
        <h4><span class="section-icon">👨‍🏫</span> 名师点评</h4>
        <div class="markdown-body comment-box" v-html="renderMarkdown(result.feedback)"></div>
      </div>

      <!-- 4. 思路引导 -->
      <div class="analysis-section" v-if="result.guidance">
        <h4><span class="section-icon">💡</span> 思路引导</h4>
        <div class="guidance-box">
          {{ result.guidance }}
        </div>
      </div>

      <!-- 5. 解题路径可视化 -->
      <div class="analysis-section full-width" v-if="result.solution_path">
        <h4><span class="section-icon">🕸️</span> 标准解题路径可视化</h4>
        <div class="viz-container">
          <DecompositionView :data="decompositionData" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import DecompositionView from '../agents/DecompositionView.vue';

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
});

defineEmits(['close']);

// 构造传递给 DecompositionView 的数据
const decompositionData = computed(() => {
  if (!props.result || !props.result.solution_path) return {};
  return {
    "知识体系": { "root": "标准解题路径" },
    "核心概念": props.result.solution_path
  };
});

const translateScoreKey = (key) => {
  const map = {
    'logic': '逻辑严密性',
    'calculation': '计算准确度',
    'completeness': '步骤完整性',
    'mastery': '知识掌握度'
  };
  return map[key] || key;
};

const getScoreClass = (score) => {
  if (score >= 0.8) return 'bg-green-500';
  if (score >= 0.6) return 'bg-blue-500';
  return 'bg-amber-500';
};

const getScoreTextClass = (score) => {
  if (score >= 0.8) return 'text-green-600';
  if (score >= 0.6) return 'text-blue-600';
  return 'text-amber-600';
};

// Markdown 渲染 (复用逻辑)
const renderMarkdown = (text) => {
  if (!text) return '';
  const formulaRegex = /\$\$([\s\S]*?)\$\$|\$((?:\\.|[^\\$])*)\$/g;
  const formulas = [];
  const protectedText = text.replace(formulaRegex, (match, display, inline) => {
    formulas.push({ display, inline, match });
    return `FORMULA-PLACEHOLDER-${formulas.length - 1}`;
  });
  let html = marked(protectedText);
  html = html.replace(/FORMULA-PLACEHOLDER-(\d+)/g, (_, index) => {
    const { display, inline, match } = formulas[index];
    const formula = display || inline;
    const isDisplay = !!display;
    try {
      return katex.renderToString(formula, { throwOnError: false, displayMode: isDisplay });
    } catch (e) { return match; }
  });
  return html;
};
</script>

<style scoped>
.math-deep-diagnosis {
  width: 480px;
  background: #fff;
  border-left: 1px solid #e1e4e8;
  display: flex;
  flex-direction: column;
  box-shadow: -10px 0 30px rgba(0,0,0,0.08);
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  font-family: 'Inter', sans-serif;
}

.feedback-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title .icon {
  font-size: 1.2rem;
}

.feedback-header h3 {
  margin: 0;
  color: #0f172a;
  font-size: 1.1rem;
  font-weight: 700;
}

.close-btn {
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #475569;
}

.feedback-content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.analysis-section {
  margin-bottom: 32px;
}

.analysis-section h4 {
  margin: 0 0 16px 0;
  font-size: 0.95rem;
  color: #334155;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  font-size: 1rem;
}

.score-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-label {
  width: 90px;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.progress-bg {
  flex: 1;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease-out;
}

.bg-green-500 { background-color: #22c55e; }
.bg-blue-500 { background-color: #3b82f6; }
.bg-amber-500 { background-color: #f59e0b; }

.score-val {
  font-weight: 800;
  width: 30px;
  text-align: right;
  font-size: 0.9rem;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.error-tag {
  background: #fef2f2;
  color: #ef4444;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid #fecaca;
}

.comment-box {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #334155;
}

.guidance-box {
  background: #eff6ff;
  padding: 16px;
  border-radius: 12px;
  color: #1e40af;
  font-size: 0.9rem;
  line-height: 1.6;
  border: 1px solid #dbeafe;
}

.viz-container {
  height: 320px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
</style>