import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../components/Chat.vue'
import AdminView from '../views/AdminView.vue'
import LoginView from '../views/LoginView.vue'
import LearningView from '../views/LearningView.vue'
import MathView from '../views/MathView.vue'
import { getAdminToken } from '../utils/api'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: ChatView,
    meta: {
      title: 'AI 助教聊天'
    }
  },
  {
    path: '/math',
    name: 'Math',
    component: MathView,
    meta: {
      title: '考研数学专栏'
    }
  },
  {
    path: '/learn',
    name: 'Learning',
    component: LearningView,
    meta: {
      title: '云心学习模式'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      title: '管理员登录'
    }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: {
      title: '管理员控制台',
      requiresAuth: true
    }
  },
  {
    // 404 页面
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由标题设置
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'AI 助教'
  const token = getAdminToken()

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (to.name === 'Login' && token) {
    return next('/admin')
  }

  next()
})

export default router
