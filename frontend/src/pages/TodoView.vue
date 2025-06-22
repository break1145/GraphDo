<template>
  <AppLayout>
    <div class="max-w-4xl mx-auto p-6">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Todo List</h1>
        <p class="text-gray-600">Manage your tasks and stay organized</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <div class="flex items-center">
            <ListTodo class="w-8 h-8 text-blue-500 mr-3" />
            <div>
              <p class="text-sm font-medium text-blue-600">Total Tasks</p>
              <p class="text-2xl font-bold text-blue-900">{{ todos.length }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-green-50 rounded-lg p-6 border border-green-200">
          <div class="flex items-center">
            <CheckCircle class="w-8 h-8 text-green-500 mr-3" />
            <div>
              <p class="text-sm font-medium text-green-600">Completed</p>
              <p class="text-2xl font-bold text-green-900">{{ completedCount }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-orange-50 rounded-lg p-6 border border-orange-200">
          <div class="flex items-center">
            <Clock class="w-8 h-8 text-orange-500 mr-3" />
            <div>
              <p class="text-sm font-medium text-orange-600">In Progress</p>
              <p class="text-2xl font-bold text-orange-900">{{ inProgressCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Todos List -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">Your Tasks</h2>
          <button
            @click="refreshTodos"
            :disabled="!currentUserId"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors duration-200 flex items-center space-x-2"
          >
            <RefreshCw class="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
        
        <div class="p-6">
          <div v-if="todos.length === 0" class="text-center py-12">
            <ListTodo class="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">No todos yet</h3>
            <p class="text-gray-500">Start chatting with the agent to create your first todo!</p>
          </div>
          
          <div v-else class="space-y-6">
            <TodoItem
              v-for="(todo, index) in todos"
              :key="index"
              :todo="todo"
              :index="index"
              @toggle="toggleTodo"
              @update="updateTodo"
            />
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ListTodo, CheckCircle, Clock, RefreshCw } from 'lucide-vue-next'
import AppLayout from '@/components/AppLayout.vue'
import TodoItem from '@/components/TodoItem.vue'
import { 
  currentUserId,
  loadTodos,
  type Todo 
} from '@/api/useApi'

const todos = ref<Todo[]>([])

const completedCount = computed(() => 
  todos.value.filter(todo => todo.status === 'completed').length
)

const inProgressCount = computed(() => 
  todos.value.filter(todo => todo.status === 'in progress').length
)

const refreshTodos = async () => {
  todos.value = await loadTodos()
}

const toggleTodo = async (index: number) => {
  const todo = todos.value[index]
  if (todo) {
    todo.status = todo.status === 'completed' ? 'not started' : 'completed'
    // 这里可以调用API保存状态变更
  }
}

const updateTodo = (index: number, updatedTodo: Todo) => {
  if (index >= 0 && index < todos.value.length) {
    todos.value[index] = updatedTodo
  }
}

onMounted(() => {
  refreshTodos()
})
</script>