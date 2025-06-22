import { ref } from 'vue'

// Types
export interface Message {
  id: number
  text: string
  sender: 'user' | 'agent'
  timestamp: Date
}

export interface Todo {
  task: string
  key?: string
  status: 'not started' | 'in progress' | 'done' | 'archived' | 'completed'
  deadline: string | null
  solutions: string[]
  planned_edits: string[]
  time_to_complete: number | null
}

export interface UserProfile {
  name?: string
  job?: string
  key?: string
  location?: string
  interests?: string[]
  connections?: string[]
}

// 单个指令的基础类型
export interface Instruction {
  language: string
  content: string
  key: string
}

// API响应包装器，重用Instruction类型
export interface UserInstructions {
  response?: Instruction[]  // 直接使用Instruction[]而不是内联类型
  key?: string
}


export interface ChatInput {
  user_id: string
  input: string
}

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000'

// Shared state
export const currentUserId = ref<string>('1')
export const isLoading = ref(false)
export const error = ref<string>('')

// API Functions
export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  try {
    console.log('API CALLED' + `${API_BASE_URL}${endpoint}`)
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (err) {
    console.error('API call failed:', err)
    throw err
  }
}

// ==================== Chat API ====================

// 发送消息
export const sendChatMessage = async (chatInput: ChatInput) => {
  return await apiCall('/agent/chat', {
    method: 'POST',
    body: JSON.stringify(chatInput),
  })
}

// ==================== To do CRUD ====================

// 获取to do列表
export const loadTodos = async () => {
  if (!currentUserId.value) return []

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/api/todos/${currentUserId.value}`)

    if (response.success && Array.isArray(response.response)) {
      return response.response
    } else if (Array.isArray(response)) {
      return response
    } else {
      return []
    }
  } catch (err) {
    error.value = `Failed to load todos: ${err instanceof Error ? err.message : 'Unknown error'}`
    return []
  } finally {
    isLoading.value = false
  }
}

// 创建新的待办事项
export const createTodo = async (todo: Omit<Todo, 'key'>) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall('/api/todos', {
      method: 'POST',
      body: JSON.stringify({
        user_id: currentUserId.value,
        ...todo
      })
    })
    return response.success
  } catch (err) {
    error.value = `Failed to create todo: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// 更新待办事项
export const updateTodo = async (key: string, todo: Omit<Todo, 'key'>) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/api/todos/${currentUserId.value}/${key}`, {
      method: 'PUT',
      body: JSON.stringify({
        user_id: currentUserId.value,
        ...todo
      })
    })
    return response.success
  } catch (err) {
    error.value = `Failed to update todo: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// 删除待办事项
export const deleteTodo = async (key: string) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/api/todos/${currentUserId.value}/${key}`, {
      method: 'DELETE'
    })
    return response.success
  } catch (err) {
    error.value = `Failed to delete todo: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// ==================== Profile CRUD ====================

// 获取用户档案
export const loadProfile = async () => {
  if (!currentUserId.value) return {}

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/api/profile/${currentUserId.value}`)
    return response.success ? response.response : {}
  } catch (err) {
    error.value = `Failed to load profile: ${err instanceof Error ? err.message : 'Unknown error'}`
    return {}
  } finally {
    isLoading.value = false
  }
}

// 创建用户档案
export const createProfile = async (profile: UserProfile) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall('/api/profile', {
      method: 'POST',
      body: JSON.stringify({
        user_id: currentUserId.value,
        ...profile
      })
    })
    return response.success
  } catch (err) {
    error.value = `Failed to create profile: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// 更新用户档案
export const updateProfile = async (profile: UserProfile) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/api/profile/${currentUserId.value}`, {
      method: 'PUT',
      body: JSON.stringify({
        user_id: currentUserId.value,
        ...profile
      })
    })
    return response.success
  } catch (err) {
    error.value = `Failed to update profile: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// ==================== Instructions CRUD ====================

// 获取用户指令
export const loadInstructions = async () => {
  if (!currentUserId.value) return { response: [] }

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/api/instructions/${currentUserId.value}`)
    console.log(response)
    return response.success ? { response: response.response } : { response: [] }
  } catch (err) {
    error.value = `Failed to load instructions: ${err instanceof Error ? err.message : 'Unknown error'}`
    return { response: [] }
  } finally {
    isLoading.value = false
  }
}

// 创建新指令
export const createInstruction = async (instruction: Instruction) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall('/api/instructions', {
      method: 'POST',
      body: JSON.stringify({
        user_id: currentUserId.value,
        ...instruction
      })
    })
    return response.success
  } catch (err) {
    error.value = `Failed to create instruction: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// 更新指令
export const updateInstruction = async (key: string, instruction: Instruction) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    console.log("update inst: key = " + key + " inst = " + instruction)
    const response = await apiCall(`/api/instructions/${currentUserId.value}/${key}`, {
      method: 'PUT',
      body: JSON.stringify(instruction)
    })
    return response.success
  } catch (err) {
    error.value = `Failed to update instruction: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// 删除指令
export const deleteInstruction = async (key: string) => {
  if (!currentUserId.value) return false

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/api/instructions/${currentUserId.value}/${key}`, {
      method: 'DELETE'
    })
    return response.success
  } catch (err) {
    error.value = `Failed to delete instruction: ${err instanceof Error ? err.message : 'Unknown error'}`
    return false
  } finally {
    isLoading.value = false
  }
}

// ==================== Utility Functions ====================

// 获取不同状态的css
export const getStatusClass = (status: string): string => {
  switch (status?.toLowerCase()) {
    case 'done':
      return 'bg-green-100 text-green-800'
    case 'in progress':
      return 'bg-blue-100 text-blue-800'
    case 'not started':
      return 'bg-gray-100 text-gray-800'
    case 'archived':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export const formatTime = (date: Date): string => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString([], {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

export const formatTimeToComplete = (minutes: number | null): string => {
  if (!minutes) return 'Not specified'
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (hours > 0) {
    return `${hours}h ${remainingMinutes}m`
  }
  return `${remainingMinutes}m`
}