<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Article } from '@/types'
import { articlesApi } from '@/api/articles'
import { useMarkdown } from '@/composables/useMarkdown'
import { formatDate } from '@/utils/date'
import CommentList from '@/components/comment/CommentList.vue'

const route = useRoute()
const article = ref<Article | null>(null)
const loading = ref(false)
const error = ref('')

const contentMd = computed(() => article.value?.content_md ?? '')
const { html } = useMarkdown(contentMd)

async function load(slug: string) {
  loading.value = true
  error.value = ''
  try {
    article.value = await articlesApi.getBySlug(slug)
  } catch (e: any) {
    error.value = e.response?.status === 404 ? '文章不存在' : '加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => route.params.slug as string, load, { immediate: true })
</script>

<template>
  <div>
    <div v-if="loading" class="animate-pulse space-y-4">
      <div class="h-8 bg-gray-100 dark:bg-gray-900 rounded w-3/4" />
      <div class="h-4 bg-gray-100 dark:bg-gray-900 rounded w-1/4" />
    </div>

    <div v-else-if="error" class="py-20 text-center text-sm text-gray-400">{{ error }}</div>

    <article v-else-if="article">
      <!-- Meta -->
      <header class="mb-10">
        <div class="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-600 mb-4">
          <RouterLink v-if="article.category" :to="`/category/${article.category.slug}`" class="hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
            {{ article.category.name }}
          </RouterLink>
          <span v-if="article.category">·</span>
          <time>{{ formatDate(article.published_at || article.created_at) }}</time>
          <span>·</span>
          <span>{{ article.view_count }} 阅读</span>
        </div>

        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 leading-tight mb-3">
          {{ article.title }}
        </h1>

        <p v-if="article.summary" class="text-gray-500 dark:text-gray-400 leading-relaxed">
          {{ article.summary }}
        </p>

        <!-- Tags -->
        <div v-if="article.tags.length" class="flex flex-wrap gap-2 mt-4">
          <RouterLink
            v-for="tag in article.tags"
            :key="tag.id"
            :to="`/tag/${tag.slug}`"
            class="text-xs text-gray-400 dark:text-gray-600 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            #{{ tag.name }}
          </RouterLink>
        </div>
      </header>

      <!-- Cover image -->
      <img
        v-if="article.cover_image"
        :src="article.cover_image"
        :alt="article.title"
        class="w-full rounded-lg mb-10 object-cover max-h-80"
      />

      <!-- Divider -->
      <hr class="border-gray-100 dark:border-gray-900 mb-10" />

      <!-- Content -->
      <div
        class="prose dark:prose-invert max-w-none prose-headings:font-semibold prose-a:text-gray-900 dark:prose-a:text-gray-100 prose-code:text-sm"
        v-html="html"
      />

      <!-- Comments -->
      <CommentList :article-id="article.id" />
    </article>
  </div>
</template>

