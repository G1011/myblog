<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Category } from '@/types'
import { categoriesApi } from '@/api/categories'
import { formatDateTime } from '@/utils/date'
import ConfirmDialog from '@/components/admin/ConfirmDialog.vue'

const categories = ref<Category[]>([])
const loading = ref(false)

const showForm = ref(false)
const editingId = ref<number | null>(null)
const formName = ref('')
const formDesc = ref('')
const formError = ref('')
const saving = ref(false)

const confirmDelete = ref(false)
const deletingId = ref<number | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  try {
    categories.value = await categoriesApi.list()
  } finally {
    loading.value = false
  }
}

function startCreate() {
  editingId.value = null
  formName.value = ''
  formDesc.value = ''
  formError.value = ''
  showForm.value = true
}

function startEdit(cat: Category) {
  editingId.value = cat.id
  formName.value = cat.name
  formDesc.value = cat.description || ''
  formError.value = ''
  showForm.value = true
}

async function save() {
  if (!formName.value.trim()) {
    formError.value = '请输入分类名称'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      await categoriesApi.update(editingId.value, { name: formName.value.trim(), description: formDesc.value.trim() || undefined })
    } else {
      await categoriesApi.create(formName.value.trim(), formDesc.value.trim() || undefined)
    }
    showForm.value = false
    await load()
  } catch (e: any) {
    formError.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function deleteCategory() {
  if (!deletingId.value) return
  deleting.value = true
  try {
    await categoriesApi.delete(deletingId.value)
    confirmDelete.value = false
    await load()
  } finally {
    deleting.value = false
    deletingId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">分类管理</h1>
      <button @click="startCreate" class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 transition-opacity">
        新增分类
      </button>
    </div>

    <!-- Inline form -->
    <div v-if="showForm" class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg p-5 mb-5">
      <h2 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-4">{{ editingId ? '编辑分类' : '新增分类' }}</h2>
      <div class="space-y-3">
        <input v-model="formName" placeholder="分类名称 *" class="w-full px-3 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#0a0a0a] focus:outline-none" />
        <input v-model="formDesc" placeholder="描述（可选）" class="w-full px-3 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#0a0a0a] focus:outline-none" />
        <div v-if="formError" class="text-xs text-red-500">{{ formError }}</div>
        <div class="flex gap-2">
          <button @click="save" :disabled="saving" class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 disabled:opacity-50 transition-opacity">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button @click="showForm = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">取消</button>
        </div>
      </div>
    </div>

    <div class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">加载中...</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-900 text-xs text-gray-400 dark:text-gray-600">
            <th class="text-left px-4 py-3 font-medium">名称</th>
            <th class="text-left px-4 py-3 font-medium">Slug</th>
            <th class="text-left px-4 py-3 font-medium">文章数</th>
            <th class="text-left px-4 py-3 font-medium">创建时间</th>
            <th class="text-right px-4 py-3 font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-900">
          <tr v-if="!categories.length">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">暂无分类</td>
          </tr>
          <tr v-for="cat in categories" :key="cat.id" class="hover:bg-gray-50 dark:hover:bg-gray-900/50">
            <td class="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">{{ cat.name }}</td>
            <td class="px-4 py-3 text-gray-400 font-mono text-xs">{{ cat.slug }}</td>
            <td class="px-4 py-3 text-gray-500">{{ cat.article_count }}</td>
            <td class="px-4 py-3 text-gray-400 text-xs tabular-nums">{{ formatDateTime(cat.created_at) }}</td>
            <td class="px-4 py-3">
              <div class="flex gap-3 justify-end">
                <button @click="startEdit(cat)" class="text-xs text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">编辑</button>
                <button @click="deletingId = cat.id; confirmDelete = true" class="text-xs text-red-400 hover:text-red-600 transition-colors">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmDialog v-if="confirmDelete" title="删除分类" message="删除后该分类下的文章将失去分类关联。" :loading="deleting" @confirm="deleteCategory" @cancel="confirmDelete = false; deletingId = null" />
  </div>
</template>
