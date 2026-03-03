<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

const route = useRoute()
const blogOpen = ref(false)

const blogItems = [
  { label: 'TechBlog', category: 'tech' },
  { label: 'LifeBlog', category: 'life' },
]

function isBlogActive() {
  return route.name === 'blog' || route.name === 'article'
}
</script>

<template>
  <header class="w-full border-b border-gray-100 dark:border-gray-900">
    <div class="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
      <nav class="flex items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
        <RouterLink
          to="/"
          class="hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          :class="{ 'text-gray-900 dark:text-gray-100': route.name === 'about' }"
        >
          About
        </RouterLink>

        <!-- Blog dropdown — 用 padding 而非 margin 桥接鼠标移动区域 -->
        <div
          class="relative"
          @mouseenter="blogOpen = true"
          @mouseleave="blogOpen = false"
        >
          <button
            class="flex items-center gap-1 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
            :class="{ 'text-gray-900 dark:text-gray-100': isBlogActive() }"
          >
            Blog
            <svg
              class="w-3 h-3 transition-transform duration-150"
              :class="{ 'rotate-180': blogOpen }"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path d="M2 4l4 4 4-4" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>

          <!-- pt-1 而非 mt-1，让顶部透明区域仍在父元素 hover 范围内 -->
          <div
            v-show="blogOpen"
            class="absolute top-full left-0 pt-1 z-50"
          >
            <div class="py-1 min-w-[120px] bg-white dark:bg-[#111] border border-gray-100 dark:border-gray-800 rounded-md shadow-sm">
              <RouterLink
                v-for="item in blogItems"
                :key="item.category"
                :to="{ name: 'blog', query: { category: item.category } }"
                class="block px-3 py-1.5 text-xs hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
                :class="
                  route.query.category === item.category && isBlogActive()
                    ? 'text-gray-900 dark:text-gray-100 font-medium'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
                "
                @click="blogOpen = false"
              >
                {{ item.label }}
              </RouterLink>
            </div>
          </div>
        </div>
      </nav>

      <ThemeToggle />
    </div>
  </header>
</template>
