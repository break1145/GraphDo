<template>
  <div class="flex items-start justify-between mb-4">
    <div class="flex items-start space-x-4 flex-1">
      <button
        @click="toggleTodo"
        :class="[
          'w-5 h-5 rounded-full border-2 flex items-center justify-center mt-1 flex-shrink-0',
          todo.status === 'completed'
            ? 'bg-green-500 border-green-500'
            : 'border-gray-300 hover:border-blue-500'
        ]"
      >
        <Check v-if="todo.status === 'completed'" class="w-3 h-3 text-white" />
      </button>
      <div class="flex-1">
        <!-- Task Title -->
        <div v-if="!isEditing">
          <h3
            :class="[
              'font-semibold text-lg mb-2',
              todo.status === 'completed' ? 'text-gray-500 line-through' : 'text-gray-900'
            ]"
          >
            {{ todo.task }}
          </h3>
        </div>
        <div v-else class="mb-2">
          <input
            v-model="editedTodo.task"
            class="w-full font-semibold text-lg border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-blue-500"
            placeholder="任务标题"
          />
        </div>
        
        <!-- Status and Time Info -->
        <div class="flex items-center space-x-4 mb-3">
          <div v-if="!isEditing">
            <span
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                getStatusClass(todo.status)
              ]"
            >
              {{ todo.status }}
            </span>
          </div>
          <div v-else>
            <select
              v-model="editedTodo.status"
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium border border-gray-300 focus:outline-none focus:border-blue-500',
                getStatusClass(editedTodo.status)
              ]"
            >
              <option value="not started">not started</option>
              <option value="in progress">in progress</option>
              <option value="completed">completed</option>
            </select>
          </div>
          
          <span v-if="todo.deadline" class="text-xs text-gray-500 flex items-center">
            <Calendar class="w-3 h-3 mr-1" />
            <span v-if="!isEditing">{{ formatDate(todo.deadline) }}</span>
            <input
              v-else
              v-model="editedTodo.deadline"
              type="date"
              class="border border-gray-300 rounded px-1 text-xs focus:outline-none focus:border-blue-500"
            />
          </span>
          
          <span v-if="todo.time_to_complete" class="text-xs text-blue-600 flex items-center">
            <Clock class="w-3 h-3 mr-1" />
            <span v-if="!isEditing">{{ formatTimeToComplete(todo.time_to_complete) }}</span>
            <input
              v-else
              v-model.number="editedTodo.time_to_complete"
              type="number"
              min="0"
              class="w-16 border border-gray-300 rounded px-1 text-xs focus:outline-none focus:border-blue-500"
              placeholder="分钟"
            />
          </span>
        </div>

        <!-- Solutions -->
        <div v-if="todo.solutions.length > 0 || isEditing" class="mb-3">
          <h4 class="text-sm font-medium text-gray-700 mb-2">解决方案:</h4>
          <div v-if="!isEditing">
            <ul class="space-y-1">
              <li 
                v-for="(solution, sIndex) in todo.solutions" 
                :key="sIndex"
                class="text-sm text-gray-600 flex items-start"
              >
                <span class="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                {{ solution }}
              </li>
            </ul>
          </div>
          <div v-else class="space-y-2">
            <div 
              v-for="(solution, sIndex) in editedTodo.solutions" 
              :key="sIndex"
              class="flex items-center space-x-2"
            >
              <input
                v-model="editedTodo.solutions[sIndex]"
                class="flex-1 text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-blue-500"
                placeholder="解决方案"
              />
              <button
                @click="removeSolution(sIndex)"
                class="text-red-500 hover:text-red-700"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
            <button
              @click="addSolution"
              class="text-blue-500 hover:text-blue-700 text-sm flex items-center"
            >
              <Plus class="w-4 h-4 mr-1" />
              添加解决方案
            </button>
          </div>
        </div>

        <!-- Planned Edits -->
        <div v-if="todo.planned_edits.length > 0 || isEditing">
          <h4 class="text-sm font-medium text-gray-700 mb-2">计划</h4>
          <div v-if="!isEditing">
            <ul class="space-y-1">
              <li 
                v-for="(edit, eIndex) in todo.planned_edits" 
                :key="eIndex"
                class="text-sm text-gray-600 flex items-start"
              >
                <span class="w-1.5 h-1.5 bg-orange-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                {{ edit }}
              </li>
            </ul>
          </div>
          <div v-else class="space-y-2">
            <div 
              v-for="(edit, eIndex) in editedTodo.planned_edits" 
              :key="eIndex"
              class="flex items-center space-x-2"
            >
              <input
                v-model="editedTodo.planned_edits[eIndex]"
                class="flex-1 text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-blue-500"
                placeholder="计划编辑"
              />
              <button
                @click="removeEdit(eIndex)"
                class="text-red-500 hover:text-red-700"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
            <button
              @click="addEdit"
              class="text-blue-500 hover:text-blue-700 text-sm flex items-center"
            >
              <Plus class="w-4 h-4 mr-1" />
              添加计划
            </button>
          </div>
        </div>

        <!-- Edit/Save Buttons -->
        <div class="mt-4 flex space-x-2">
          <button
            v-if="!isEditing"
            @click="startEdit"
            class="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
          >
            编辑
          </button>
          <template v-else>
            <button
              @click="saveChanges"
              :disabled="isSaving"
              class="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 disabled:opacity-50 transition-colors"
            >
              {{ isSaving ? '保存中...' : '保存' }}
            </button>
            <button
              @click="cancelEdit"
              :disabled="isSaving"
              class="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600 disabled:opacity-50 transition-colors"
            >
              取消
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Check, Calendar, Clock, X, Plus } from 'lucide-vue-next'
import { 
  getStatusClass, 
  formatDate, 
  formatTimeToComplete,
  updateTodo,
  type Todo 
} from '@/api/useApi'

interface Props {
  todo: Todo
  index: number
}

interface Emits {
  toggle: [index: number]
  update: [index: number, todo: Todo]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isEditing = ref(false)
const isSaving = ref(false)
const editedTodo = reactive<Todo>({
  task: '',
  key: '',
  status: 'not started',
  deadline: null,
  solutions: [],
  planned_edits: [],
  time_to_complete: null
})

const toggleTodo = () => {
  emit('toggle', props.index)
}

const startEdit = () => {
  isEditing.value = true
  // 深拷贝当前to do到编辑状态
  Object.assign(editedTodo, {
    ...props.todo,
    solutions: [...props.todo.solutions],
    planned_edits: [...props.todo.planned_edits]
  })
}

const cancelEdit = () => {
  isEditing.value = false
}

const saveChanges = async () => {
  isSaving.value = true
  try {
    const result = await updateTodo(props.todo.key || '', {
      task: editedTodo.task,
      status: editedTodo.status,
      deadline: editedTodo.deadline,
      solutions: editedTodo.solutions,
      planned_edits: editedTodo.planned_edits,
      time_to_complete: editedTodo.time_to_complete
    })
    
    if (result) {
      // 发射更新事件给父组件
      emit('update', props.index, { ...editedTodo })
      isEditing.value = false
      console.log('Todo保存成功')
    } else {
      console.error('保存失败')
      // 这里可以添加用户友好的错误提示
      alert('保存失败，请重试')
    }
  } catch (error) {
    console.error('保存出错:', error)
    alert('保存出错，请检查网络连接')
  } finally {
    isSaving.value = false
  }
}

const addSolution = () => {
  editedTodo.solutions.push('')
}

const removeSolution = (index: number) => {
  editedTodo.solutions.splice(index, 1)
}

const addEdit = () => {
  editedTodo.planned_edits.push('')
}

const removeEdit = (index: number) => {
  editedTodo.planned_edits.splice(index, 1)
}
</script>