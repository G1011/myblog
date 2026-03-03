<script setup lang="ts">
import { ref } from 'vue'
import { commentsApi } from '@/api/comments'

const props = defineProps<{
  articleId: number
  parentId?: number
}>()

const emit = defineEmits<{
  (e: 'submitted'): void
  (e: 'cancel'): void
}>()

const name = ref('')
const email = ref('')
const body = ref('')
const submitting = ref(false)
const error = ref('')
const success = ref(false)

async function submit() {
  if (!name.value.trim() || !email.value.trim() || !body.value.trim()) {
    error.value = '请填写所有必填项'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await commentsApi.submit(props.articleId, {
      author_name: name.value.trim(),
      author_email: email.value.trim(),
      body: body.value.trim(),
      parent_id: props.parentId,
    })
    success.value = true
    name.value = ''
    email.value = ''
    body.value = ''
    emit('submitted')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '提交失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="space-y-3">
    <div v-if="success" class="text-sm text-green-600 dark:text-green-400 p-3 bg-green-50 dark:bg-green-900/20 rounded">
      评论已提交，等待管理员审核后显示。
    </div>
    <template v-else>
      <div class="flex gap-3">
        <input
          v-model="name"
          placeholder="名字 *"
          class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600"
        />
        <input
          v-model="email"
          type="email"
          placeholder="邮箱 *（不公开）"
          class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600"
        />
      </div>
      <textarea
        v-model="body"
        rows="4"
        placeholder="写下你的评论..."
        class="w-full px-3 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600 resize-none"
      />
      <div v-if="error" class="text-sm text-red-500">{{ error }}</div>
      <div class="flex gap-2">
        <button
          @click="submit"
          :disabled="submitting"
          class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 disabled:opacity-50 transition-opacity"
        >
          {{ submitting ? '提交中...' : '提交评论' }}
        </button>
        <button
          v-if="parentId"
          @click="emit('cancel')"
          class="px-4 py-2 text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
        >
          取消
        </button>
      </div>
    </template>
  </div>
</template>
