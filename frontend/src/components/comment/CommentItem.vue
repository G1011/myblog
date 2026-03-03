<script setup lang="ts">
import { ref } from 'vue'
import type { Comment } from '@/types'
import { formatDate } from '@/utils/date'
import CommentForm from './CommentForm.vue'

const props = defineProps<{
  comment: Comment
  articleId: number
}>()

const emit = defineEmits<{ (e: 'refresh'): void }>()

const showReplyForm = ref(false)
</script>

<template>
  <div class="space-y-4">
    <div class="flex gap-3">
      <!-- Avatar initial -->
      <div class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center text-xs font-semibold text-gray-600 dark:text-gray-300 shrink-0">
        {{ comment.author_name.charAt(0).toUpperCase() }}
      </div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ comment.author_name }}</span>
          <time class="text-xs text-gray-400 dark:text-gray-600">{{ formatDate(comment.created_at) }}</time>
        </div>
        <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">{{ comment.body }}</p>
        <button
          @click="showReplyForm = !showReplyForm"
          class="mt-1.5 text-xs text-gray-400 dark:text-gray-600 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
        >
          回复
        </button>

        <div v-if="showReplyForm" class="mt-3">
          <CommentForm
            :article-id="articleId"
            :parent-id="comment.id"
            @submitted="showReplyForm = false; emit('refresh')"
            @cancel="showReplyForm = false"
          />
        </div>

        <!-- Nested replies -->
        <div v-if="comment.replies?.length" class="mt-4 pl-4 border-l-2 border-gray-100 dark:border-gray-900 space-y-4">
          <CommentItem
            v-for="reply in comment.replies"
            :key="reply.id"
            :comment="reply"
            :article-id="articleId"
            @refresh="emit('refresh')"
          />
        </div>
      </div>
    </div>
  </div>
</template>
