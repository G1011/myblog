<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { ArticleSummary } from '@/types'
import { articlesApi } from '@/api/articles'
import { usePagination } from '@/composables/usePagination'
import ArticleCard from '@/components/article/ArticleCard.vue'
import Pagination from '@/components/common/Pagination.vue'

const route = useRoute()
const articles = ref<ArticleSummary[]>([])
const loading = ref(false)
const pagination = usePagination(10)

async function load() {
  loading.value = true
  try {
    const res = await articlesApi.list({
      category: route.params.slug as string,
      page: pagination.currentPage.value,
      size: pagination.pageSize.value,
    })
    articles.value = res.items
    pagination.setFromResponse(res)
  } finally {
    loading.value = false
  }
}

watch([() => route.params.slug, () => pagination.currentPage.value], load)
onMounted(load)
</script>

<template>
  <div>
    <header class="mb-8">
      <p class="text-xs text-gray-400 dark:text-gray-600 mb-1">分类</p>
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">{{ route.params.slug }}</h1>
    </header>

    <div v-if="loading" class="text-sm text-gray-400">加载中...</div>
    <div v-else-if="!articles.length" class="py-20 text-center text-sm text-gray-400">该分类下暂无文章</div>
    <div v-else>
      <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
      <Pagination :current-page="pagination.currentPage.value" :total-pages="pagination.totalPages.value" @change="pagination.goToPage" />
    </div>
  </div>
</template>
