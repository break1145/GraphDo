<template>
  <div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
    <div v-if="!isEditing">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-blue-600">{{ instruction.language }}</span>
        <button
          @click="startEdit"
          class="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
        >
          编辑
        </button>
      </div>
      <div class="text-gray-700 leading-relaxed whitespace-pre-wrap">
        {{ instruction.content }}
      </div>
    </div>
    
    <div v-else>
      <div class="flex items-center justify-between mb-4">
        <input
          v-model="editedInstruction.language"
          class="text-sm font-medium text-blue-600 bg-white border border-gray-300 rounded px-2 py-1 focus:outline-none focus:border-blue-500"
          placeholder="语言"
        />
        <div class="flex space-x-2">
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
        </div>
      </div>
      <textarea
        v-model="editedInstruction.content"
        class="w-full h-32 text-gray-700 leading-relaxed bg-white border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500 resize-vertical"
        placeholder="指令内容"
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { updateInstruction, type Instruction } from '@/api/useApi'

interface Props {
  instruction: Instruction
  instructionKey: string  // 将 key 改为 instructionKey
}

interface Emits {
  update: [instruction: Instruction]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isEditing = ref(false)
const isSaving = ref(false)
const editedInstruction = reactive<Instruction>({
  language: '',
  content: '',
  key: ''
})

const startEdit = () => {
  isEditing.value = true
  // 深拷贝当前指令到编辑状态
  Object.assign(editedInstruction, {
    language: props.instruction.language,
    content: props.instruction.content,
  })
}

const cancelEdit = () => {
  isEditing.value = false
}

const saveChanges = async () => {
  isSaving.value = true
  try {
    const result = await updateInstruction(props.instructionKey, {
      language: editedInstruction.language,
      content: editedInstruction.content,
      key: editedInstruction.key
    })
    
    if (result) {
      // 发射更新事件给父组件
      emit('update', { ...editedInstruction })
      isEditing.value = false
      console.log('指令保存成功')
    } else {
      console.error('保存失败')
      alert('保存失败，请重试')
    }
  } catch (error) {
    console.error('保存出错:', error)
    alert('保存出错，请检查网络连接')
  } finally {
    isSaving.value = false
  }
}
</script>