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
  status: 'not started' | 'in progress' | 'completed'
  deadline: string | null
  solutions: string[]
  planned_edits: string[]
  time_to_complete: number | null
}

export interface UserProfile {
  id?: string
  name?: string
  job?: string
  location?: string
  interests?: []
  connections?: []
  [key: string]: any
}

export interface UserInstructions {
  response?: Array<{
    content: string
    language: string
  }>
  [key: string]: any
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

// 发送消息
export const sendChatMessage = async (chatInput: ChatInput) => {
  return await apiCall('/agent/chat', {
    method: 'POST',
    body: JSON.stringify(chatInput),
  })
}


// 获取to do列表
export const loadTodos = async () => {
  if (!currentUserId.value) return []

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/agent/todos/${currentUserId.value}`)

    // 根据新的API格式处理响应
    if (response.response && Array.isArray(response.response)) {
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

// 按id获取profile
export const loadProfile = async () => {
  if (!currentUserId.value) return {}

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/agent/profile/${currentUserId.value}`)
    // console.log((response["response"][0]))
    return response["response"][0] || {}
  } catch (err) {
    error.value = `Failed to load profile: ${err instanceof Error ? err.message : 'Unknown error'}`
    return {}
  } finally {
    isLoading.value = false
  }
}

// 按id获取偏好
export const loadInstructions = async () => {
  if (!currentUserId.value) return { response: [] }

  try {
    isLoading.value = true
    error.value = ''
    const response = await apiCall(`/agent/instructions/${currentUserId.value}`)
    return response["response"] || { response: [] }
  } catch (err) {
    error.value = `Failed to load instructions: ${err instanceof Error ? err.message : 'Unknown error'}`
    return { response: [] }
  } finally {
    isLoading.value = false
  }
}

// 获取不同状态的css
export const getStatusClass = (status: string): string => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'in progress':
      return 'bg-blue-100 text-blue-800'
    case 'not started':
      return 'bg-gray-100 text-gray-800'
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