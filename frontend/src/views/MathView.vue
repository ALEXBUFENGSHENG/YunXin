<template>
  <div class="math-container">
    <!-- 左侧导航：任务与题库 -->
    <aside class="math-sidebar">
      <!-- ... (sidebar content unchanged) ... -->
      <div class="sidebar-header">
        <div class="header-top">
          <button class="back-btn" @click="goBack">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5"/>
              <path d="M12 19l-7-7 7-7"/>
            </svg>
            返回
          </button>
          <h2>考研数学一</h2>
        </div>
        <div class="target-badge">目标 140+</div>
      </div>
      
      <div class="task-section">
        <h3>今日任务</h3>
        <div v-for="task in todayTasks" :key="task.id" 
             :class="['task-card', { active: currentTaskId === task.id }]"
             @click="selectTask(task)">
          <span class="task-type" :class="task.type">{{ task.type_label }}</span>
          <p v-html="renderMarkdown(task.content)"></p>
          <div class="task-meta">{{ task.duration_min }}min</div>
        </div>
      </div>

      <div class="progress-stats">
        <h3>掌握度看板</h3>
        <div class="stat-grid">
          <div class="stat-item">
            <label>高数</label>
            <div class="progress-bar"><div class="fill" style="width: 65%"></div></div>
          </div>
          <div class="stat-item">
            <label>线代</label>
            <div class="progress-bar"><div class="fill" style="width: 40%"></div></div>
          </div>
          <div class="stat-item">
            <label>概率</label>
            <div class="progress-bar"><div class="fill" style="width: 20%"></div></div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 中间主区域：做题与交互 -->
    <main class="math-main">
      <header class="main-header">
        <div class="session-info">
          <span class="timer">已专注: {{ formatTime(spentTime) }}</span>
        </div>
        <button class="onboard-btn" @click="showOnboard = true">调整目标</button>
      </header>

      <div class="problem-area" v-if="currentProblem">
        <div class="problem-card">
          <div class="problem-tag" v-html="renderMarkdown(currentProblem.source || '真题题库')"></div>
          <div class="problem-stem" v-html="renderMarkdown(currentProblem.stem)"></div>
        </div>

        <div class="interaction-area">
          <div class="input-tabs">
            <button class="active">我的解题步骤</button>
            <button @click="showDraft = !showDraft">草稿纸</button>
          </div>
          <textarea 
            v-model="userSteps" 
            placeholder="请在此输入关键解题步骤或思路点... (支持 Markdown/LaTeX)"
            class="steps-input"
          ></textarea>
          
          <div class="action-footer">
            <div class="self-eval">
              <span>自评难度:</span>
              <div class="stars">
                <span v-for="i in 5" :key="i" @click="rating = i" :class="{ active: rating >= i }">★</span>
              </div>
            </div>
            <button class="submit-btn" @click="submitAttempt" :disabled="isSubmitting">
               {{ isSubmitting ? 'AI 阅卷中...' : '提交核对' }}
            </button>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else>
        <div class="empty-icon">📐</div>
        <p>选择一个任务开始今日修行</p>
        <button class="start-btn" @click="fetchTodayTasks">获取今日计划</button>
      </div>
    </main>

    <!-- 右侧：AI 诊断与反馈 (模块化组件) -->
    <transition name="slide">
      <MathDeepDiagnosis 
        v-if="analysisResult" 
        :result="analysisResult" 
        @close="analysisResult = null" 
      />
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { marked } from 'marked';
import MathDeepDiagnosis from '../components/math/MathDeepDiagnosis.vue';

const router = useRouter();

// ... (renderMarkdown and other utils unchanged) ...
import katex from 'katex';
import 'katex/dist/katex.min.css';

// Markdown 渲染配置 (保持不变)
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

const todayTasks = ref([]);
const currentTaskId = ref(null);
const currentProblem = ref(null);
const userSteps = ref('');
const rating = ref(0);
const spentTime = ref(0);
const showOnboard = ref(false);
const isSubmitting = ref(false);

// 新增：结构化分析结果
const analysisResult = ref(null);

// 构造传递给 DecompositionView 的数据 (已迁移到 MathDeepDiagnosis 组件内部)
// const decompositionData = computed(() => { ... });

// ... (fetch logic unchanged) ...
const selectTask = async (task) => {
  currentTaskId.value = task.id;
  if (task.metadata && task.metadata.problem_id) {
    await fetchProblem(task.metadata.problem_id);
    // 切换题目时清空上次分析
    analysisResult.value = null;
    userSteps.value = '';
  }
};

const fetchTodayTasks = async () => {
  try {
    const res = await axios.get(`/api/math/today?username=${localStorage.getItem('ai-assistant-username') || '访客'}`);
    if (res.data.tasks && res.data.tasks.length > 0) {
      todayTasks.value = res.data.tasks.map(t => ({...t, type_label: '真题'}));
      selectTask(todayTasks.value[0]);
    }
  } catch (e) { console.error(e); }
};

const fetchProblem = async (id) => {
  try {
    const res = await axios.get(`/api/math/problem/${id}`);
    currentProblem.value = res.data;
  } catch (e) { console.error(e); }
};

const submitAttempt = async () => {
  if (!currentProblem.value) return;
  isSubmitting.value = true;
  
  try {
    const payload = {
      username: localStorage.getItem('ai-assistant-username') || '访客',
      problem_id: currentProblem.value.id,
      self_score: rating.value,
      time_spent_sec: spentTime.value,
      user_steps: userSteps.value,
      key_check_result: { passed: true },
      error_tags: []
    };

    const res = await axios.post('/api/math/attempt', payload);
    
    if (res.data.status === 'success') {
      // 优先使用结构化分析，回退到 feedback 文本
      if (res.data.analysis) {
          analysisResult.value = res.data.analysis;
      } else {
          analysisResult.value = {
              feedback: res.data.feedback,
              scores: null,
              error_tags: [],
              solution_path: null
          };
      }
    }
  } catch (e) {
    console.error('提交失败', e);
    analysisResult.value = { feedback: "提交失败，请检查网络。" };
  } finally {
    isSubmitting.value = false;
  }
};

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const goBack = () => router.push('/');

onMounted(() => {
  fetchTodayTasks();
  setInterval(() => spentTime.value++, 1000);
});
</script>

<style scoped>
/* ... (Keep existing styles) ... */
.math-container {
  display: flex;
  height: 100vh;
  background: #f0f2f5;
  color: #2c3e50;
  font-family: 'Inter', system-ui, sans-serif;
}
.math-sidebar {
  width: 300px;
  background: white;
  border-right: 1px solid #e1e4e8;
  padding: 24px;
  display: flex;
  flex-direction: column;
}
.header-top { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.back-btn { display: flex; align-items: center; gap: 6px; background: #f0f2f5; border: 1px solid #e1e4e8; border-radius: 6px; padding: 6px 12px; font-size: 0.9rem; color: #666; cursor: pointer; transition: all 0.3s; }
.back-btn:hover { background: #e4e6e9; transform: translateX(-2px); }
.sidebar-header h2 { margin: 0; font-size: 1.5rem; color: #1a73e8; }
.target-badge { display: inline-block; padding: 4px 12px; background: #e8f0fe; color: #1a73e8; border-radius: 20px; font-size: 0.8rem; margin-top: 8px; }
.task-section { margin-top: 32px; flex: 1; }
.task-card { padding: 16px; background: #f8f9fa; border-radius: 12px; margin-bottom: 12px; cursor: pointer; transition: all 0.3s; border: 2px solid transparent; }
.task-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.task-card.active { border-color: #1a73e8; background: #fff; }
.task-type { font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; font-weight: bold; }
.task-type.review { background: #fff7e6; color: #fa8c16; }
.task-type.practice { background: #e6f7ff; color: #1890ff; }
.math-main { flex: 1; display: flex; flex-direction: column; padding: 24px; overflow-y: auto; }
.main-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.problem-card { background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 24px; }
.problem-tag { color: #999; font-size: 0.9rem; margin-bottom: 16px; }
.problem-stem { font-size: 1.25rem; line-height: 1.8; }
.interaction-area { background: white; border-radius: 16px; padding: 24px; display: flex; flex-direction: column; flex: 1; }
.steps-input { width: 100%; flex: 1; min-height: 200px; border: 1px solid #e1e4e8; border-radius: 8px; padding: 16px; font-family: inherit; font-size: 1rem; resize: none; margin: 16px 0; }
.action-footer { display: flex; justify-content: space-between; align-items: center; }
.stars span { font-size: 1.5rem; cursor: pointer; color: #ddd; }
.stars span.active { color: #fadb14; }
.submit-btn { background: #1a73e8; color: white; border: none; padding: 12px 32px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
.submit-btn:hover { background: #1557b0; }
.submit-btn:disabled { background: #ccc; cursor: not-allowed; }
.progress-bar { height: 8px; background: #eee; border-radius: 4px; margin-top: 4px; }
.progress-bar .fill { height: 100%; background: #1a73e8; border-radius: 4px; }

/* Enhanced Feedback Drawer Styles */
/* 样式已迁移到 MathDeepDiagnosis 组件 */
</style>
