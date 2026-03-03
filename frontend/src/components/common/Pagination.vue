<script setup lang="ts">
defineProps<{
  currentPage: number
  totalPages: number
}>()

const emit = defineEmits<{
  (e: 'change', page: number): void
}>()
</script>

<template>
  <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-10">
    <button
      :disabled="currentPage <= 1"
      @click="emit('change', currentPage - 1)"
      class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
    >
      上一页
    </button>

    <template v-for="p in totalPages" :key="p">
      <button
        @click="emit('change', p)"
        :class="[
          'px-3 py-1.5 text-sm rounded transition-colors',
          p === currentPage
            ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900'
            : 'border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800',
        ]"
      >
        {{ p }}
      </button>
    </template>

    <button
      :disabled="currentPage >= totalPages"
      @click="emit('change', currentPage + 1)"
      class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
    >
      下一页
    </button>
  </div>
</template>
