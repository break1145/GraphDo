<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
    <!-- Header -->
    <header class="bg-white/80 backdrop-blur-sm border-b border-blue-200 sticky top-0 z-50 flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <CheckSquare class="w-5 h-5 text-white" />
            </div>
            <h1 class="text-xl font-bold text-gray-900">Graph Do</h1>
          </div>
          
          <!-- User ID Input -->
          <div class="flex items-center space-x-3">
            <div class="flex items-center space-x-2 bg-white/60 backdrop-blur-sm rounded-lg px-3 py-2 border border-blue-200">
              <User class="w-4 h-4 text-gray-500" />
              <input
                id="userId"
                v-model="currentUserId"
                type="text"
                placeholder="Enter User ID"
                class="bg-transparent border-0 outline-none text-sm text-gray-700 placeholder-gray-500 w-32 focus:w-40 transition-all duration-200"
              />
              <button
                @click="loadUserData"
                class="ml-2 px-3 py-1 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-xs rounded-md hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 shadow-sm hover:shadow-md"
              >
                Load
              </button>
            </div>
          </div>
          
          <nav class="flex space-x-1">
            <router-link
              v-for="tab in tabs"
              :key="tab.path"
              :to="tab.path"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all duration-200',
                $route.path === tab.path
                  ? 'bg-blue-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              ]"
            >
              <component :is="tab.icon" class="w-4 h-4 inline mr-2" />
              {{ tab.name }}
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content - 使用 flex-1 填满剩余空间 -->
    <main class="flex-1 flex flex-col">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 mx-4">
        <div class="flex items-center">
          <AlertCircle class="w-5 h-5 text-red-500 mr-2" />
          <span class="text-red-700">{{ error }}</span>
        </div>
      </div>

      <!-- Page Content - 填满剩余空间 -->
      <div class="flex-1 flex flex-col">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { CheckSquare, MessageCircle, User, AlertCircle } from 'lucide-vue-next'
import { currentUserId, isLoading, error, loadTodos, loadProfile, loadInstructions } from '@/api/useApi'

const tabs = [
  { path: '/chat', name: 'Chat', icon: MessageCircle },
  { path: '/todos', name: 'Todos', icon: CheckSquare },
  { path: '/profile', name: 'Profile', icon: User }
]

const loadUserData = async () => {
  if (!currentUserId.value) {
    error.value = 'Please enter a user ID'
    return
  }

  error.value = ''
  await Promise.all([
    loadTodos(),
    loadProfile(),
    loadInstructions()
  ])
}
</script>