<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const navItems = [
  { label: '概览', to: '/admin', name: 'admin-dashboard', icon: 'M3 4h18v2H3V4zm0 7h18v2H3v-2zm0 7h18v2H3v-2z' },
  { label: '文章', to: '/admin/articles', name: 'admin-articles', icon: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14l-5-5 1.41-1.41L12 14.17l7.59-7.59L21 8l-9 9z' },
  { label: '分类', to: '/admin/categories', name: 'admin-categories', icon: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z' },
  { label: '标签', to: '/admin/tags', name: 'admin-tags', icon: 'M17.63 5.84C17.27 5.33 16.67 5 16 5L5 5.01C3.9 5.01 3 5.9 3 7v10c0 1.1.9 1.99 2 1.99L16 19c.67 0 1.27-.33 1.63-.84L22 12l-4.37-6.16z' },
  { label: '评论', to: '/admin/comments', name: 'admin-comments', icon: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z' },
]
</script>

<template>
  <aside class="w-48 shrink-0 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-[#111] flex flex-col">
    <!-- Brand -->
    <div class="h-14 flex items-center px-5 border-b border-gray-200 dark:border-gray-800">
      <RouterLink to="/" class="text-sm font-semibold text-gray-900 dark:text-gray-100">MyBlog</RouterLink>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-3 space-y-0.5">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :exact-active-class="item.name === 'admin-dashboard' ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100' : ''"
        :active-class="item.name !== 'admin-dashboard' ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100' : ''"
        class="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
      >
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
        </svg>
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- User info -->
    <div class="p-3 border-t border-gray-200 dark:border-gray-800">
      <button
        @click="auth.logout"
        class="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-500 dark:text-gray-500 hover:text-red-500 transition-colors rounded-md"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        退出登录
      </button>
    </div>
  </aside>
</template>
