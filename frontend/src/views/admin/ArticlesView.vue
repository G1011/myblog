<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ArticleSummary } from '@/types'
import { articlesApi } from '@/api/articles'
import { usePagination } from '@/composables/usePagination'
import { formatDateTime } from '@/utils/date'
import ConfirmDialog from '@/components/admin/ConfirmDialog.vue'
import Pagination from '@/components/common/Pagination.vue'

const articles = ref<ArticleSummary[]>([])
const loading = ref(false)
const pagination = usePagination(20)

const confirmDelete = ref(false)
const deletingId = ref<number | null>(null)
const deleting = ref(false)

const uploadInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadError = ref('')

async function load() {
  loading.value = true
  try {
    const res = await articlesApi.adminList(pagination.currentPage.value, pagination.pageSize.value)
    articles.value = res.items
    pagination.setFromResponse(res)
  } finally {
    loading.value = false
  }
}

async function toggleStatus(article: ArticleSummary) {
  try {
    if (article.status === 'published') {
      await articlesApi.unpublish(article.id)
    } else {
      await articlesApi.publish(article.id)
    }
    await load()
  } catch (e) {
    console.error(e)
  }
}

async function deleteArticle() {
  if (!deletingId.value) return
  deleting.value = true
  try {
    await articlesApi.delete(deletingId.value)
    confirmDelete.value = false
    await load()
  } finally {
    deleting.value = false
    deletingId.value = null
  }
}

function triggerUpload() {
  uploadError.value = ''
  uploadInput.value?.click()
}

async function handleUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  uploadError.value = ''
  try {
    await articlesApi.uploadMd(file)
    await load()
  } catch (e: any) {
    uploadError.value = e.response?.data?.detail || '上传失败'
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function downloadMd(article: ArticleSummary) {
  try {
    await articlesApi.downloadMd(article.id, article.slug)
  } catch (e) {
    console.error(e)
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">文章管理</h1>
      <div class="flex items-center gap-3">
        <span v-if="uploadError" class="text-xs text-red-500">{{ uploadError }}</span>
        <input
          ref="uploadInput"
          type="file"
          accept=".md"
          class="hidden"
          @change="handleUpload"
        />
        <button
          @click="triggerUpload"
          :disabled="uploading"
          class="px-4 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 transition-colors text-gray-600 dark:text-gray-400"
        >
          {{ uploading ? '上传中...' : '上传 .md' }}
        </button>
        <RouterLink to="/admin/articles/new" class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 transition-opacity">
          写新文章
        </RouterLink>
      </div>
    </div>

    <div class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">加载中...</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-900 text-xs text-gray-400 dark:text-gray-600">
            <th class="text-left px-4 py-3 font-medium">标题</th>
            <th class="text-left px-4 py-3 font-medium">状态</th>
            <th class="text-left px-4 py-3 font-medium">分类</th>
            <th class="text-left px-4 py-3 font-medium">阅读</th>
            <th class="text-left px-4 py-3 font-medium">创建时间</th>
            <th class="text-right px-4 py-3 font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-900">
          <tr v-if="!articles.length">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400">暂无文章</td>
          </tr>
          <tr v-for="article in articles" :key="article.id" class="hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors">
            <td class="px-4 py-3">
              <span class="font-medium text-gray-900 dark:text-gray-100 line-clamp-1">{{ article.title }}</span>
            </td>
            <td class="px-4 py-3">
              <span :class="[
                'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                article.status === 'published'
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400',
              ]">
                {{ article.status === 'published' ? '已发布' : '草稿' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 dark:text-gray-500">{{ article.category?.name || '-' }}</td>
            <td class="px-4 py-3 text-gray-500 dark:text-gray-500 tabular-nums">{{ article.view_count }}</td>
            <td class="px-4 py-3 text-gray-400 dark:text-gray-600 tabular-nums">{{ formatDateTime(article.created_at) }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-3 justify-end">
                <button @click="toggleStatus(article)" class="text-xs text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  {{ article.status === 'published' ? '撤回' : '发布' }}
                </button>
                <RouterLink :to="`/admin/articles/${article.id}/edit`" class="text-xs text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  编辑
                </RouterLink>
                <button @click="downloadMd(article)" class="text-xs text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  下载
                </button>
                <button
                  @click="deletingId = article.id; confirmDelete = true"
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

    <ConfirmDialog
      v-if="confirmDelete"
      title="删除文章"
      message="删除后无法恢复，文章关联的评论也将一并删除。"
      confirm-text="确认删除"
      :loading="deleting"
      @confirm="deleteArticle"
      @cancel="confirmDelete = false; deletingId = null"
    />
  </div>
</template>
