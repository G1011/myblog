<script setup lang="ts">
import type { ArticleSummary } from '@/types'
import { formatDate } from '@/utils/date'

defineProps<{ article: ArticleSummary }>()
</script>

<template>
  <article class="group">
    <RouterLink :to="`/blog/${article.slug}`" class="flex gap-6 items-start py-5 border-b border-gray-100 dark:border-gray-900 hover:border-gray-300 dark:hover:border-gray-700 transition-colors">
      <!-- Date column -->
      <time class="text-sm text-gray-400 dark:text-gray-600 tabular-nums shrink-0 pt-0.5 w-24 text-right">
        {{ formatDate(article.published_at || article.created_at) }}
      </time>
      <!-- Content -->
      <div class="flex-1 min-w-0">
        <h2 class="text-sm font-semibold text-gray-900 dark:text-gray-100 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors leading-snug">
          {{ article.title }}
        </h2>
        <p v-if="article.summary" class="mt-1 text-sm text-gray-500 dark:text-gray-500 leading-relaxed line-clamp-2">
          {{ article.summary }}
        </p>
        <!-- Tags -->
        <div v-if="article.tags.length" class="mt-2 flex flex-wrap gap-1.5">
          <RouterLink
            v-for="tag in article.tags"
            :key="tag.id"
            :to="`/tag/${tag.slug}`"
            @click.stop
            class="text-xs text-gray-400 dark:text-gray-600 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            #{{ tag.name }}
          </RouterLink>
        </div>
      </div>
    </RouterLink>
  </article>
</template>
