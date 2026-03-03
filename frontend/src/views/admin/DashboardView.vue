<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statsApi } from '@/api/stats'
import type { Stats } from '@/types'

const stats = ref<Stats | null>(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    stats.value = await statsApi.get()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">概览</h1>

    <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="h-24 bg-gray-100 dark:bg-gray-900 rounded-lg animate-pulse" />
    </div>

    <div v-else-if="stats" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg p-5">
        <p class="text-xs text-gray-400 dark:text-gray-600 mb-1">总文章数</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total_articles }}</p>
      </div>
      <div class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg p-5">
        <p class="text-xs text-gray-400 dark:text-gray-600 mb-1">已发布</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.published_articles }}</p>
      </div>
      <div class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg p-5">
        <p class="text-xs text-gray-400 dark:text-gray-600 mb-1">总阅读量</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total_views }}</p>
      </div>
      <div class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg p-5">
        <p class="text-xs text-gray-400 dark:text-gray-600 mb-1">待审评论</p>
        <p class="text-3xl font-bold" :class="stats.pending_comments > 0 ? 'text-orange-500' : 'text-gray-900 dark:text-gray-100'">
          {{ stats.pending_comments }}
        </p>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="mt-8">
      <h2 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">快速操作</h2>
      <div class="flex gap-3">
        <RouterLink to="/admin/articles/new" class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 transition-opacity">
          写新文章
        </RouterLink>
        <RouterLink to="/admin/comments" class="px-4 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-700 dark:text-gray-300">
          审核评论
        </RouterLink>
      </div>
    </div>
  </div>
</template>
