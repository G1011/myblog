<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Comment } from '@/types'
import { commentsApi } from '@/api/comments'
import CommentItem from './CommentItem.vue'
import CommentForm from './CommentForm.vue'

const props = defineProps<{ articleId: number }>()

const comments = ref<Comment[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    comments.value = await commentsApi.list(props.articleId)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="mt-16">
    <h2 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-8">
      评论 <span class="text-gray-400 dark:text-gray-600 font-normal">{{ comments.length }}</span>
    </h2>

    <!-- Comment list -->
    <div v-if="loading" class="text-sm text-gray-400">加载中...</div>
    <div v-else-if="!comments.length" class="text-sm text-gray-400 dark:text-gray-600 mb-8">
      还没有评论，来第一个评论吧！
    </div>
    <div v-else class="space-y-6 mb-10">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :article-id="articleId"
        @refresh="load"
      />
    </div>

    <!-- Submit form -->
    <div class="border-t border-gray-100 dark:border-gray-900 pt-8">
      <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-4">发表评论</h3>
      <CommentForm :article-id="articleId" @submitted="load" />
    </div>
  </section>
</template>
