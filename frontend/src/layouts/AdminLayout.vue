<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'

const authStore = useAuthStore()
onMounted(() => authStore.fetchMe())
</script>

<template>
  <div class="min-h-screen flex bg-gray-50 dark:bg-[#0a0a0a]">
    <AdminSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top bar -->
      <header class="h-14 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-6 bg-white dark:bg-[#111]">
        <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
          <RouterView name="title" />
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500 dark:text-gray-400">{{ authStore.user?.username }}</span>
          <button
            @click="authStore.logout"
            class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          >
            退出
          </button>
        </div>
      </header>
      <!-- Content -->
      <main class="flex-1 p-6 overflow-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>
