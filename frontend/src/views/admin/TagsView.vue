<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Tag } from '@/types'
import { tagsApi } from '@/api/tags'
import ConfirmDialog from '@/components/admin/ConfirmDialog.vue'

const tags = ref<Tag[]>([])
const loading = ref(false)

const showForm = ref(false)
const editingId = ref<number | null>(null)
const formName = ref('')
const formError = ref('')
const saving = ref(false)

const confirmDelete = ref(false)
const deletingId = ref<number | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  try {
    tags.value = await tagsApi.list()
  } finally {
    loading.value = false
  }
}

function startCreate() {
  editingId.value = null
  formName.value = ''
  formError.value = ''
  showForm.value = true
}

function startEdit(tag: Tag) {
  editingId.value = tag.id
  formName.value = tag.name
  formError.value = ''
  showForm.value = true
}

async function save() {
  if (!formName.value.trim()) {
    formError.value = '请输入标签名称'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      await tagsApi.update(editingId.value, formName.value.trim())
    } else {
      await tagsApi.create(formName.value.trim())
    }
    showForm.value = false
    await load()
  } catch (e: any) {
    formError.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function deleteTag() {
  if (!deletingId.value) return
  deleting.value = true
  try {
    await tagsApi.delete(deletingId.value)
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
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">标签管理</h1>
      <button @click="startCreate" class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 transition-opacity">
        新增标签
      </button>
    </div>

    <div v-if="showForm" class="bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg p-5 mb-5">
      <h2 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-4">{{ editingId ? '编辑标签' : '新增标签' }}</h2>
      <div class="flex gap-3 items-start">
        <input v-model="formName" placeholder="标签名称 *" class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#0a0a0a] focus:outline-none" />
        <button @click="save" :disabled="saving" class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 disabled:opacity-50 transition-opacity">
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button @click="showForm = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">取消</button>
      </div>
      <div v-if="formError" class="mt-2 text-xs text-red-500">{{ formError }}</div>
    </div>

    <div class="flex flex-wrap gap-3">
      <div
        v-for="tag in tags"
        :key="tag.id"
        class="flex items-center gap-2 px-3 py-2 bg-white dark:bg-[#111] border border-gray-200 dark:border-gray-800 rounded-lg text-sm"
      >
        <span class="text-gray-900 dark:text-gray-100">#{{ tag.name }}</span>
        <span class="text-xs text-gray-400 dark:text-gray-600">({{ tag.article_count }})</span>
        <button @click="startEdit(tag)" class="text-xs text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">编辑</button>
        <button @click="deletingId = tag.id; confirmDelete = true" class="text-xs text-red-400 hover:text-red-600 transition-colors">×</button>
      </div>
      <div v-if="!tags.length && !loading" class="text-sm text-gray-400">暂无标签</div>
    </div>

    <ConfirmDialog v-if="confirmDelete" title="删除标签" message="删除后该标签将从所有文章中移除。" :loading="deleting" @confirm="deleteTag" @cancel="confirmDelete = false; deletingId = null" />
  </div>
</template>
