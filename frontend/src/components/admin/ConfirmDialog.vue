<script setup lang="ts">
defineProps<{
  title?: string
  message?: string
  confirmText?: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white dark:bg-[#1a1a1a] rounded-lg shadow-xl p-6 w-full max-w-sm mx-4">
      <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">
        {{ title || '确认操作' }}
      </h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
        {{ message || '此操作不可撤销，是否继续？' }}
      </p>
      <div class="flex gap-3 justify-end">
        <button
          @click="emit('cancel')"
          class="px-4 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          取消
        </button>
        <button
          @click="emit('confirm')"
          :disabled="loading"
          class="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 transition-colors"
        >
          {{ loading ? '处理中...' : (confirmText || '确认') }}
        </button>
      </div>
    </div>
  </div>
</template>
