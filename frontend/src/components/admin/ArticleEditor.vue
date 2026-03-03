<script setup lang="ts">
import { computed } from 'vue'
import { useMarkdown } from '@/composables/useMarkdown'

const model = defineModel<string>({ default: '' })

const { html } = useMarkdown(model)
</script>

<template>
  <div class="grid grid-cols-2 gap-0 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden h-[600px]">
    <!-- Editor pane -->
    <div class="flex flex-col border-r border-gray-200 dark:border-gray-800">
      <div class="px-3 py-2 text-xs font-medium text-gray-400 dark:text-gray-600 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#111]">
        Markdown 编辑
      </div>
      <textarea
        v-model="model"
        class="flex-1 p-4 text-sm font-mono bg-white dark:bg-[#0a0a0a] text-gray-900 dark:text-gray-100 resize-none focus:outline-none"
        placeholder="开始写作..."
        spellcheck="false"
      />
    </div>

    <!-- Preview pane -->
    <div class="flex flex-col">
      <div class="px-3 py-2 text-xs font-medium text-gray-400 dark:text-gray-600 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#111]">
        预览
      </div>
      <div
        class="flex-1 p-4 overflow-auto prose prose-sm dark:prose-invert max-w-none"
        v-html="html"
      />
    </div>
  </div>
</template>
