<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { Comment } from '@/types'
import { commentsApi } from '@/api/comments'
import { usePagination } from '@/composables/usePagination'
import { formatDateTime } from '@/utils/date'
import ConfirmDialog from '@/components/admin/ConfirmDialog.vue'
import Pagination from '@/components/common/Pagination.vue'

const comments = ref<Comment[]>([])
const loading = ref(false)
const statusFilter = ref<string>('')
const pagination = usePagination(20)

const confirmDelete = ref(false)
const deletingId = ref<number | null>(null)
const deleting = ref(false)
const approving = ref<number | null>(null)

async function load() {
  loading.value = true
  try {
    const res = await commentsApi.adminList({
      status: statusFilter.value || undefined,
      page: pagination.currentPage.value,
      size: pagination.pageSize.value,
    })
    comments.value = res.items
    pagination.setFromResponse(res)
  } finally {
    loading.value = false
  }
}

async function approve(id: number) {
  approving.value = id
  try {
    await commentsApi.approve(id)
    await load()
  } finally {
    approving.value = null
  }
}

async function deleteComment() {
  if (!deletingId.value) return
  deleting.value = true
  try {
    await commentsApi.delete(deletingId.value)
    confirmDelete.value = false
    await load()
  } finally {
    deleting.value = false
    deletingId.value = null
  }
}

watch(statusFilter, () => {
  pagination.currentPage.value = 1
  load()
})

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">评论管理</h1>
      <div class="flex gap-2">
        <button
          v-for="f in [{ label: '全部', value: '' }, { label: '待审', value: 'pending' }, { label: '已审', value: 'approved' }]"
          :key="f.value"
          @click="statusFilter = f.value"
          :class="[
            'px-3 py-1.5 text-xs rounded transition-colors',
            statusFilter === f.value
              ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
              : 'border border-gray-200 dark:border-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
          ]"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <div class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">加载中...</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-900 text-xs text-gray-400 dark:text-gray-600">
            <th class="text-left px-4 py-3 font-medium">评论者</th>
            <th class="text-left px-4 py-3 font-medium">内容</th>
            <th class="text-left px-4 py-3 font-medium">状态</th>
            <th class="text-left px-4 py-3 font-medium">时间</th>
            <th class="text-right px-4 py-3 font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-900">
          <tr v-if="!comments.length">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">暂无评论</td>
          </tr>
          <tr v-for="comment in comments" :key="comment.id" class="hover:bg-gray-50 dark:hover:bg-gray-900/50">
            <td class="px-4 py-3">
              <div class="font-medium text-gray-900 dark:text-gray-100">{{ comment.author_name }}</div>
            </td>
            <td class="px-4 py-3 text-gray-600 dark:text-gray-400 max-w-xs">
              <p class="line-clamp-2">{{ comment.body }}</p>
            </td>
            <td class="px-4 py-3">
              <span :class="[
                'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                comment.is_approved
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  : 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
              ]">
                {{ comment.is_approved ? '已审核' : '待审核' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-400 text-xs tabular-nums">{{ formatDateTime(comment.created_at) }}</td>
            <td class="px-4 py-3">
              <div class="flex gap-3 justify-end">
                <button
                  v-if="!comment.is_approved"
                  @click="approve(comment.id)"
                  :disabled="approving === comment.id"
                  class="text-xs text-green-600 hover:text-green-700 transition-colors disabled:opacity-50"
                >
                  {{ approving === comment.id ? '审核中...' : '批准' }}
                </button>
                <button
                  @click="deletingId = comment.id; confirmDelete = true"
                  class="text-xs text-red-400 hover:text-red-600 transition-colors"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Pagination :current-page="pagination.currentPage.value" :total-pages="pagination.totalPages.value" @change="p => { pagination.goToPage(p); load() }" />

    <ConfirmDialog v-if="confirmDelete" title="删除评论" message="删除后无法恢复。" :loading="deleting" @confirm="deleteComment" @cancel="confirmDelete = false; deletingId = null" />
  </div>
</template>
