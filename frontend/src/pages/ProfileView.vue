<template>
  <AppLayout>
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-2xl shadow-xl border border-blue-100 overflow-hidden">
        <!-- Profile Header -->
        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 px-8 py-12 text-center">
          <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto mb-4">
            <User class="w-5 h-5 mr-2 text-blue-500" />
          </div>
          <h2 class="text-2xl font-bold text-white">{{ userProfile.name || 'User Profile' }}</h2>
          <p class="text-blue-100 mt-1">{{ userProfile.email || currentUserId }}</p>
        </div>

        <!-- Profile Content -->
        <div class="p-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- User Information -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <User class="w-5 h-5 mr-2 text-blue-500" />
                Profile Information
              </h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">User ID</label>
                  <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{{ currentUserId || 'Not set' }}</div>
                </div>
                <div v-if="userProfile.name">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{{ userProfile.name }}</div>
                </div>
                <div v-if="userProfile.job">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Job</label>
                  <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{{ userProfile.job }}</div>
                </div>
                <div v-if="userProfile.location">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{{ userProfile.location }}</div>
                </div>
                <div v-if="userProfile.interests">
                  <label class="block text-sm font-medium text-gray-700 mb-1">interests</label>
                  <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{{ userProfile.interests }}</div>
                </div>
                <div v-if="userProfile.connections">
                  <label class="block text-sm font-medium text-gray-700 mb-1">connections</label>
                  <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{{ userProfile.connections }}</div>
                </div>
              </div>
            </div>

            <!-- User Instructions -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FileText class="w-5 h-5 mr-2 text-blue-500" />
                Agent Instructions
              </h3>
              <div v-if="userInstructions && userInstructions.length > 0" class="space-y-4">
                <div 
                  v-for="(instruction, index) in userInstructions"
                  :key="index"
                  class="bg-blue-50 rounded-lg p-6 border border-blue-200"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-blue-600">{{ instruction.language }}</span>
                  </div>
                  <div class="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {{ instruction.content }}
                  </div>
                </div>
              </div>
              <div v-else class="bg-blue-50 rounded-lg p-6 border border-blue-200">
                <p class="text-gray-700 leading-relaxed">
                  No instructions set yet. Chat with the agent to set up your preferences!
                </p>
              </div>
              <button
                @click="refreshInstructions"
                :disabled="!currentUserId"
                class="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors duration-200 flex items-center space-x-2"
              >
                <RefreshCw class="w-4 h-4" />
                <span>Refresh Instructions</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { User, FileText, RefreshCw } from 'lucide-vue-next'
import AppLayout from '@/components/AppLayout.vue'
import { 
  currentUserId,
  loadProfile,
  loadInstructions,
  formatDate,
  type UserProfile,
  type UserInstructions 
} from '@/api/useApi'

const userProfile = ref<UserProfile>({})
const userInstructions = ref<UserInstructions>({})

const refreshProfile = async () => {
  userProfile.value = await loadProfile()
  // console.log(userProfile.value)
}

const refreshInstructions = async () => {
  userInstructions.value = await loadInstructions()
}

onMounted(() => {
  refreshProfile()
  refreshInstructions()
})
</script>