<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ArticleSummary } from '@/types'
import { articlesApi } from '@/api/articles'
import { usePagination } from '@/composables/usePagination'
import ArticleCard from '@/components/article/ArticleCard.vue'
import Pagination from '@/components/common/Pagination.vue'

const route = useRoute()
const router = useRouter()
const query = ref((route.query.q as string) || '')
const articles = ref<ArticleSummary[]>([])
const loading = ref(false)
const searched = ref(false)
const pagination = usePagination(10)

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await articlesApi.list({
      q: query.value.trim(),
      page: pagination.currentPage.value,
      size: pagination.pageSize.value,
    })
    articles.value = res.items
    pagination.setFromResponse(res)
  } finally {
    loading.value = false
  }
}

function handleSubmit() {
  pagination.currentPage.value = 1
  router.replace({ query: { q: query.value } })
  search()
}

watch(() => route.query.q, (q) => {
  query.value = q as string || ''
  if (query.value) search()
})

onMounted(() => {
  if (query.value) search()
})
</script>

<template>
  <div>
    <header class="mb-8">
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">搜索</h1>
      <form @submit.prevent="handleSubmit" class="flex gap-2">
        <input
          v-model="query"
          placeholder="搜索文章..."
          class="flex-1 px-4 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600"
        />
        <button
          type="submit"
          class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 transition-opacity"
        >
          搜索
        </button>
      </form>
    </header>

    <div v-if="loading" class="text-sm text-gray-400">搜索中...</div>
    <div v-else-if="searched && !articles.length" class="py-20 text-center text-sm text-gray-400">
      未找到相关文章
    </div>
    <div v-else-if="articles.length">
      <p class="text-xs text-gray-400 dark:text-gray-600 mb-4">找到 {{ pagination.total.value }} 篇文章</p>
      <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
      <Pagination :current-page="pagination.currentPage.value" :total-pages="pagination.totalPages.value" @change="p => { pagination.goToPage(p); search() }" />
    </div>
  </div>
</template>
