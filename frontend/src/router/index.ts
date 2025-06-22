import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '@/pages/ChatView.vue'
import TodoView from '@/pages/TodoView.vue'
import ProfileView from '@/pages/ProfileView.vue'

const routes = [
  {
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatView
  },
  {
    path: '/todos',
    name: 'Todos', 
    component: TodoView
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router