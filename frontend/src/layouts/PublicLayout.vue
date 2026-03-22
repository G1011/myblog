<script setup lang="ts">
import TheHeader from '@/components/common/TheHeader.vue'
import TheFooter from '@/components/common/TheFooter.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-white dark:bg-[#0a0a0a]">
    <TheHeader />
    <main class="flex-1 w-full max-w-2xl mx-auto px-4 py-10">
      <RouterView />
    </main>
    <TheFooter />
    <!-- Admin entry (fixed bottom-right) -->
    <a
      href="/admin/login"
      class="fixed bottom-5 right-5 z-50 w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-700 dark:hover:text-gray-300 transition-colors shadow-sm"
      title="Admin"
    >
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="8" r="4" />
        <path d="M4 20c0-4 3.582-7 8-7s8 3 8 7" />
      </svg>
    </a>
  </div>
</template>
