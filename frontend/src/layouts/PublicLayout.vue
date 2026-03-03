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
  </div>
</template>
