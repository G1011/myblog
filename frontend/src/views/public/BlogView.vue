<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { ArticleSummary, Tag, PaginatedResponse } from '@/types'
import { articlesApi } from '@/api/articles'
import { tagsApi } from '@/api/tags'
import { usePagination } from '@/composables/usePagination'
import ArticleCard from '@/components/article/ArticleCard.vue'
import Pagination from '@/components/common/Pagination.vue'

// ── Mock data (shown when backend is unavailable) ──────────────────────────
const MOCK_TECH: ArticleSummary[] = [
  {
    id: 1, slug: 'vue3-composition-api', status: 'published', view_count: 128,
    title: 'Vue 3 Composition API 深度解析',
    summary: '从 Options API 到 Composition API 的思维转变，以及 setup()、ref、reactive、computed 等核心 API 的最佳实践。',
    cover_image: null, published_at: '2026-02-20T00:00:00', created_at: '2026-02-20T00:00:00',
    author: { id: 1, username: 'admin' },
    category: { id: 1, name: 'TechBlog', slug: 'tech' },
    tags: [{ id: 1, name: 'Vue', slug: 'vue' }, { id: 2, name: 'Frontend', slug: 'frontend' }],
  },
  {
    id: 2, slug: 'fastapi-async-sqlalchemy', status: 'published', view_count: 96,
    title: '用 FastAPI + SQLAlchemy 2.0 构建异步 API',
    summary: 'async/await 全链路：从 asyncpg 连接池到 Repository 模式，实现高性能异步数据库访问。',
    cover_image: null, published_at: '2026-02-10T00:00:00', created_at: '2026-02-10T00:00:00',
    author: { id: 1, username: 'admin' },
    category: { id: 1, name: 'TechBlog', slug: 'tech' },
    tags: [{ id: 3, name: 'Python', slug: 'python' }, { id: 4, name: 'FastAPI', slug: 'fastapi' }],
  },
  {
    id: 3, slug: 'docker-compose-dev-workflow', status: 'published', view_count: 74,
    title: 'Docker Compose 本地开发工作流',
    summary: '多服务协作、健康检查、Volume 挂载、网络隔离——用 Docker Compose 搭建与生产一致的本地环境。',
    cover_image: null, published_at: '2026-01-28T00:00:00', created_at: '2026-01-28T00:00:00',
    author: { id: 1, username: 'admin' },
    category: { id: 1, name: 'TechBlog', slug: 'tech' },
    tags: [{ id: 5, name: 'Docker', slug: 'docker' }, { id: 6, name: 'DevOps', slug: 'devops' }],
  },
  {
    id: 4, slug: 'typescript-generics-patterns', status: 'published', view_count: 58,
    title: 'TypeScript 泛型模式实战',
    summary: '条件类型、infer、映射类型……深入理解 TypeScript 类型系统，写出更安全、更可复用的代码。',
    cover_image: null, published_at: '2026-01-15T00:00:00', created_at: '2026-01-15T00:00:00',
    author: { id: 1, username: 'admin' },
    category: { id: 1, name: 'TechBlog', slug: 'tech' },
    tags: [{ id: 7, name: 'TypeScript', slug: 'typescript' }],
  },
]

const MOCK_LIFE: ArticleSummary[] = [
  {
    id: 5, slug: 'morning-routine-productivity', status: 'published', view_count: 210,
    title: '我的晨间routine：如何用1小时开启高效的一天',
    summary: '6点起床、冥想、阅读、运动——四年坚持下来，这套晨间习惯让我的专注力和情绪稳定性提升了不少。',
    cover_image: null, published_at: '2026-02-25T00:00:00', created_at: '2026-02-25T00:00:00',
    author: { id: 1, username: 'admin' },
    category: { id: 2, name: 'LifeBlog', slug: 'life' },
    tags: [{ id: 8, name: '习惯', slug: 'habit' }, { id: 9, name: '效率', slug: 'productivity' }],
  },
  {
    id: 6, slug: 'remote-work-reflections', status: 'published', view_count: 145,
    title: '远程工作两年后的真实感受',
    summary: '不是所有人都适合远程工作。自律、边界感、社交孤独——聊聊那些远程工作的光面与暗面。',
    cover_image: null, published_at: '2026-02-08T00:00:00', created_at: '2026-02-08T00:00:00',
    author: { id: 1, username: 'admin' },
    category: { id: 2, name: 'LifeBlog', slug: 'life' },
    tags: [{ id: 10, name: '远程工作', slug: 'remote' }],
  },
  {
    id: 7, slug: 'reading-habit-2025', status: 'published', view_count: 89,
    title: '2025年我读了哪些书',
    summary: '技术、哲学、传记——年度书单与读书笔记，以及一些改变了我思考方式的段落。',
    cover_image: null, published_at: '2026-01-05T00:00:00', created_at: '2026-01-05T00:00:00',
    author: { id: 1, username: 'admin' },
    category: { id: 2, name: 'LifeBlog', slug: 'life' },
    tags: [{ id: 11, name: '阅读', slug: 'reading' }, { id: 12, name: '书单', slug: 'booklist' }],
  },
]

function getMockByCategory(slug: string): PaginatedResponse<ArticleSummary> {
  const items = slug === 'life' ? MOCK_LIFE : slug === 'tech' ? MOCK_TECH : [...MOCK_TECH, ...MOCK_LIFE]
  return { items, total: items.length, page: 1, size: items.length, pages: 1 }
}
// ──────────────────────────────────────────────────────────────────────────

const route = useRoute()

const articles = ref<ArticleSummary[]>([])
const tags = ref<Tag[]>([])
const loading = ref(false)
const usingMock = ref(false)

const pagination = usePagination(10)
const categorySlug = computed(() => route.query.category as string || '')
const selectedTag = ref<string>('')

const pageTitle = computed(() => {
  if (categorySlug.value === 'tech') return 'TechBlog'
  if (categorySlug.value === 'life') return 'LifeBlog'
  return 'Blog'
})

async function fetchArticles() {
  loading.value = true
  try {
    if (usingMock.value) {
      // Backend already known to be unavailable — skip the request
      const mock = getMockByCategory(categorySlug.value)
      articles.value = mock.items
      pagination.setFromResponse(mock)
      return
    }
    const res = await articlesApi.list({
      page: pagination.currentPage.value,
      size: pagination.pageSize.value,
      category: categorySlug.value || undefined,
      tag: selectedTag.value || undefined,
    })
    articles.value = res.items
    pagination.setFromResponse(res)
    usingMock.value = false
  } catch {
    // Backend not available — fall back to mock data
    const mock = getMockByCategory(categorySlug.value)
    articles.value = mock.items
    pagination.setFromResponse(mock)
    usingMock.value = true
  } finally {
    loading.value = false
  }
}

function selectTag(slug: string) {
  selectedTag.value = selectedTag.value === slug ? '' : slug
  pagination.currentPage.value = 1
}

watch([categorySlug, selectedTag, () => pagination.currentPage.value], fetchArticles)

watch(categorySlug, () => {
  selectedTag.value = ''
  pagination.currentPage.value = 1
})

onMounted(async () => {
  await fetchArticles()
  try {
    tags.value = await tagsApi.list()
  } catch {
    // tags not critical
  }
})
</script>

<template>
  <div>
    <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100 tracking-tight mb-6">
      {{ pageTitle }}
    </h1>

    <!-- Tag filter (only when backend is live) -->
    <div v-if="!usingMock && tags.length" class="flex flex-wrap gap-2 mb-8">
      <button
        v-for="tag in tags"
        :key="tag.id"
        @click="selectTag(tag.slug)"
        :class="[
          'text-xs transition-colors',
          selectedTag === tag.slug
            ? 'text-gray-900 dark:text-gray-100 font-medium'
            : 'text-gray-400 dark:text-gray-600 hover:text-gray-700 dark:hover:text-gray-300',
        ]"
      >
        #{{ tag.name }}
      </button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-1">
      <div v-for="i in 4" :key="i" class="py-5 border-b border-gray-100 dark:border-gray-900 animate-pulse">
        <div class="flex gap-6">
          <div class="w-24 h-4 bg-gray-100 dark:bg-gray-900 rounded shrink-0" />
          <div class="flex-1 space-y-2">
            <div class="h-4 bg-gray-100 dark:bg-gray-900 rounded w-3/4" />
            <div class="h-3 bg-gray-100 dark:bg-gray-900 rounded w-full" />
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!articles.length" class="py-20 text-center text-sm text-gray-400 dark:text-gray-600">
      暂无文章
    </div>

    <div v-else>
      <ArticleCard v-for="article in articles" :key="article.id" :article="article" />
      <Pagination
        :current-page="pagination.currentPage.value"
        :total-pages="pagination.totalPages.value"
        @change="pagination.goToPage"
      />
    </div>
  </div>
</template>
