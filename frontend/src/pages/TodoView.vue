<template>
  <AppLayout>
    <div class="max-w-6xl mx-auto">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h2 class="text-3xl font-bold text-gray-900">Your Todos</h2>
          <p class="text-gray-600 mt-1">Manage your tasks efficiently</p>
        </div>
        <button
          @click="refreshTodos"
          :disabled="!currentUserId"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors duration-200 flex items-center space-x-2"
        >
          <RefreshCw class="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      <!-- Todo Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl p-6 shadow-lg border border-blue-100">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Tasks</p>
              <p class="text-2xl font-bold text-gray-900">{{ todos.length }}</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <List class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-lg border border-green-100">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Completed</p>
              <p class="text-2xl font-bold text-gray-900">{{ completedTodos }}</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-lg border border-orange-100">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Pending</p>
              <p class="text-2xl font-bold text-gray-900">{{ pendingTodos }}</p>
            </div>
            <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Clock class="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Todo List -->
      <div class="space-y-4">
        <div
          v-for="todo in todos"
          :key="todo.id"
          class="bg-white rounded-xl p-6 shadow-lg border border-blue-100 hover:shadow-xl transition-shadow duration-200"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-4">
              <button
                @click="toggleTodo(todo.id)"
                :class="[
                  'w-5 h-5 rounded-full border-2 flex items-center justify-center mt-1',
                  todo.completed
                    ? 'bg-green-500 border-green-500'
                    : 'border-gray-300 hover:border-blue-500'
                ]"
              >
                <Check v-if="todo.completed" class="w-3 h-3 text-white" />
              </button>
              <div class="flex-1">
                <h3
                  :class="[
                    'font-semibold text-lg',
                    todo.completed ? 'text-gray-500 line-through' : 'text-gray-900'
                  ]"
                >
                  {{ todo.title }}
                </h3>
                <p
                  :class="[
                    'text-sm mt-1',
                    todo.completed ? 'text-gray-400' : 'text-gray-600'
                  ]"
                >
                  {{ todo.description }}
                </p>
                <div class="flex items-center space-x-4 mt-3">
                  <span
                    v-if="todo.priority"
                    :class="[
                      'px-3 py-1 rounded-full text-xs font-medium',
                      getPriorityClass(todo.priority)
                    ]"
                  >
                    {{ todo.priority }}
                  </span>
                  <span v-if="todo.due_date" class="text-xs text-gray-500 flex items-center">
                    <Calendar class="w-3 h-3 mr-1" />
                    {{ formatDate(todo.due_date) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="todos.length === 0 && !isLoading" class="text-center py-12">
        <div class="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckSquare class="w-12 h-12 text-blue-500" />
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No todos yet</h3>
        <p class="text-gray-600">Start by chatting with the agent to create your first todo!</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RefreshCw, List, CheckCircle, Clock, Check, Calendar, CheckSquare } from 'lucide-vue-next'
import AppLayout from '@/components/AppLayout.vue'
import { 
  currentUserId, 
  isLoading,
  loadTodos,
  getPriorityClass,
  formatDate,
  type Todo 
} from '@/composables/useApi'

const todos = ref<Todo[]>([])

const completedTodos = computed(() => todos.value.filter(todo => todo.completed).length)
const pendingTodos = computed(() => todos.value.filter(todo => !todo.completed).length)

const refreshTodos = async () => {
  todos.value = await loadTodos()
}

const toggleTodo = async (id: string | number) => {
  const todo = todos.value.find(t => t.id === id)
  if (todo) {
    todo.completed = !todo.completed
  }
}

onMounted(() => {
  refreshTodos()
})
</script>