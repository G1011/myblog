<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Category, Tag } from '@/types'
import { articlesApi } from '@/api/articles'
import { categoriesApi } from '@/api/categories'
import { tagsApi } from '@/api/tags'
import ArticleEditor from '@/components/admin/ArticleEditor.vue'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const articleId = computed(() => Number(route.params.id))

const title = ref('')
const summary = ref('')
const contentMd = ref('')
const coverImage = ref('')
const status = ref('draft')
const selectedCategoryId = ref<number | null>(null)
const selectedTagIds = ref<number[]>([])

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  try {
    const [cats, tgs] = await Promise.all([categoriesApi.list(), tagsApi.list()])
    categories.value = cats
    tags.value = tgs

    if (isEdit.value) {
      const article = await articlesApi.adminGet(articleId.value)
      title.value = article.title
      summary.value = article.summary || ''
      contentMd.value = article.content_md
      coverImage.value = article.cover_image || ''
      status.value = article.status
      selectedCategoryId.value = article.category?.id || null
      selectedTagIds.value = article.tags.map(t => t.id)
    }
  } finally {
    loading.value = false
  }
}

function toggleTag(id: number) {
  const idx = selectedTagIds.value.indexOf(id)
  if (idx >= 0) selectedTagIds.value.splice(idx, 1)
  else selectedTagIds.value.push(id)
}

async function downloadMd() {
  if (!isEdit.value) return
  try {
    const article = await articlesApi.adminGet(articleId.value)
    await articlesApi.downloadMd(articleId.value, article.slug)
  } catch (e) {
    console.error(e)
  }
}

async function save() {
  if (!title.value.trim()) {
    error.value = '请填写文章标题'
    return
  }
  if (!contentMd.value.trim()) {
    error.value = '请填写文章内容'
    return
  }
  saving.value = true
  error.value = ''
  try {
    const payload = {
      title: title.value.trim(),
      summary: summary.value.trim() || undefined,
      content_md: contentMd.value,
      cover_image: coverImage.value.trim() || undefined,
      status: status.value,
      category_id: selectedCategoryId.value || null,
      tag_ids: selectedTagIds.value,
    }
    if (isEdit.value) {
      await articlesApi.update(articleId.value, payload)
    } else {
      await articlesApi.create(payload)
    }
    router.push('/admin/articles')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
        {{ isEdit ? '编辑文章' : '写新文章' }}
      </h1>
      <div class="flex gap-3">
        <RouterLink to="/admin/articles" class="px-4 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-600 dark:text-gray-400">
          取消
        </RouterLink>
        <button
          v-if="isEdit"
          @click="downloadMd"
          class="px-4 py-2 text-sm border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-600 dark:text-gray-400"
        >
          下载 .md
        </button>
        <button
          @click="save"
          :disabled="saving"
          class="px-4 py-2 text-sm bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 disabled:opacity-50 transition-opacity"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-sm text-gray-400">加载中...</div>
    <div v-else class="space-y-5">
      <!-- Title -->
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">标题 *</label>
        <input
          v-model="title"
          placeholder="文章标题"
          class="w-full px-3 py-2.5 text-base border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600 font-medium"
        />
      </div>

      <!-- Summary -->
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">摘要</label>
        <textarea
          v-model="summary"
          rows="2"
          placeholder="文章摘要（可选，留空则自动截取正文）"
          class="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600 resize-none"
        />
      </div>

      <!-- Metadata row -->
      <div class="grid grid-cols-3 gap-4">
        <!-- Status -->
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">状态</label>
          <select
            v-model="status"
            class="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none"
          >
            <option value="draft">草稿</option>
            <option value="published">已发布</option>
          </select>
        </div>

        <!-- Category -->
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">分类</label>
          <select
            v-model="selectedCategoryId"
            class="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none"
          >
            <option :value="null">无分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>

        <!-- Cover image -->
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">封面图 URL</label>
          <input
            v-model="coverImage"
            placeholder="https://..."
            class="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600"
          />
        </div>
      </div>

      <!-- Tags -->
      <div v-if="tags.length">
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">标签</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in tags"
            :key="tag.id"
            @click="toggleTag(tag.id)"
            :class="[
              'text-xs px-2.5 py-1 rounded-full border transition-colors',
              selectedTagIds.includes(tag.id)
                ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 border-transparent'
                : 'border-gray-200 dark:border-gray-800 text-gray-500 dark:text-gray-500 hover:border-gray-400',
            ]"
          >
            #{{ tag.name }}
          </button>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="text-sm text-red-500 py-1">{{ error }}</div>

      <!-- Markdown editor -->
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">内容 *</label>
        <ArticleEditor v-model="contentMd" />
      </div>
    </div>
  </div>
</template>
