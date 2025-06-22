<template>
  <AppLayout>
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-2xl shadow-xl border border-blue-100 overflow-hidden">
        <!-- Chat Header -->
        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
          <h2 class="text-xl font-semibold text-white flex items-center">
            <MessageCircle class="w-5 h-5 mr-2" />
            Chat with Todo Agent
          </h2>
          <p class="text-blue-100 text-sm mt-1">Ask me to manage your todos, set reminders, or get help!</p>
        </div>

        <!-- Messages -->
        <div class="h-96 overflow-y-auto p-6 space-y-4" ref="messagesContainer">
          <div
            v-for="message in messages"
            :key="message.id"
            :class="[
              'flex',
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-xs lg:max-w-md px-4 py-3 rounded-2xl',
                message.sender === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              ]"
            >
              <p class="text-sm whitespace-pre-wrap">{{ message.text }}</p>
              <span class="text-xs opacity-70 mt-1 block">{{ formatTime(message.timestamp) }}</span>
            </div>
          </div>
          <div v-if="isTyping" class="flex justify-start">
            <div class="bg-gray-100 px-4 py-3 rounded-2xl">
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Input -->
        <div class="border-t border-gray-200 p-4">
          <form @submit.prevent="sendMessage" class="flex space-x-3">
            <input
              v-model="newMessage"
              type="text"
              placeholder="Type your message..."
              class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              :disabled="isTyping || !currentUserId"
            />
            <button
              type="submit"
              :disabled="!newMessage.trim() || isTyping || !currentUserId"
              class="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <Send class="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { MessageCircle, Send } from 'lucide-vue-next'
import AppLayout from '@/components/AppLayout.vue'
import { 
  currentUserId, 
  sendChatMessage, 
  loadTodos,
  formatTime,
  type Message, 
  type ChatInput 
} from '@/api/useApi'

const newMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement>()

const messages = ref<Message[]>([
  {
    id: 1,
    text: "Hello! I'm your Todo Agent. How can I help you manage your tasks today?",
    sender: 'agent',
    timestamp: new Date()
  }
])

const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentUserId.value) return

  const userMessage: Message = {
    id: Date.now(),
    text: newMessage.value,
    sender: 'user',
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const messageText = newMessage.value
  newMessage.value = ''

  await nextTick()
  scrollToBottom()

  isTyping.value = true

  try {
    const chatInput: ChatInput = {
      user_id: currentUserId.value,
      input: messageText
    }

    const response = await sendChatMessage(chatInput)

    let agentResponseText = ''
    if (typeof response === 'string') {
      agentResponseText = response
    } else if (response.response) {
      agentResponseText = response.response
    } else if (response.message) {
      agentResponseText = response.message
    } else {
      agentResponseText = JSON.stringify(response)
    }

    const agentResponse: Message = {
      id: Date.now() + 1,
      text: agentResponseText,
      sender: 'agent',
      timestamp: new Date()
    }

    messages.value.push(agentResponse)
    await loadTodos()

  } catch (err) {
    const errorMessage: Message = {
      id: Date.now() + 1,
      text: `Sorry, I encountered an error: ${err instanceof Error ? err.message : 'Unknown error'}`,
      sender: 'agent',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
  } finally {
    isTyping.value = false
    nextTick(() => scrollToBottom())
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>