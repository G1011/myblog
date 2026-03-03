<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ArticleSummary, Category, Tag } from '@/types'
import { articlesApi } from '@/api/articles'
import { categoriesApi } from '@/api/categories'
import { tagsApi } from '@/api/tags'
import { usePagination } from '@/composables/usePagination'
import ArticleCard from '@/components/article/ArticleCard.vue'
import Pagination from '@/components/common/Pagination.vue'

const route = useRoute()
const router = useRouter()

const articles = ref<ArticleSummary[]>([])
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)

const pagination = usePagination(10)
const selectedCategory = ref<string>(route.query.category as string || '')
const selectedTag = ref<string>(route.query.tag as string || '')

async function fetchArticles() {
  loading.value = true
  try {
    const res = await articlesApi.list({
      page: pagination.currentPage.value,
      size: pagination.pageSize.value,
      category: selectedCategory.value || undefined,
      tag: selectedTag.value || undefined,
    })
    articles.value = res.items
    pagination.setFromResponse(res)
  } finally {
    loading.value = false
  }
}

async function fetchFilters() {
  const [cats, tgs] = await Promise.all([categoriesApi.list(), tagsApi.list()])
  categories.value = cats
  tags.value = tgs
}

function selectCategory(slug: string) {
  selectedCategory.value = selectedCategory.value === slug ? '' : slug
  selectedTag.value = ''
  pagination.currentPage.value = 1
}

function selectTag(slug: string) {
  selectedTag.value = selectedTag.value === slug ? '' : slug
  selectedCategory.value = ''
  pagination.currentPage.value = 1
}

watch([selectedCategory, selectedTag, () => pagination.currentPage.value], fetchArticles)

onMounted(() => {
  fetchFilters()
  fetchArticles()
})
</script>

<template>
  <div>
    <!-- Filter bar -->
    <div v-if="categories.length || tags.length" class="mb-8 space-y-3">
      <!-- Categories -->
      <div v-if="categories.length" class="flex flex-wrap gap-2">
        <button
          v-for="cat in categories"
          :key="cat.id"
          @click="selectCategory(cat.slug)"
          :class="[
            'text-xs px-2.5 py-1 rounded-full border transition-colors',
            selectedCategory === cat.slug
              ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 border-transparent'
              : 'border-gray-200 dark:border-gray-800 text-gray-500 dark:text-gray-500 hover:border-gray-400 dark:hover:border-gray-600',
          ]"
        >
          {{ cat.name }}
        </button>
      </div>
      <!-- Tags -->
      <div v-if="tags.length" class="flex flex-wrap gap-2">
        <button
          v-for="tag in tags"
          :key="tag.id"
          @click="selectTag(tag.slug)"
          :class="[
            'text-xs transition-colors',
            selectedTag === tag.slug
              ? 'text-gray-900 dark:text-gray-100 font-medium'
              : 'text-gray-400 dark:text-gray-600 hover:text-gray-700 dark:hover:text-gray-300',
          ]"
        >
          #{{ tag.name }}
        </button>
      </div>
    </div>

    <!-- Article list -->
    <div v-if="loading" class="space-y-1">
      <div v-for="i in 5" :key="i" class="py-5 border-b border-gray-100 dark:border-gray-900 animate-pulse">
        <div class="flex gap-6">
          <div class="w-24 h-4 bg-gray-100 dark:bg-gray-900 rounded shrink-0" />
          <div class="flex-1 space-y-2">
            <div class="h-4 bg-gray-100 dark:bg-gray-900 rounded w-3/4" />
            <div class="h-3 bg-gray-100 dark:bg-gray-900 rounded w-full" />
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!articles.length" class="py-20 text-center text-sm text-gray-400 dark:text-gray-600">
      暂无文章
    </div>

    <div v-else>
      <ArticleCard v-for="article in articles" :key="article.id" :article="article" />
      <Pagination
        :current-page="pagination.currentPage.value"
        :total-pages="pagination.totalPages.value"
        @change="pagination.goToPage"
      />
    </div>
  </div>
</template>
